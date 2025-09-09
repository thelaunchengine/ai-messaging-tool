import { NextRequest, NextResponse } from 'next/server';
import { getServerSession } from 'next-auth';
import { authOptions } from 'utils/authOptions';
import { prisma } from 'lib/prisma';

export async function POST(
  request: NextRequest,
  { params }: { params: { fileUploadId: string; batchNumber: string } }
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

    const { fileUploadId, batchNumber } = params;
    const batchNum = parseInt(batchNumber);

    if (isNaN(batchNum)) {
      return NextResponse.json({ error: 'Invalid batch number' }, { status: 400 });
    }

    // Find the chunk for this batch
    const chunk = await prisma.processingChunk.findFirst({
      where: {
        fileUploadId,
        chunkNumber: batchNum
      }
    });

    if (!chunk) {
      return NextResponse.json({ error: 'Batch not found' }, { status: 404 });
    }

    // Update chunk status to processing
    await prisma.processingChunk.update({
      where: { id: chunk.id },
      data: {
        status: 'PROCESSING',
        startedAt: new Date()
      }
    });

    // Trigger backend scraping for this batch
    try {
      const params = new URLSearchParams({
        file_upload_id: fileUploadId,
        batch_number: batchNum.toString(),
        action: 'start_scraping'
      });

              await fetch(`${process.env.PYTHON_API_URL || 'http://103.215.159.51:8001'}/api/admin/batch/scraping?${params}`, {
        method: 'POST'
      });
    } catch (error) {
      console.error('Failed to trigger backend scraping:', error);
      // Revert chunk status if backend call fails
      await prisma.processingChunk.update({
        where: { id: chunk.id },
        data: { status: 'PENDING' }
      });
      return NextResponse.json({ error: 'Failed to start scraping on backend' }, { status: 500 });
    }

    return NextResponse.json({
      message: `Scraping started for batch ${batchNum}`,
      batchNumber: batchNum,
      status: 'PROCESSING'
    });

  } catch (error) {
    console.error('Start scraping error:', error);
    return NextResponse.json({ error: 'Internal server error' }, { status: 500 });
  }
}
