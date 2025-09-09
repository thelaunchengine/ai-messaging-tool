import { NextRequest, NextResponse } from 'next/server';
import { getServerSession } from 'next-auth';
import { authOptions } from '../../../../../utils/authOptions';
import { prisma } from '../../../../../lib/prisma';

export async function GET(
  request: NextRequest,
  { params }: { params: Promise<{ fileUploadId: string }> }
) {
  try {
    const session = await getServerSession(authOptions);
    if (!session) {
      return NextResponse.json({ error: 'Unauthorized' }, { status: 401 });
    }

    const { fileUploadId } = await params;
    
    if (!fileUploadId) {
      return NextResponse.json({ error: 'File upload ID is required' }, { status: 400 });
    }

    console.log('🔍 Fetching websites for file upload:', fileUploadId);

    // Fetch websites from the database
    const websites = await prisma.website.findMany({
      where: {
        fileUploadId: fileUploadId
      },
      select: {
        id: true,
        websiteUrl: true,
        companyName: true,
        industry: true,
        businessType: true,
        aboutUsContent: true,
        contactFormUrl: true,
        scrapingStatus: true,
        messageStatus: true,
        generatedMessage: true,
        errorMessage: true,
        createdAt: true,
        updatedAt: true
      },
      orderBy: {
        createdAt: 'asc'
      }
    });

    console.log(`📊 Found ${websites.length} websites for file upload ${fileUploadId}`);

    return NextResponse.json({
      success: true,
      fileUploadId: fileUploadId,
      websites: websites,
      total: websites.length
    });

  } catch (error) {
    console.error('💥 Error fetching websites by file upload ID:', error);
    
    return NextResponse.json(
      { 
        error: 'Internal server error', 
        details: error instanceof Error ? error.message : 'Unknown error'
      },
      { status: 500 }
    );
  }
} 