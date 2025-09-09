import { NextRequest, NextResponse } from 'next/server';
import { PrismaClient } from '@prisma/client';
import { getServerSession } from 'next-auth';
import { authOptions } from '../../../../utils/authOptions';

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
    
    const userId = session.user.id;
    
    // Fetch real statistics from the database
    const [
      fileUploads,
      websites,
      contactPages,
      messagesSent,
      websitesWithoutContact,
      recentFileActivity,
      recentMessageActivity
    ] = await Promise.all([
      // Count file uploads
      prisma.fileUpload.count({
        where: { userId }
      }),
      
      // Count total websites
      prisma.website.count({
        where: { userId }
      }),
      
      // Count websites with contact form URLs
      prisma.website.count({
        where: {
          userId,
          contactFormUrl: { not: null }
        }
      }),
      
      // Count messages sent (this would be from a messages table if it exists)
      // For now, we'll use a placeholder
      Promise.resolve(0),
      
      // Count websites without contact pages
      prisma.website.count({
        where: {
          userId,
          contactFormUrl: null
        }
      }),
      
      // Get recent file upload activity
      prisma.fileUpload.findMany({
        where: { userId },
        orderBy: { createdAt: 'desc' },
        take: 3,
        select: {
          id: true,
          filename: true,
          status: true,
          createdAt: true,
          totalWebsites: true
        }
      }),
      
      // Get recent message activity (placeholder for now)
      Promise.resolve([])
    ]);

    // Calculate dynamic batch processing status
    const activeScrapingJobs = await prisma.fileUpload.findMany({
      where: {
        userId,
        status: 'PROCESSING'
      },
      orderBy: { createdAt: 'desc' }
    });

    const batchStatus = activeScrapingJobs.length > 0 
      ? `${activeScrapingJobs.length} active batch${activeScrapingJobs.length > 1 ? 'es' : ''}`
      : 'No active batches';

    // Format recent file activity
    const formattedFileActivity = recentFileActivity.map(activity => ({
      type: 'File Upload',
      detail: activity.filename,
      time: getTimeAgo(activity.createdAt),
      status: activity.status,
      websites: activity.totalWebsites
    }));

    // Only show real user-specific activities, no hardcoded data
    const allRecentActivity = [...formattedFileActivity]
      .sort((a, b) => {
        const timeA = getTimeInSeconds(a.time);
        const timeB = getTimeInSeconds(b.time);
        return timeA - timeB;
      })
      .slice(0, 5);

    const stats = {
      firstRow: [
        { label: 'List Submitted', value: fileUploads, icon: 'CloudUpload' },
        { label: 'Total Websites', value: websites, icon: 'ListAlt' },
        { label: 'Contact Pages', value: contactPages, icon: 'CheckCircle' }
      ],
      secondRow: [
        { label: 'Messages', value: messagesSent, icon: 'Message' },
        { label: 'Websites w/o Contact Page', value: websitesWithoutContact, icon: 'ErrorOutline' },
        { label: 'Batch-wise Scraping', value: batchStatus, icon: 'BatchPrediction' }
      ],
      recentActivity: allRecentActivity
    };

    return NextResponse.json(stats);
  } catch (error) {
    console.error('Error fetching dashboard stats:', error);
    return NextResponse.json(
      { error: 'Failed to fetch dashboard statistics' },
      { status: 500 }
    );
  }
}

function getTimeAgo(date: Date): string {
  const now = new Date();
  const diffInSeconds = Math.floor((now.getTime() - date.getTime()) / 1000);
  
  if (diffInSeconds < 60) return `${diffInSeconds} seconds ago`;
  if (diffInSeconds < 3600) return `${Math.floor(diffInSeconds / 60)} minutes ago`;
  if (diffInSeconds < 86400) return `${Math.floor(diffInSeconds / 3600)} hours ago`;
  return `${Math.floor(diffInSeconds / 86400)} days ago`;
}

function getTimeInSeconds(timeString: string): number {
  if (timeString.includes('seconds')) {
    return parseInt(timeString.split(' ')[0]);
  }
  if (timeString.includes('minutes')) {
    return parseInt(timeString.split(' ')[0]) * 60;
  }
  if (timeString.includes('hours')) {
    return parseInt(timeString.split(' ')[0]) * 3600;
  }
  if (timeString.includes('days')) {
    return parseInt(timeString.split(' ')[0]) * 86400;
  }
  return 0;
} 