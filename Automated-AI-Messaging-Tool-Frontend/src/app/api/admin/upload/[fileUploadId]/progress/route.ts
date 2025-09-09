import { NextRequest, NextResponse } from 'next/server';
import { getServerSession } from 'next-auth';
import { authOptions } from 'utils/authOptions';
import { prisma } from 'lib/prisma';

export async function GET(
  request: NextRequest,
  { params }: { params: { fileUploadId: string } }
) {
  try {
    const session = await getServerSession(authOptions);
    
    if (!session?.user?.id) {
      return NextResponse.json({ error: 'Unauthorized' }, { status: 401 });
    }

    // Check if user is admin
    const adminUser = await prisma.user.findUnique({
      where: { id: session.user.id },
      select: { role: true }
    });

    if (adminUser?.role !== 'ADMIN' && adminUser?.role !== 'admin') {
      return NextResponse.json({ error: 'Access denied. Admin privileges required.' }, { status: 403 });
    }

    const { fileUploadId } = params;

    // Get file upload with chunks and websites
    const fileUpload = await prisma.fileUpload.findUnique({
      where: { id: fileUploadId },
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
            companyName: true,
            industry: true,
            contactFormUrl: true
          }
        }
      }
    });

    if (!fileUpload) {
      return NextResponse.json({ error: 'File upload not found' }, { status: 404 });
    }

    // Calculate overall progress
    const totalChunks = fileUpload.chunks.length;
    const completedChunks = fileUpload.chunks.filter(chunk => chunk.status === 'COMPLETED').length;
    const processingChunks = fileUpload.chunks.filter(chunk => chunk.status === 'PROCESSING').length;
    const failedChunks = fileUpload.chunks.filter(chunk => chunk.status === 'FAILED').length;

    // Calculate website statistics
    const totalWebsites = fileUpload.websites.length;
    const scrapedWebsites = fileUpload.websites.filter(website => website.scrapingStatus === 'COMPLETED').length;
    const messageSentWebsites = fileUpload.websites.filter(website => website.messageStatus === 'SENT').length;

    // Prepare batch information
    const batches = fileUpload.chunks.map(chunk => ({
      batchNumber: chunk.chunkNumber,
      startIndex: chunk.startRow - 1,
      endIndex: chunk.endRow,
      totalUrls: chunk.totalRecords,
      status: chunk.status,
      progress: chunk.status === 'COMPLETED' ? 100 : 
                chunk.status === 'PROCESSING' ? Math.round((chunk.processedRecords / chunk.totalRecords) * 100) : 0,
      processedRecords: chunk.processedRecords,
      totalRecords: chunk.totalRecords
    }));

    // Determine overall status
    let overallStatus = 'PENDING';
    if (completedChunks === totalChunks) {
      overallStatus = 'COMPLETED';
    } else if (processingChunks > 0 || completedChunks > 0) {
      overallStatus = 'PROCESSING';
    } else if (failedChunks === totalChunks) {
      overallStatus = 'FAILED';
    }

    // Calculate overall progress percentage
    const overallProgress = totalChunks > 0 ? Math.round((completedChunks / totalChunks) * 100) : 0;

    return NextResponse.json({
      fileUploadId,
      filename: fileUpload.originalName,
      status: overallStatus,
      progress: overallProgress,
      totalChunks,
      completedChunks,
      processingChunks,
      failedChunks,
      totalWebsites,
      scrapedWebsites,
      messageSentWebsites,
      batches,
      createdAt: fileUpload.createdAt,
      processingStartedAt: fileUpload.processingStartedAt,
      processingCompletedAt: fileUpload.processingCompletedAt
    });

  } catch (error) {
    console.error('Get admin upload progress error:', error);
    return NextResponse.json({ error: 'Internal server error' }, { status: 500 });
  }
}
