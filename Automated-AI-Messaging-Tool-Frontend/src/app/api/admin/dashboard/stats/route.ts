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
    
    // Fetch admin statistics from the database
    const [
      totalFileUploads,
      totalWebsites,
      totalContactPages,
      totalMessages,
      websitesWithoutContact,
      totalUsers,
      activeUsers,
      disabledUsers,
      activeScrapingJobs
    ] = await Promise.all([
      // Count total file uploads across all users
      prisma.fileUpload.count(),
      
      // Count total websites across all users
      prisma.website.count(),
      
      // Count websites with contact form URLs
      prisma.website.count({
        where: {
          contactFormUrl: { not: null }
        }
      }),
      
      // Count messages sent (placeholder for now)
      Promise.resolve(0),
      
      // Count websites without contact pages
      prisma.website.count({
        where: {
          contactFormUrl: null
        }
      }),
      
      // Count total users
      prisma.user.count(),
      
      // Count active users
      prisma.user.count({
        where: { status: 'active' }
      }),
      
      // Count disabled users
      prisma.user.count({
        where: { status: 'disabled' }
      }),
      
      // Get active scraping jobs
      prisma.fileUpload.findMany({
        where: {
          status: 'PROCESSING'
        },
        orderBy: { createdAt: 'desc' }
      })
    ]);

    // Calculate batch processing status
    const batchStatus = activeScrapingJobs.length > 0 
      ? `${activeScrapingJobs.length} active batch${activeScrapingJobs.length > 1 ? 'es' : ''}`
      : 'No active batches';

    const stats = [
      {
        label: 'List Submitted',
        value: totalFileUploads,
        icon: 'CloudUpload',
        change: '', // Removed percentage
        color: '#4F8CFF'
      },
      {
        label: 'Total Websites',
        value: totalWebsites,
        icon: 'ListAlt',
        change: '', // Removed percentage
        color: '#FFB547'
      },
      {
        label: 'Contact Pages',
        value: totalContactPages,
        icon: 'CheckCircle',
        change: '', // Removed percentage
        color: '#4CAF50'
      },
      {
        label: 'Messages',
        value: totalMessages,
        icon: 'Message',
        change: '', // Removed percentage
        color: '#2196F3'
      },
      {
        label: 'Websites w/o Contact Page',
        value: websitesWithoutContact,
        icon: 'ErrorOutline',
        change: '', // Removed percentage
        color: '#F44336'
      },
      {
        label: 'Total Users',
        value: totalUsers,
        icon: 'People',
        change: '', // Removed percentage
        color: '#FF9800'
      },
      {
        label: 'Batch-wise Scraping',
        value: batchStatus,
        icon: 'Assignment',
        change: '', // Removed percentage
        color: '#2196F3'
      }
    ];

    return NextResponse.json({ stats });
  } catch (error) {
    console.error('Error fetching admin dashboard stats:', error);
    return NextResponse.json(
      { error: 'Failed to fetch admin dashboard statistics' },
      { status: 500 }
    );
  }
} 