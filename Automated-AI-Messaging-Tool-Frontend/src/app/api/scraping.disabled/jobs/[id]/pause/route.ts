import { NextRequest, NextResponse } from 'next/server';
import { PrismaClient } from '@prisma/client';

const prisma = new PrismaClient();

// POST - Pause a scraping job
export async function POST(request: NextRequest, { params }: { params: Promise<{ id: string }> }) {
  try {
    const { id: jobId } = await params;

    // Check if job exists and can be paused
    const job = await prisma.scrapingJob.findUnique({
      where: { id: jobId }
    });

    if (!job) {
      return NextResponse.json({ error: 'Scraping job not found' }, { status: 404 });
    }

    if (job.status !== 'RUNNING') {
      return NextResponse.json({ error: 'Job is not running' }, { status: 400 });
    }

    // Update job status to paused
    const updatedJob = await prisma.scrapingJob.update({
      where: { id: jobId },
      data: {
        status: 'PAUSED'
      }
    });

    return NextResponse.json({
      job: updatedJob,
      message: 'Scraping job paused successfully'
    });
  } catch (error) {
    console.error('Error pausing scraping job:', error);
    return NextResponse.json({ error: 'Failed to pause scraping job' }, { status: 500 });
  }
}
