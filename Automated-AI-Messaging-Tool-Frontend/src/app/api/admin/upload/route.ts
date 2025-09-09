import { NextRequest, NextResponse } from 'next/server';
import { getServerSession } from 'next-auth';
import { authOptions } from '../../../../utils/authOptions';
import { prisma } from '../../../../lib/prisma';

export async function POST(request: NextRequest) {
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

    const body = await request.json();
    const { filename, originalName, fileSize, fileType, content, totalUrls, batchSize, enableScraping } = body;

    if (!filename || !originalName || !fileSize || !fileType || !content || !totalUrls) {
      return NextResponse.json({ error: 'Missing required fields' }, { status: 400 });
    }

    // Calculate batches
    const calculatedBatchSize = batchSize || 10000;
    const totalBatches = Math.ceil(totalUrls / calculatedBatchSize);

    // Create file upload record
    const fileUpload = await prisma.fileUpload.create({
      data: {
        userId: session.user.id,
        filename,
        originalName,
        fileSize,
        fileType,
        totalWebsites: totalUrls,
        totalChunks: totalBatches,
        status: 'PENDING',
        processingStartedAt: new Date()
      }
    });

    // Create batch records
    const batchData = [];
    for (let i = 0; i < totalBatches; i++) {
      const startIndex = i * calculatedBatchSize;
      const endIndex = Math.min((i + 1) * calculatedBatchSize, totalUrls);
      const batchUrls = endIndex - startIndex;

      batchData.push({
        fileUploadId: fileUpload.id,
        chunkNumber: i + 1,
        startRow: startIndex + 1,
        endRow: endIndex,
        totalRecords: batchUrls,
        status: 'PENDING'
      });
    }

    await prisma.processingChunk.createMany({
      data: batchData
    });

    // Trigger background processing for admin
    try {
      const params = new URLSearchParams({
        file_upload_id: fileUpload.id,
        total_urls: totalUrls.toString(),
        total_batches: totalBatches.toString(),
        batch_size: calculatedBatchSize.toString(),
        enable_scraping: enableScraping.toString(),
        is_admin: 'true'
      });

      // Call backend API for processing
              await fetch(`${process.env.PYTHON_API_URL || 'http://103.215.159.51:8001'}/api/admin/process-file?${params}`, {
        method: 'POST'
      });
    } catch (error) {
      console.error('Failed to trigger admin background processing:', error);
      // Don't fail the upload if background processing fails
    }

    return NextResponse.json({
      id: fileUpload.id,
      filename,
      totalWebsites: totalUrls,
      status: 'PENDING',
      message: `File uploaded successfully. Processing ${totalUrls} URLs in ${totalBatches} batches.`,
      batches: totalBatches,
      batchSize: calculatedBatchSize
    });

  } catch (error) {
    console.error('Admin upload error:', error);
    return NextResponse.json({ error: 'Internal server error' }, { status: 500 });
  }
}

export async function GET(request: NextRequest) {
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

    const { searchParams } = new URL(request.url);
    const page = parseInt(searchParams.get('page') || '1');
    const limit = parseInt(searchParams.get('limit') || '10');
    const search = searchParams.get('search') || '';
    const statusFilter = searchParams.get('status') || '';

    const whereClause: any = {};
    
    if (search) {
      whereClause.OR = [
        { originalName: { contains: search, mode: 'insensitive' } },
        { filename: { contains: search, mode: 'insensitive' } }
      ];
    }
    
    if (statusFilter && statusFilter !== 'all') {
      whereClause.status = statusFilter;
    }

    const totalCount = await prisma.fileUpload.count({
      where: whereClause
    });

    const totalPages = Math.ceil(totalCount / limit);
    const skip = (page - 1) * limit;

    const fileUploads = await prisma.fileUpload.findMany({
      where: whereClause,
      include: {
        chunks: {
          select: {
            chunkNumber: true,
            status: true,
            processedRecords: true,
            totalRecords: true
          }
        },
        websites: {
          select: {
            id: true,
            websiteUrl: true,
            scrapingStatus: true,
            messageStatus: true,
            generatedMessage: true
          }
        }
      },
      orderBy: { createdAt: 'desc' },
      skip,
      take: limit
    });

    return NextResponse.json({
      fileUploads,
      pagination: {
        page,
        limit,
        totalCount,
        totalPages,
        hasNextPage: page < totalPages,
        hasPreviousPage: page > 1
      }
    });

  } catch (error) {
    console.error('Get admin uploads error:', error);
    return NextResponse.json({ error: 'Internal server error' }, { status: 500 });
  }
}
