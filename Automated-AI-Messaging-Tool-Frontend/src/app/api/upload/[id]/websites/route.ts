import { NextRequest, NextResponse } from 'next/server';
import { PrismaClient } from '@prisma/client';

const prisma = new PrismaClient({
  datasources: {
    db: {
      url: 'postgresql://postgres:AiMessaging2024Secure@production-ai-messaging-db.cmpkwkuqu30h.us-east-1.rds.amazonaws.com:5432/ai_messaging'
    }
  }
});

export async function GET(request: NextRequest, { params }: { params: Promise<{ id: string }> }) {
  try {
    const { id: fileUploadId } = await params;
    const { searchParams } = new URL(request.url);
    
    // Pagination parameters
    const page = parseInt(searchParams.get('page') || '1');
    const limit = parseInt(searchParams.get('limit') || '50');
    const search = searchParams.get('search') || '';
    const sortBy = searchParams.get('sortBy') || 'updatedAt';
    const sortOrder = searchParams.get('sortOrder') || 'desc';
    
    const skip = (page - 1) * limit;
    
    // Build where clause
    const where: any = {
      fileUploadId: fileUploadId
    };
    
    // Add search filter if provided
    if (search) {
      where.OR = [
        { websiteUrl: { contains: search, mode: 'insensitive' } },
        { contactFormUrl: { contains: search, mode: 'insensitive' } },
        { companyName: { contains: search, mode: 'insensitive' } },
        { industry: { contains: search, mode: 'insensitive' } }
      ];
    }
    
    // Get total count for pagination
    const total = await prisma.websites.count({ where });
    
    // Get paginated websites
    const websites = await prisma.websites.findMany({
      where,
      select: {
        id: true,
        websiteUrl: true,
        contactFormUrl: true,
        hasContactForm: true,
        companyName: true,
        businessType: true,
        industry: true,
        aboutUsContent: true,
        scrapingStatus: true,
        messageStatus: true,
        generatedMessage: true,
        submissionStatus: true,
        submissionResponse: true,
        submissionError: true,
        submittedFormFields: true,
        createdAt: true,
        updatedAt: true
      },
      orderBy: {
        [sortBy]: sortOrder
      },
      skip,
      take: limit
    });

    // Return websites with submission status (already in database)
    const websitesWithSubmissionStatus = websites.map(website => ({
      ...website,
      submissionStatus: website.submissionStatus || "PENDING"
    }));
    
    return NextResponse.json({
      websites: websitesWithSubmissionStatus,
      pagination: {
        page,
        limit,
        total,
        pages: Math.ceil(total / limit),
        hasNext: page * limit < total,
        hasPrev: page > 1
      }
    });
  } catch (error) {
    console.error('Error fetching websites:', error);
    return NextResponse.json({ error: 'Failed to fetch websites' }, { status: 500 });
  } finally {
    await prisma.$disconnect();
  }
}
