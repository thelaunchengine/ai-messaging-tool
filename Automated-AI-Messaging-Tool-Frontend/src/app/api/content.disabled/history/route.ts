import { NextRequest, NextResponse } from 'next/server';
import { PrismaClient } from '@prisma/client';

const prisma = new PrismaClient();

// GET - Retrieve content version history
export async function GET(request: NextRequest) {
  try {
    const { searchParams } = new URL(request.url);
    const type = searchParams.get('type');

    if (!type) {
      return NextResponse.json({ error: 'Content type is required' }, { status: 400 });
    }

    // Validate content type
    const validTypes = ['about', 'privacy', 'terms', 'help', 'cookies'];
    if (!validTypes.includes(type)) {
      return NextResponse.json({ error: 'Invalid content type' }, { status: 400 });
    }

    // Get all versions for this content type
    const contentHistory = await prisma.staticContent.findMany({
      where: {
        type
      },
      orderBy: {
        version: 'desc'
      },
      select: {
        id: true,
        version: true,
        title: true,
        status: true,
        createdAt: true,
        updatedAt: true,
        createdBy: true
      }
    });

    return NextResponse.json({
      success: true,
      contentHistory
    });
  } catch (error) {
    console.error('Error fetching content history:', error);
    return NextResponse.json({ error: 'Internal server error' }, { status: 500 });
  }
}
