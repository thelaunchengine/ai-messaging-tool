import { NextRequest, NextResponse } from 'next/server';
import { getServerSession } from 'next-auth';
import { authOptions } from '../../../utils/authOptions';
import { prisma } from .*/lib/prisma.js;

export async function POST(request: NextRequest) {
  try {
    // Get user session
    const session = await getServerSession(authOptions);
    
    if (!session?.user?.id) {
      return NextResponse.json({ error: 'User ID is required' }, { status: 401 });
    }

    const body = await request.json();
    const { filename, originalName, fileSize, fileType, content } = body;

    // Validate required fields
    if (!filename || !originalName || !fileSize || !fileType || !content) {
      return NextResponse.json({ 
        error: 'Validation error',
        details: [
          { code: 'invalid_type', expected: 'string', received: typeof filename, path: ['filename'], message: 'Required' },
          { code: 'invalid_type', expected: 'string', received: typeof originalName, path: ['originalName'], message: 'Required' },
          { code: 'invalid_type', expected: 'number', received: typeof fileSize, path: ['fileSize'], message: 'Required' },
          { expected: "'csv' | 'xlsx'", received: typeof fileType, code: 'invalid_type', path: ['fileType'], message: 'Required' },
          { code: 'invalid_type', expected: 'string', received: typeof content, path: ['content'], message: 'Required' }
        ]
      }, { status: 400 });
    }

    // Create file upload record
    const fileUpload = await prisma.fileUpload.create({
      data: {
        filename,
        originalName,
        fileSize,
        fileType,
        content,
        userId: session.user.id,
        status: 'PENDING'
      }
    });

    return NextResponse.json({
      message: 'File uploaded successfully',
      fileUploadId: fileUpload.id,
      filename: fileUpload.filename,
      status: fileUpload.status
    });

  } catch (error) {
    console.error('Upload error:', error);
    return NextResponse.json({ error: 'Internal server error' }, { status: 500 });
  }
}

export async function GET(request: NextRequest) {
  try {
    // Get user session
    const session = await getServerSession(authOptions);
    
    if (!session?.user?.id) {
      return NextResponse.json({ error: 'User ID is required' }, { status: 401 });
    }

    // Return user's uploads
    const uploads = await prisma.fileUpload.findMany({
      where: { userId: session.user.id },
      orderBy: { createdAt: 'desc' }
    });

    return NextResponse.json(uploads);

  } catch (error) {
    console.error('Get uploads error:', error);
    return NextResponse.json({ error: 'Internal server error' }, { status: 500 });
  }
}
