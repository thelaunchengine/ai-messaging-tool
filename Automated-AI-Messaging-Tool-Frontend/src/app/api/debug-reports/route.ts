import { NextRequest, NextResponse } from 'next/server';
import { PrismaClient } from '@prisma/client';

const prisma = new PrismaClient({
  datasources: {
    db: {
      url: 'postgresql://postgres:AiMessaging2024Secure@production-ai-messaging-db.cmpkwkuqu30h.us-east-1.rds.amazonaws.com:5432/ai_messaging'
    }
  }
});

export async function GET(request: NextRequest) {
  try {
    // Get total counts
    const totalFiles = await prisma.file_uploads.count();
    const totalWebsites = await prisma.websites.count();
    
    // Check message statuses - handle null values properly
    const messageStatuses = await prisma.websites.groupBy({
      by: ['messageStatus'],
      _count: true
    });
    
    // Check websites with sent messages - use different approach
    const websitesWithSentMessages = await prisma.websites.count({
      where: {
        sentMessage: {
          not: null
        }
      }
    });
    
    // Check websites with any message status - use different approach
    const websitesWithAnyMessage = await prisma.websites.count({
      where: {
        messageStatus: {
          not: null
        }
      }
    });
    
    // Check form submission statuses
    const formSubmissionStatuses = await prisma.websites.groupBy({
      by: ['submissionStatus'],
      _count: true
    });
    
    // Sample of websites data
    const sampleWebsites = await prisma.websites.findMany({
      take: 5,
      select: {
        id: true,
        websiteUrl: true,
        messageStatus: true,
        sentMessage: true,
        submissionStatus: true,
        aiMessageStatus: true
      }
    });

    return NextResponse.json({
      totalFiles,
      totalWebsites,
      messageStatuses,
      websitesWithSentMessages,
      websitesWithAnyMessage,
      formSubmissionStatuses,
      sampleWebsites
    });
  } catch (error) {
    console.error('Error in debug reports:', error);
    return NextResponse.json(
      { error: `Failed to fetch debug data: ${error.message}` },
      { status: 500 }
    );
  } finally {
    await prisma.$disconnect();
  }
}
