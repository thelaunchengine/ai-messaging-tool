import { NextRequest, NextResponse } from 'next/server';
import { PrismaClient } from '@prisma/client';

const prisma = new PrismaClient();

// POST - Stop a scraping job
export async function POST(request: NextRequest, { params }: { params: Promise<{ id: string }> }) {
  try {
    const { id: jobId } = await params;

    // Check if job exists and can be stopped
    const job = await prisma.scrapingJob.findUnique({
      where: { id: jobId }
    });

    if (!job) {
      return NextResponse.json({ error: 'Scraping job not found' }, { status: 404 });
    }

    if (job.status !== 'RUNNING') {
      return NextResponse.json({ error: 'Job is not running' }, { status: 400 });
    }

    // Update job status to failed (stopped)
    const updatedJob = await prisma.scrapingJob.update({
      where: { id: jobId },
      data: {
        status: 'FAILED',
        errorMessage: 'Job stopped by admin'
      }
    });

    return NextResponse.json({
      job: updatedJob,
      message: 'Scraping job stopped successfully'
    });
  } catch (error) {
    console.error('Error stopping scraping job:', error);
    return NextResponse.json({ error: 'Failed to stop scraping job' }, { status: 500 });
  }
}
