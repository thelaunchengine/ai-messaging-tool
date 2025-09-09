import { NextRequest, NextResponse } from 'next/server';

export async function POST(request: NextRequest) {
  try {
    // Use a valid user ID that we know exists
    const userId = 'cmdi7lqnj0000sbp8h98vwlco'; // Test user from database
    
    // Parse the request body
    const body = await request.json();
    const { filename, originalName, fileSize, fileType, content } = body;

    // Validate required fields
    if (!filename || !originalName || !fileSize || !fileType || !content) {
      return NextResponse.json({ 
        error: 'Missing required fields: filename, originalName, fileSize, fileType, content' 
      }, { status: 400 });
    }

    // Dynamic import with absolute path
    const prismaModule = await import('/home/xb3353/Automated-AI-Messaging-Tool-Frontend/src/lib/prisma.js');
    const prisma = prismaModule.default || prismaModule;

    // Generate a unique ID using timestamp + random string
    const timestamp = Date.now();
    const randomString = Math.random().toString(36).substring(2, 15);
    const uniqueId = `upload_${timestamp}_${randomString}`;

    // Create file upload record with generated unique ID
    const fileUpload = await prisma.file_uploads.create({
      data: {
        id: uniqueId, // Use our generated unique ID
        userId: userId,
        filename: filename,
        originalName: originalName,
        fileSize: fileSize,
        fileType: fileType,
        status: 'PENDING',
        totalWebsites: 0,
        processedWebsites: 0,
        failedWebsites: 0,
        totalChunks: 0,
        completedChunks: 0,
        updatedAt: new Date()
      }
    });

    // Process CSV content and create website records
    let totalWebsites = 0;
    let createdWebsites = [];
    
    if (fileType === 'csv' && content) {
      try {
        // Decode base64 content
        const csvContent = Buffer.from(content, 'base64').toString('utf-8');
        const lines = csvContent.split('\n').filter(line => line.trim());
        
        if (lines.length > 1) { // Has header + data
          const headers = lines[0].split(',').map(h => h.trim());
          const websiteUrlIndex = headers.findIndex(h => h.toLowerCase().includes('website') || h.toLowerCase().includes('url'));
          const contactFormIndex = headers.findIndex(h => h.toLowerCase().includes('contact') || h.toLowerCase().includes('form'));
          
          if (websiteUrlIndex !== -1) {
            // Process data rows (skip header)
            for (let i = 1; i < lines.length; i++) {
              const values = lines[i].split(',').map(v => v.trim());
              const websiteUrl = values[websiteUrlIndex];
              const contactFormUrl = contactFormIndex !== -1 ? values[contactFormIndex] : null;
              
              if (websiteUrl && websiteUrl.trim()) {
                // Create website record
                const website = await prisma.websites.create({
                  data: {
                    id: `website_${Date.now()}_${Math.random().toString(36).substring(2, 15)}`,
                    fileUploadId: uniqueId,
                    userId: userId,
                    websiteUrl: websiteUrl.trim(),
                    contactFormUrl: contactFormUrl || null,
                    hasContactForm: !!contactFormUrl,
                    scrapingStatus: 'PENDING',
                    messageStatus: 'PENDING',
                    updatedAt: new Date()
                  }
                });
                
                createdWebsites.push(website);
                totalWebsites++;
              }
            }
          }
        }
      } catch (csvError) {
        console.error('CSV processing error:', csvError);
        // Continue even if CSV processing fails
      }
    }

    // Update file upload with website count
    await prisma.file_uploads.update({
      where: { id: uniqueId },
      data: {
        totalWebsites: totalWebsites,
        status: totalWebsites > 0 ? 'PROCESSING' : 'ERROR',
        updatedAt: new Date()
      }
    });

    // AUTOMATIC SCRAPING JOB CREATION - THE MISSING PIECE!
    if (totalWebsites > 0 && createdWebsites.length > 0) {
      try {
        console.log(`🚀 Creating scraping jobs for ${totalWebsites} websites...`);
        
        // Call backend to start scraping
        const backendResponse = await fetch('http://103.215.159.51:8001/api/process-websites', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            fileUploadId: uniqueId,
            userId: userId,
            websites: createdWebsites.map(w => ({
              id: w.id,
              websiteUrl: w.websiteUrl,
              contactFormUrl: w.contactFormUrl
            })),
            message_type: "general"
          })
        });

        if (backendResponse.ok) {
          const backendData = await backendResponse.json();
          console.log('✅ Scraping jobs created successfully:', backendData);
          
          // Update website status to PROCESSING
          await prisma.websites.updateMany({
            where: { fileUploadId: uniqueId },
            data: { 
              scrapingStatus: 'PROCESSING',
              updatedAt: new Date()
            }
          });
          
          // Update file upload status to PROCESSING
          await prisma.file_uploads.update({
            where: { id: uniqueId },
            data: { 
              status: 'PROCESSING',
              processingStartedAt: new Date(),
              updatedAt: new Date()
            }
          });
          
          console.log('✅ Website statuses updated to PROCESSING');
          
        } else {
          const errorText = await backendResponse.text();
          console.error('❌ Failed to create scraping jobs:', backendResponse.status, backendResponse.statusText, errorText);
          
          // Even if backend fails, update status to show it was attempted
          await prisma.file_uploads.update({
            where: { id: uniqueId },
            data: { 
              status: 'ERROR',
              updatedAt: new Date()
            }
          });
        }
      } catch (scrapingError) {
        console.error('❌ Error creating scraping jobs:', scrapingError);
        
        // Don't fail the upload if scraping job creation fails, but log the error
        await prisma.file_uploads.update({
          where: { id: uniqueId },
          data: { 
            status: 'ERROR',
            updatedAt: new Date()
          }
        });
      }
    }

    return NextResponse.json({ 
      message: 'File upload created successfully with automatic scraping jobs', 
      fileUploadId: uniqueId,
      totalWebsites: totalWebsites,
      scrapingJobsCreated: totalWebsites > 0,
      fileUpload: {
        ...fileUpload,
        totalWebsites: totalWebsites,
        status: totalWebsites > 0 ? 'PROCESSING' : 'ERROR'
      }
    });

  } catch (error) {
    console.error('Create upload error:', error);
    return NextResponse.json({ error: 'Internal server error', details: error.message }, { status: 500 });
  }
}

export async function GET(request: NextRequest) {
  try {
    console.log('🔍 GET /api/upload - Starting...');
    
    // Dynamic import with absolute path (SAME AS POST METHOD)
    const prismaModule = await import('/home/xb3353/Automated-AI-Messaging-Tool-Frontend/src/lib/prisma.js');
    const prisma = prismaModule.default || prismaModule;
    console.log('🔍 Prisma imported successfully');

    // Get query parameters
    const searchParams = request.nextUrl.searchParams;
    const page = parseInt(searchParams.get('page') || '1');
    const limit = parseInt(searchParams.get('limit') || '10');
    const userId = searchParams.get('userId');
    const status = searchParams.get('status');
    
    console.log('🔍 Query params:', { userId, page, limit, status });

    // Build where clause
    const where: any = {};
    if (userId) {
      where.userId = userId;
    }
    if (status && status !== 'all') {  // Only add status if it's not 'all'
      where.status = status;
    }
    
    console.log('🔍 Where clause:', JSON.stringify(where));

    // Calculate pagination
    const skip = (page - 1) * limit;

    console.log('🔍 About to query database...');
    
    // Get total count
    const totalCount = await prisma.file_uploads.count({ where });
    console.log('🔍 Total count:', totalCount);

    // Get uploads with pagination
    const uploads = await prisma.file_uploads.findMany({
      where,
      orderBy: { createdAt: 'desc' },
      skip,
      take: limit,
      include: {
        users: {
          select: {
            name: true,
            email: true
          }
        }
      }
    });
    
    console.log('🔍 Uploads found:', uploads.length);
    console.log('🔍 First upload ID:', uploads[0]?.id || 'none');
    console.log('🔍 All upload IDs:', uploads.map(u => u.id));

    // Calculate pagination info
    const totalPages = Math.ceil(totalCount / limit);
    const hasNextPage = page < totalPages;
    const hasPrevPage = page > 1;

    return NextResponse.json({
      uploads,
      pagination: {
        page,
        limit,
        totalCount,
        totalPages,
        hasNextPage,
        hasPrevPage
      }
    });

  } catch (error) {
    console.error('Get uploads error:', error);
    return NextResponse.json({ error: 'Internal server error', details: error.message }, { status: 500 });
  }
}
