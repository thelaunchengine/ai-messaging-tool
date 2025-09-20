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
    
    // Fetch all users with their statistics
    const users = await prisma.users.findMany({
      include: {
        file_uploads: {
          select: {
            id: true,
            filename: true,
            status: true,
            totalWebsites: true,
            processedWebsites: true,
            createdAt: true
          }
        },
        websites: {
          select: {
            id: true,
            websiteUrl: true,
            contactFormUrl: true,
            sentMessage: true,
            messageStatus: true
          }
        }
      }
    });

    // Process user data to create reports
    const reports = users.map(user => {
      const filesUploaded = user.file_uploads.length;
      const websitesProcessed = user.websites.length;
      const messagesSent = user.websites.filter(w => w.sentMessage && w.messageStatus === 'SENT').length;
      const successRate = websitesProcessed > 0 ? Math.round((messagesSent / websitesProcessed) * 100) : 0;
      
      return {
        id: user.id,
        userName: user.name,
        userEmail: user.email,
        filesUploaded,
        websitesProcessed,
        messagesSent,
        successRate,
        subscription: user.role === 'ADMIN' ? 'admin' : 'basic',
        status: user.status
      };
    });

    return NextResponse.json({ reports });
  } catch (error) {
    console.error('Error fetching admin reports:', error);
    return NextResponse.json(
      { error: 'Failed to fetch admin reports' },
      { status: 500 }
    );
  } finally {
    await prisma.$disconnect();
  }
} 