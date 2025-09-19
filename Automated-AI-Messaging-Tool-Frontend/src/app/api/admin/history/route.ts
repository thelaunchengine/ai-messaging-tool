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
    // Get user ID from query parameters (passed from frontend)
    const { searchParams } = new URL(request.url);
    const userId = searchParams.get('userId');

    if (!userId) {
      return NextResponse.json(
        { error: 'User ID is required' },
        { status: 400 }
      );
    }

    // Check if user is admin
    const user = await prisma.users.findUnique({
      where: { id: userId },
      select: { role: true }
    });

    if (user?.role !== 'ADMIN' && user?.role !== 'admin') {
      return NextResponse.json(
        { error: 'Access denied. Admin privileges required.' },
        { status: 403 }
      );
    }

    // Admin can see all file uploads from all users

    // Get file uploads with user data, handling cases where user might not exist
    const fileUploads = await prisma.file_uploads.findMany({
      select: {
        id: true,
        userId: true,
        originalName: true,
        fileSize: true,
        status: true,
        totalWebsites: true,
        createdAt: true,
        updatedAt: true,
        websites: {
          select: {
            id: true,
            scrapingStatus: true,
            messageStatus: true
          }
        }
      },
      orderBy: { createdAt: 'desc' }
    });

    // Get user data separately to handle missing relationships
    const userIds = fileUploads.map(f => f.userId);
    const users = await prisma.users.findMany({
      where: { id: { in: userIds } },
      select: { id: true, name: true, email: true }
    });

    const userMap = new Map(users.map(u => [u.id, u]));

    const historyData = fileUploads.map(upload => {
      const processedWebsites = upload.websites.filter(w => w.scrapingStatus === 'COMPLETED').length;
      const failedWebsites = upload.websites.filter(w => w.scrapingStatus === 'FAILED').length;
      const messagesSent = upload.websites.filter(w => w.messageStatus === 'SENT').length;
      
      const user = userMap.get(upload.userId);
      
      return {
        id: upload.id,
        fileName: upload.originalName,
        userName: user?.name || 'Unknown User',
        userEmail: user?.email || 'Unknown Email',
        fileSize: upload.fileSize || 'Unknown',
        fileType: upload.originalName.split('.').pop()?.toUpperCase() || 'Unknown',
        uploadDate: upload.createdAt,
        status: upload.status.toLowerCase(),
        websitesCount: upload.totalWebsites,
        messagesSent: messagesSent,
        processedWebsites: processedWebsites,
        failedWebsites: failedWebsites,
        successRate: upload.totalWebsites > 0 ? Math.round((processedWebsites / upload.totalWebsites) * 100) : 0,
        processingTime: upload.updatedAt ? 
          Math.round((new Date(upload.updatedAt).getTime() - new Date(upload.createdAt).getTime()) / 1000 / 60) + 'm' : 'Unknown'
      };
    });

    return NextResponse.json({ history: historyData });
  } catch (error) {
    console.error('Error fetching admin history:', error);
    return NextResponse.json({ error: 'Failed to fetch history data' }, { status: 500 });
  } finally {
    await prisma.$disconnect();
  }
} 