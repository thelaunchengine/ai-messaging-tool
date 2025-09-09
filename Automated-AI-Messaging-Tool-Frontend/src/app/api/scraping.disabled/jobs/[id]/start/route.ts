import { NextRequest, NextResponse } from 'next/server';
import { PrismaClient } from '@prisma/client';

const prisma = new PrismaClient();

// POST - Start a scraping job
export async function POST(request: NextRequest, { params }: { params: Promise<{ id: string }> }) {
  try {
    const { id: jobId } = await params;

    // Check if job exists and can be started
    const job = await prisma.scrapingJob.findUnique({
      where: { id: jobId }
    });

    if (!job) {
      return NextResponse.json({ error: 'Scraping job not found' }, { status: 404 });
    }

    if (job.status === 'RUNNING') {
      return NextResponse.json({ error: 'Job is already running' }, { status: 400 });
    }

    if (job.status === 'COMPLETED') {
      return NextResponse.json({ error: 'Job is already completed' }, { status: 400 });
    }

    // Update job status to running
    const updatedJob = await prisma.scrapingJob.update({
      where: { id: jobId },
      data: {
        status: 'RUNNING',
        startedAt: new Date()
      }
    });

    // TODO: Trigger the actual scraping process via Celery
    // This would typically involve calling the Python backend
    // For now, we'll just update the status

    return NextResponse.json({
      job: updatedJob,
      message: 'Scraping job started successfully'
    });
  } catch (error) {
    console.error('Error starting scraping job:', error);
    return NextResponse.json({ error: 'Failed to start scraping job' }, { status: 500 });
  }
}
