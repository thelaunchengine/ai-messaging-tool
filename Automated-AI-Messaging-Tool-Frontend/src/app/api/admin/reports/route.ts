import { NextRequest, NextResponse } from 'next/server';
import { PrismaClient } from '@prisma/client';
import { getServerSession } from 'next-auth';
import { authOptions } from '../../_lib/auth';

const prisma = new PrismaClient();

export async function GET(request: NextRequest) {
  try {
    // Get user ID from the authenticated session
    const session = await getServerSession(authOptions);
    
    if (!session?.user?.id) {
      return NextResponse.json(
        { error: 'Unauthorized' },
        { status: 401 }
      );
    }

    // Check if user is admin
    const user = await prisma.user.findUnique({
      where: { id: session.user.id },
      select: { role: true }
    });

    if (user?.role !== 'ADMIN' && user?.role !== 'admin') {
      return NextResponse.json(
        { error: 'Access denied. Admin privileges required.' },
        { status: 403 }
      );
    }
    
    // Fetch all users with their statistics
    const users = await prisma.user.findMany({
      include: {
        fileUploads: {
          select: {
            id: true,
            filename: true,
            status: true,
            totalWebsites: true,
            createdAt: true
          }
        },
        websites: {
          select: {
            id: true,
            websiteUrl: true,
            contactFormUrl: true
          }
        }
      }
    });

    // Process user data to create reports
    const reports = users.map(user => {
      const filesUploaded = user.fileUploads.length;
      const websitesProcessed = user.websites.length;
      const messagesSent = 0; // Placeholder - would come from messages table
      const successRate = websitesProcessed > 0 ? Math.round((websitesProcessed / (websitesProcessed + 10)) * 100) : 0; // Mock calculation
      
      return {
        id: user.id,
        userName: user.name,
        userEmail: user.email,
        filesUploaded,
        websitesProcessed,
        messagesSent,
        successRate,
        lastActivity: user.createdAt ? new Date(user.createdAt).toLocaleDateString() : 'N/A',
        subscription: 'basic', // Placeholder - would come from subscription table
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
  }
} 