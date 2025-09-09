import { NextRequest, NextResponse } from 'next/server';
import { PrismaClient } from '@prisma/client';

const prisma = new PrismaClient();

// POST - Resume a paused scraping job
export async function POST(request: NextRequest, { params }: { params: Promise<{ id: string }> }) {
  try {
    const { id: jobId } = await params;

    // Check if job exists and can be resumed
    const job = await prisma.scrapingJob.findUnique({
      where: { id: jobId }
    });

    if (!job) {
      return NextResponse.json({ error: 'Scraping job not found' }, { status: 404 });
    }

    if (job.status !== 'PAUSED') {
      return NextResponse.json({ error: 'Job is not paused' }, { status: 400 });
    }

    // Update job status to running
    const updatedJob = await prisma.scrapingJob.update({
      where: { id: jobId },
      data: {
        status: 'RUNNING'
      }
    });

    return NextResponse.json({
      job: updatedJob,
      message: 'Scraping job resumed successfully'
    });
  } catch (error) {
    console.error('Error resuming scraping job:', error);
    return NextResponse.json({ error: 'Failed to resume scraping job' }, { status: 500 });
  }
}
