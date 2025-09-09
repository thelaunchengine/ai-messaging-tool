import { NextRequest, NextResponse } from 'next/server';
import { PrismaClient } from '@prisma/client';

const prisma = new PrismaClient();

// GET - Retrieve all scraping jobs
export async function GET(request: NextRequest) {
  try {
    const { searchParams } = new URL(request.url);
    const status = searchParams.get('status');
    const limit = parseInt(searchParams.get('limit') || '50');
    const page = parseInt(searchParams.get('page') || '1');
    const skip = (page - 1) * limit;

    // Build where clause
    const where: any = {};
    if (status) {
      where.status = status;
    }

    // Get scraping jobs with pagination
    const jobs = await prisma.scrapingJob.findMany({
      where,
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
      },
      orderBy: {
        createdAt: 'desc'
      },
      skip,
      take: limit
    });

    // Get total count
    const total = await prisma.scrapingJob.count({ where });

    return NextResponse.json({
      jobs,
      pagination: {
        page,
        limit,
        total,
        pages: Math.ceil(total / limit)
      }
    });
  } catch (error) {
    console.error('Error fetching scraping jobs:', error);
    return NextResponse.json({ error: 'Failed to fetch scraping jobs' }, { status: 500 });
  }
}

// POST - Create a new scraping job
export async function POST(request: NextRequest) {
  try {
    const body = await request.json();
    const { fileUploadId, totalWebsites } = body;

    if (!fileUploadId || !totalWebsites) {
      return NextResponse.json({ error: 'fileUploadId and totalWebsites are required' }, { status: 400 });
    }

    // Verify file upload exists
    const fileUpload = await prisma.fileUpload.findUnique({
      where: { id: fileUploadId }
    });

    if (!fileUpload) {
      return NextResponse.json({ error: 'File upload not found' }, { status: 404 });
    }

    // Create scraping job
    const scrapingJob = await prisma.scrapingJob.create({
      data: {
        fileUploadId,
        totalWebsites,
        status: 'PENDING',
        processedWebsites: 0,
        failedWebsites: 0
      },
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
      job: scrapingJob,
      message: 'Scraping job created successfully'
    });
  } catch (error) {
    console.error('Error creating scraping job:', error);
    return NextResponse.json({ error: 'Failed to create scraping job' }, { status: 500 });
  }
}
