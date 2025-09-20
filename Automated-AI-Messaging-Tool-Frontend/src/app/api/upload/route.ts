import { NextRequest, NextResponse } from 'next/server';
import { PrismaClient } from '@prisma/client';

export async function POST(request: NextRequest) {
  try {
    // Get the request body
    const body = await request.json();
    
    if (!body.content) {
      return NextResponse.json({ 
        error: 'Missing required field: content' 
      }, { status: 400 });
    }

    // Convert base64 content back to buffer
    const fileContent = Buffer.from(body.content, 'base64');
    
    // Create FormData using native FormData (compatible with Node.js 18+)
    const formData = new FormData();
    
    // Create a Blob from the buffer and append it directly
    const blob = new Blob([fileContent], { 
      type: body.fileType === 'csv' ? 'text/csv' : 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet' 
    });
    
    // Append the blob to FormData with filename
    formData.append('file', blob, body.filename);
    
    // Forward the request to the backend on port 8001
    const backendUrl = process.env.PYTHON_API_URL || 'http://98.85.16.204:8001';
    const userId = body.userId || 'cmdi7lqnj0000sbp8h98vwlco'; // Default test user if not provided
    
    const backendResponse = await fetch(`${backendUrl}/api/upload-from-frontend?userId=${userId}`, {
      method: 'POST',
      body: formData
    });

    // Get the response from backend
    const backendData = await backendResponse.json();
    
    // Return the backend response with the same status
    return NextResponse.json(backendData, { status: backendResponse.status });

  } catch (error) {
    console.error('Upload proxy error:', error);
    return NextResponse.json({ 
      error: 'Failed to forward request to backend',
      details: error instanceof Error ? error.message : String(error)
    }, { status: 500 });
  }
}

const prisma = new PrismaClient({
  datasources: {
    db: {
      url: 'postgresql://postgres:AiMessaging2024Secure@production-ai-messaging-db.cmpkwkuqu30h.us-east-1.rds.amazonaws.com:5432/ai_messaging'
    }
  }
});

export async function GET(request: NextRequest) {
  try {
    const { searchParams } = new URL(request.url);
    const userId = searchParams.get('userId');
    const page = parseInt(searchParams.get('page') || '1');
    const limit = parseInt(searchParams.get('limit') || '10');
    const search = searchParams.get('search') || '';
    const status = searchParams.get('status') || 'all';

    if (!userId) {
      return NextResponse.json({ error: 'User ID is required' }, { status: 400 });
    }

    const whereClause: any = {
      userId: userId
    };

    if (status !== 'all') {
      whereClause.status = status;
    }

    if (search) {
      whereClause.OR = [
        { filename: { contains: search, mode: 'insensitive' } },
        { originalName: { contains: search, mode: 'insensitive' } }
      ];
    }

    const skip = (page - 1) * limit;

    const [fileUploads, totalCount] = await Promise.all([
      prisma.file_uploads.findMany({
        where: whereClause,
        orderBy: { createdAt: 'desc' },
        skip: skip,
        take: limit,
        select: {
          id: true,
          filename: true,
          originalName: true,
          fileType: true,
          fileSize: true,
          status: true,
          createdAt: true,
          updatedAt: true,
          totalWebsites: true,
          userId: true,
          websites: {
            select: {
              id: true,
              scrapingStatus: true,
              messageStatus: true
            }
          }
        }
      }),
      prisma.file_uploads.count({
        where: whereClause
      })
    ]);

    const totalPages = Math.ceil(totalCount / limit);
    const hasNextPage = page < totalPages;
    const hasPrevPage = page > 1;

    // Calculate accurate website statistics from actual website records
    const fileUploadsWithStats = fileUploads.map(upload => {
      console.log('Processing upload:', upload.id, 'websites:', upload.websites);
      const processedWebsites = upload.websites ? upload.websites.filter(w => w.scrapingStatus === 'COMPLETED').length : 0;
      const failedWebsites = upload.websites ? upload.websites.filter(w => w.scrapingStatus === 'FAILED').length : 0;
      
      console.log('Calculated stats for', upload.id, 'processed:', processedWebsites, 'failed:', failedWebsites);
      
      return {
        ...upload,
        processedWebsites: processedWebsites,
        failedWebsites: failedWebsites
      };
    });

    return NextResponse.json({
      fileUploads: fileUploadsWithStats,
      pagination: {
        page: page,
        limit: limit,
        totalCount: totalCount,
        totalPages: totalPages,
        hasNextPage: hasNextPage,
        hasPrevPage: hasPrevPage
      }
    });

  } catch (error) {
    console.error('Error fetching uploads:', error);
    return NextResponse.json({
      error: 'Failed to fetch uploads',
      details: error instanceof Error ? error.message : String(error)
    }, { status: 500 });
  } finally {
    await prisma.$disconnect();
  }
}