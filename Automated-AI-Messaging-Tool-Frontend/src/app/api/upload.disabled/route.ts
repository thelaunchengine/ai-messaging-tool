import { NextRequest, NextResponse } from 'next/server';
import { z } from 'zod';
import * as XLSX from 'xlsx';
import { parse } from 'csv-parse/sync';
import { getServerSession } from 'next-auth';
import { authOptions } from 'utils/authOptions';
import { prisma } from 'lib/prisma';

// Validation schema for file upload
const uploadSchema = z.object({
  filename: z.string(),
  originalName: z.string(),
  fileSize: z.number().positive(),
  fileType: z.enum(['csv', 'xlsx']),
  content: z.string() // Base64 encoded file content
});

// Website data schema
const websiteSchema = z.object({
  websiteUrl: z.string().url(),
  contactFormUrl: z.string().url().optional()
});

// Helper function to intelligently map column names
const mapColumnNames = (headers: string[]): { websiteUrlColumn: string | null, contactFormUrlColumn: string | null } => {
  const websiteUrlPatterns = [
    'website url', 'websiteurl', 'website_url', 'website', 'url', 'site url', 'siteurl', 'site_url',
    'web url', 'weburl', 'web_url', 'domain', 'website domain', 'website_domain', 'website-domain',
    'site', 'website address', 'website_address', 'website-address', 'web address', 'web_address',
    'web-address', 'link', 'website link', 'website_link', 'website-link', 'web link', 'web_link',
    'web-link', 'page url', 'pageurl', 'page_url', 'page-url'
  ];

  const contactFormUrlPatterns = [
    'contact form url', 'contactformurl', 'contact_form_url', 'contact-form-url',
    'contact form', 'contactform', 'contact_form', 'contact-form', 'contact page',
    'contactpage', 'contact_page', 'contact-page', 'contact link', 'contactlink',
    'contact_link', 'contact-link', 'contact us', 'contactus', 'contact_us',
    'contact-us', 'contact form link', 'contactformlink', 'contact_form_link',
    'contact-form-link', 'contact page url', 'contactpageurl', 'contact_page_url',
    'contact-page-url', 'contact us url', 'contactusurl', 'contact_us_url',
    'contact-us-url', 'form url', 'formurl', 'form_url', 'form-url',
    'contact form page', 'contactformpage', 'contact_form_page', 'contact-form-page'
  ];

  let websiteUrlColumn: string | null = null;
  let contactFormUrlColumn: string | null = null;

  // Normalize headers for comparison (lowercase, trim, remove special chars)
  const normalizedHeaders = headers.map(header => 
    header.toLowerCase().trim().replace(/[^a-z0-9]/g, '')
  );

  // Find website URL column
  for (let i = 0; i < headers.length; i++) {
    const normalizedHeader = normalizedHeaders[i];
    const originalHeader = headers[i];
    
    // Check if this header matches any website URL pattern
    if (websiteUrlPatterns.some(pattern => 
      normalizedHeader.includes(pattern.replace(/[^a-z0-9]/g, ''))
    )) {
      websiteUrlColumn = originalHeader;
      break;
    }
  }

  // Find contact form URL column
  for (let i = 0; i < headers.length; i++) {
    const normalizedHeader = normalizedHeaders[i];
    const originalHeader = headers[i];
    
    // Check if this header matches any contact form pattern
    if (contactFormUrlPatterns.some(pattern => 
      normalizedHeader.includes(pattern.replace(/[^a-z0-9]/g, ''))
    )) {
      contactFormUrlColumn = originalHeader;
      break;
    }
  }

  return { websiteUrlColumn, contactFormUrlColumn };
};

export async function POST(request: NextRequest) {
  try {
    const body = await request.json();
    const { filename, originalName, fileSize, fileType, content } = uploadSchema.parse(body);

    // Get user from session
    const session = await getServerSession(authOptions);
    let userId: string;

    console.log('Session:', session ? 'Found' : 'Not found');

    if (!session?.user?.id) {
      // For testing purposes, use the first available user ID
      const firstUser = await prisma.user.findFirst({
        select: { id: true, email: true }
      });

      if (!firstUser) {
        return NextResponse.json({ error: 'No users found in database. Please register first.' }, { status: 400 });
      }

      userId = firstUser.id;
      console.log(`Using default user ID for testing: ${userId} (${firstUser.email})`);
    } else {
      // Validate that the session user ID actually exists in the database
      const sessionUser = await prisma.user.findUnique({
        where: { id: session.user.id },
        select: { id: true, email: true }
      });

      if (!sessionUser) {
        console.log(`Session user ID ${session.user.id} not found in database, using default user`);
        // Use the first available user instead
        const firstUser = await prisma.user.findFirst({
          select: { id: true, email: true }
        });

        if (!firstUser) {
          return NextResponse.json({ error: 'No users found in database. Please register first.' }, { status: 400 });
        }

        userId = firstUser.id;
        console.log(`Using default user ID: ${userId} (${firstUser.email})`);
      } else {
        userId = session.user.id;
        console.log(`Using session user ID: ${userId} (${sessionUser.email})`);
      }
    }

    // Decode base64 content
    const buffer = Buffer.from(content, 'base64');

    // Process file to get accurate record count and sample data
    let totalRecords = 0;
    let sampleData: any[] = [];
    let allRecords: any[] = [];

    // Get headers and map columns
    let headers: string[] = [];
    let columnMapping: { websiteUrlColumn: string | null, contactFormUrlColumn: string | null } = { websiteUrlColumn: null, contactFormUrlColumn: null };

    try {
      if (fileType === 'csv') {
        const csvContent = buffer.toString('utf-8');
        
        // First, get headers from the first line
        const lines = csvContent.split('\n');
        if (lines.length > 0) {
          headers = lines[0].split(',').map(header => header.trim().replace(/"/g, ''));
          columnMapping = mapColumnNames(headers);
        }
        
        // Parse all records to get accurate count
        allRecords = parse(csvContent, {
          columns: true,
          skip_empty_lines: true,
          trim: true
        });
        
        // Filter out rows that are completely empty or have no website URL
        const validRecords = allRecords.filter(record => {
          const websiteUrl = columnMapping.websiteUrlColumn ? record[columnMapping.websiteUrlColumn] : 
                           record.websiteUrl || record['Website URL'] || record['website_url'] || record['website url'] || record['Website'];
          return websiteUrl && websiteUrl.trim() !== '';
        });
        
        totalRecords = validRecords.length;
        sampleData = validRecords.slice(0, 100); // First 100 for validation

      } else if (fileType === 'xlsx') {
        const workbook = XLSX.read(buffer, { type: 'buffer' });
        const sheetName = workbook.SheetNames[0];
        const worksheet = workbook.Sheets[sheetName];
        
        // Get headers from the first row
        const headerRow = XLSX.utils.sheet_to_json(worksheet, { range: 0, header: 1 })[0] as any[];
        headers = headerRow.map(header => String(header || '').trim());
        columnMapping = mapColumnNames(headers);
        
        // Parse all records
        allRecords = XLSX.utils.sheet_to_json(worksheet, { 
          range: 1, // Skip header row
          header: 1, 
          defval: '' 
        });
        
        // Filter out rows that are completely empty or have no website URL
        const validRecords = allRecords.filter(record => {
          const websiteUrl = columnMapping.websiteUrlColumn ? record[columnMapping.websiteUrlColumn] : 
                           record.websiteUrl || record['Website URL'] || record['website_url'] || record['website url'] || record['Website'];
          return websiteUrl && websiteUrl.trim() !== '';
        });
        
        totalRecords = validRecords.length;
        sampleData = validRecords.slice(0, 100); // First 100 for validation
      }
    } catch (error) {
      return NextResponse.json({ error: 'Invalid file format or corrupted file' }, { status: 400 });
    }

    // Validate sample data structure
    if (sampleData.length === 0) {
      return NextResponse.json({ error: 'No valid data found in file' }, { status: 400 });
    }

    // Check if required columns exist
    if (!columnMapping.websiteUrlColumn) {
      return NextResponse.json({ 
        error: "File must contain a column with website URLs. Supported column names include: 'Website URL', 'website_url', 'Website', 'URL', 'Site URL', 'Domain', etc." 
      }, { status: 400 });
    }

    // Check if user has already uploaded a file with the same name
    const existingFile = await prisma.fileUpload.findFirst({
      where: {
        userId,
        originalName: originalName
      }
    });

    if (existingFile) {
      return NextResponse.json({ 
        error: `A file with the name "${originalName}" has already been uploaded. Please use a different filename or rename your file.` 
      }, { status: 400 });
    }

    // Create file upload record first (without file path since we're not saving locally)
    const fileUpload = await prisma.fileUpload.create({
      data: {
        userId,
        filename,
        originalName,
        fileSize,
        fileType,
        totalWebsites: totalRecords,
        totalChunks: 1, // Simplified to single chunk
        filePath: '', // Will be set by backend
        status: 'PENDING'
      }
    });

    // Upload file directly to backend for immediate processing
    try {
      // Create FormData for file upload
      const formData = new FormData();
      formData.append('file', new Blob([Buffer.from(content, 'base64')], { type: 'text/csv' }), filename);
      
      console.log('Uploading to backend endpoint:', `${process.env.PYTHON_API_URL || 'http://localhost:8001'}/api/upload-from-frontend`);

      // Call the new backend endpoint that handles frontend uploads
      const backendResponse = await fetch(`${process.env.PYTHON_API_URL || 'http://localhost:8001'}/api/upload-from-frontend?userId=${userId}`, {
        method: 'POST',
        body: formData
      });

      if (backendResponse.ok) {
        const backendResult = await backendResponse.json();
        console.log('Backend upload successful:', backendResult);
        
        // Update the file upload record with backend information
        await prisma.fileUpload.update({
          where: { id: fileUpload.id },
          data: {
            status: 'PROCESSING',
            filePath: backendResult.filePath || '', // Use backend file path
            totalWebsites: backendResult.totalWebsites || totalRecords
          }
        });

    return NextResponse.json(
      {
            message: 'File uploaded successfully and sent to backend for immediate processing.',
        fileUpload: {
          id: fileUpload.id,
          totalWebsites: fileUpload.totalWebsites,
              totalChunks: 1,
              status: 'PROCESSING'
        },
        processingInfo: {
              estimatedTime: '2-5 minutes',
              status: 'Processing started automatically'
        }
      },
      { status: 201 }
    );
      } else {
        const errorText = await backendResponse.text();
        console.error('Backend upload failed:', errorText);
        
        // Update status to ERROR
        await prisma.fileUpload.update({
          where: { id: fileUpload.id },
          data: { status: 'ERROR' }
        });

        return NextResponse.json({ 
          error: 'Failed to upload to backend for processing',
          details: errorText
        }, { status: 500 });
      }
    } catch (error) {
      console.error('Failed to upload to backend:', error);
      
      // Update status to ERROR
      await prisma.fileUpload.update({
        where: { id: fileUpload.id },
        data: { status: 'ERROR' }
      });

      return NextResponse.json({ 
        error: 'Failed to upload to backend for processing',
        details: error instanceof Error ? error.message : 'Unknown error'
      }, { status: 500 });
    }
  } catch (error) {
    if (error instanceof z.ZodError) {
      return NextResponse.json(
        {
          error: 'Validation error',
          details: error.errors
        },
        { status: 400 }
      );
    }

    console.error('File upload error:', error);
    return NextResponse.json({ error: 'Internal server error' }, { status: 500 });
  }
}

export async function GET(request: NextRequest) {
  try {
    const { searchParams } = new URL(request.url);
    let userId = searchParams.get('userId');
    const fileUploadId = searchParams.get('fileUploadId');
    const page = parseInt(searchParams.get('page') || '1');
    const limit = parseInt(searchParams.get('limit') || '10');
    const search = searchParams.get('search') || '';
    const statusFilter = searchParams.get('status') || '';

    if (!userId) {
      return NextResponse.json({ error: 'User ID is required' }, { status: 400 });
    }

    // Validate that the user ID exists in the database
    const user = await prisma.user.findUnique({
      where: { id: userId },
      select: { id: true, email: true }
    });

    if (!user) {
      console.log(`User ID ${userId} not found in database, using first available user`);
      // Use the first available user instead
      const firstUser = await prisma.user.findFirst({
        select: { id: true, email: true }
      });

      if (!firstUser) {
        return NextResponse.json({ error: 'No users found in database' }, { status: 400 });
      }

      userId = firstUser.id;
      console.log(`Using default user ID: ${userId} (${firstUser.email})`);
    } else {
      console.log(`Using provided user ID: ${userId} (${user.email})`);
    }

    if (fileUploadId) {
      // Get specific file upload with progress
      const fileUpload = await prisma.fileUpload.findUnique({
        where: { id: fileUploadId, userId },
        include: {
          chunks: {
            orderBy: { chunkNumber: 'asc' }
          },
          websites: {
            select: {
              id: true,
              websiteUrl: true,
              scrapingStatus: true,
              messageStatus: true,
              generatedMessage: true
            }
          }
        }
      });

      if (!fileUpload) {
        return NextResponse.json({ error: 'File upload not found' }, { status: 404 });
      }

      return NextResponse.json({ fileUpload });
    } else {
      // Build where clause for filtering
      const whereClause: any = { userId };
      
      if (search) {
        whereClause.OR = [
          { originalName: { contains: search, mode: 'insensitive' } },
          { filename: { contains: search, mode: 'insensitive' } }
        ];
      }
      
      if (statusFilter && statusFilter !== 'all') {
        whereClause.status = statusFilter;
      }

      // Get total count for pagination
      const totalCount = await prisma.fileUpload.count({
        where: whereClause
      });

      // Calculate pagination
      const totalPages = Math.ceil(totalCount / limit);
      const skip = (page - 1) * limit;
      const hasNextPage = page < totalPages;
      const hasPreviousPage = page > 1;

      // Get paginated file uploads for user
      const fileUploads = await prisma.fileUpload.findMany({
        where: whereClause,
        include: {
          chunks: {
            select: {
              chunkNumber: true,
              status: true,
              processedRecords: true,
              totalRecords: true
            }
          },
          websites: {
            select: {
              id: true,
              websiteUrl: true,
              scrapingStatus: true,
              messageStatus: true,
              generatedMessage: true
            }
          }
        },
        orderBy: { createdAt: 'desc' },
        skip,
        take: limit
      });

      return NextResponse.json({ 
        fileUploads,
        pagination: {
          page,
          limit,
          totalCount,
          totalPages,
          hasNextPage,
          hasPreviousPage
        }
      });
    }
  } catch (error) {
    console.error('Get file uploads error:', error);
    return NextResponse.json({ error: 'Internal server error' }, { status: 500 });
  }
}
