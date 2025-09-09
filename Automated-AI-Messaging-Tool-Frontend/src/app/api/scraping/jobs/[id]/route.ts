import { NextRequest, NextResponse } from 'next/server';
import { PrismaClient } from '@prisma/client';

const prisma = new PrismaClient();

// GET - Retrieve specific scraping job details
export async function GET(request: NextRequest, { params }: { params: Promise<{ id: string }> }) {
  try {
    const { id: jobId } = await params;

    const job = await prisma.scrapingJob.findUnique({
      where: { id: jobId },
      include: {
        fileUpload: {
          select: {
            filename: true,
            originalName: true,
            totalWebsites: true,
            processedWebsites: true,
            failedWebsites: true,
            user: {
              select: {
                name: true,
                email: true
              }
            }
          }
        }
      }
    });

    if (!job) {
      return NextResponse.json({ error: 'Scraping job not found' }, { status: 404 });
    }

    return NextResponse.json({ job });
  } catch (error) {
    console.error('Error fetching scraping job:', error);
    return NextResponse.json({ error: 'Failed to fetch scraping job' }, { status: 500 });
  }
}

// PATCH - Update scraping job
export async function PATCH(request: NextRequest, { params }: { params: { id: string } }) {
  try {
    const jobId = params.id;
    const body = await request.json();

    const updatedJob = await prisma.scrapingJob.update({
      where: { id: jobId },
      data: body,
      include: {
        fileUpload: {
          select: {
            filename: true,
            originalName: true,
            user: {
              select: {
                name: true,
                email: true
              }
            }
          }
        }
      }
    });

    return NextResponse.json({
      job: updatedJob,
      message: 'Scraping job updated successfully'
    });
  } catch (error) {
    console.error('Error updating scraping job:', error);
    return NextResponse.json({ error: 'Failed to update scraping job' }, { status: 500 });
  }
}

// DELETE - Delete scraping job
export async function DELETE(request: NextRequest, { params }: { params: { id: string } }) {
  try {
    const jobId = params.id;

    // Check if job exists
    const job = await prisma.scrapingJob.findUnique({
      where: { id: jobId }
    });

    if (!job) {
      return NextResponse.json({ error: 'Scraping job not found' }, { status: 404 });
    }

    // Delete the job
    await prisma.scrapingJob.delete({
      where: { id: jobId }
    });

    return NextResponse.json({
      message: 'Scraping job deleted successfully'
    });
  } catch (error) {
    console.error('Error deleting scraping job:', error);
    return NextResponse.json({ error: 'Failed to delete scraping job' }, { status: 500 });
  }
}
