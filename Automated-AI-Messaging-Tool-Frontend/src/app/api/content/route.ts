import { NextRequest, NextResponse } from 'next/server';
import { PrismaClient } from '@prisma/client';
import { z } from 'zod';

const prisma = new PrismaClient();

// Validation schema for content creation/update
const contentSchema = z.object({
  type: z.enum(['about', 'privacy', 'terms', 'help', 'cookies']),
  title: z.string().min(1, 'Title is required'),
  content: z.string().min(1, 'Content is required'),
  status: z.enum(['DRAFT', 'PUBLISHED']).default('DRAFT'),
  createdBy: z.string().optional()
});

// GET - Retrieve content by type (returns latest published version)
export async function GET(request: NextRequest) {
  try {
    const { searchParams } = new URL(request.url);
    const type = searchParams.get('type');
    const version = searchParams.get('version');

    if (!type) {
      return NextResponse.json({ error: 'Content type is required' }, { status: 400 });
    }

    // Validate content type
    const validTypes = ['about', 'privacy', 'terms', 'help', 'cookies'];
    if (!validTypes.includes(type)) {
      return NextResponse.json({ error: 'Invalid content type' }, { status: 400 });
    }

    let content;

    if (version) {
      // Get specific version
      content = await prisma.staticContent.findUnique({
        where: {
          type_version: {
            type,
            version: parseInt(version)
          }
        }
      });
    } else {
      // Get latest published version, fallback to latest draft
      content = await prisma.staticContent.findFirst({
        where: {
          type,
          status: 'PUBLISHED'
        },
        orderBy: {
          version: 'desc'
        }
      });

      // If no published version, get latest draft
      if (!content) {
        content = await prisma.staticContent.findFirst({
          where: {
            type
          },
          orderBy: {
            version: 'desc'
          }
        });
      }
    }

    if (!content) {
      return NextResponse.json({ error: 'Content not found' }, { status: 404 });
    }

    return NextResponse.json({
      success: true,
      content
    });
  } catch (error) {
    console.error('Error fetching content:', error);
    return NextResponse.json({ error: 'Internal server error' }, { status: 500 });
  }
}

// POST - Create new content version
export async function POST(request: NextRequest) {
  try {
    const body = await request.json();
    const validatedData = contentSchema.parse(body);

    // Get the latest version for this content type
    const latestContent = await prisma.staticContent.findFirst({
      where: {
        type: validatedData.type
      },
      orderBy: {
        version: 'desc'
      }
    });

    const newVersion = latestContent ? latestContent.version + 1 : 1;

    // Create new content version
    const content = await prisma.staticContent.create({
      data: {
        type: validatedData.type,
        title: validatedData.title,
        content: validatedData.content,
        status: validatedData.status,
        version: newVersion,
        createdBy: validatedData.createdBy || 'admin'
      }
    });

    return NextResponse.json(
      {
        success: true,
        message: 'Content created successfully',
        content
      },
      { status: 201 }
    );
  } catch (error) {
    if (error instanceof z.ZodError) {
      return NextResponse.json(
        {
          error: 'Validation error',
          details: error.errors
        },
        { status: 400 }
      );
    }

    console.error('Error creating content:', error);
    return NextResponse.json({ error: 'Internal server error' }, { status: 500 });
  }
}
