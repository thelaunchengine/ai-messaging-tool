import { NextRequest, NextResponse } from 'next/server';
import { PrismaClient } from '@prisma/client';
import { getServerSession } from 'next-auth';
import { authOptions } from 'utils/authOptions';

const prisma = new PrismaClient();

export async function GET(request: NextRequest) {
  try {
    const session = await getServerSession(authOptions);
    
    if (!session?.user?.id) {
      return NextResponse.json({ error: 'Unauthorized' }, { status: 401 });
    }

    const adminUser = await prisma.user.findUnique({
      where: { id: session.user.id },
      select: { role: true }
    });

    if (adminUser?.role !== 'ADMIN' && adminUser?.role !== 'admin') {
      return NextResponse.json({ error: 'Access denied. Admin privileges required.' }, { status: 403 });
    }

    const fileUploads = await prisma.fileUpload.findMany({
      include: {
        user: {
          select: {
            id: true,
            name: true,
            email: true
          }
        },
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

    const historyData = fileUploads.map(upload => {
      const processedWebsites = upload.websites.filter(w => w.scrapingStatus === 'COMPLETED').length;
      const failedWebsites = upload.websites.filter(w => w.scrapingStatus === 'FAILED').length;
      const messagesSent = upload.websites.filter(w => w.messageStatus === 'SENT').length;
      
      return {
        id: upload.id,
        fileName: upload.originalName,
        userName: upload.user.name || 'Unknown User',
        userEmail: upload.user.email,
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
  }
} 