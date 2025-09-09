import { NextRequest, NextResponse } from 'next/server';
import { PrismaClient } from '@prisma/client';

const prisma = new PrismaClient();

export async function GET(request: NextRequest, { params }: { params: Promise<{ id: string }> }) {
  const { id: fileUploadId } = await params;
  try {
    const fileUpload = await prisma.fileUpload.findUnique({
      where: { id: fileUploadId },
      include: {
        chunks: {
          orderBy: { chunkNumber: 'asc' }
        }
      }
    });
    if (!fileUpload) {
      return NextResponse.json({ error: 'File upload not found' }, { status: 404 });
    }
    return NextResponse.json({ fileUpload });
  } catch (error) {
    return NextResponse.json({ error: 'Failed to fetch file upload.', details: error?.message || error }, { status: 500 });
  }
}

export async function DELETE(request: NextRequest, { params }: { params: Promise<{ id: string }> }) {
  const { id: fileUploadId } = await params;
  try {
    // Delete related websites
    await prisma.website.deleteMany({ where: { fileUploadId } });
    // Delete related processing chunks
    await prisma.processingChunk.deleteMany({ where: { fileUploadId } });
    // Delete related scraping jobs
    await prisma.scrapingJob.deleteMany({ where: { fileUploadId } });
    // Delete the file upload record
    await prisma.fileUpload.delete({ where: { id: fileUploadId } });
    return NextResponse.json({ message: 'File upload and related data deleted successfully.' });
  } catch (error) {
    return NextResponse.json({ error: 'Failed to delete file upload.', details: error?.message || error }, { status: 500 });
  }
}
