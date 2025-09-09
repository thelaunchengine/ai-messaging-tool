import { NextRequest, NextResponse } from 'next/server';
import { PrismaClient } from '@prisma/client';
import { getServerSession } from 'next-auth';
import { authOptions } from 'utils/authOptions';
import { promises as fs } from 'fs';
import path from 'path';

const prisma = new PrismaClient();

export async function GET(
  request: NextRequest,
  { params }: { params: Promise<{ id: string }> }
) {
  try {
    const { id } = await params;
    const session = await getServerSession(authOptions);
    
    if (!session?.user?.id) {
      return NextResponse.json({ error: 'Unauthorized' }, { status: 401 });
    }

    const adminUser = await prisma.user.findUnique({
      where: { id: session.user.id },
      select: { role: true }
    });

    if (adminUser?.role !== 'ADMIN' && adminUser?.role !== 'admin') {
      return NextResponse.json({ error: 'Access denied. Admin privileges required.' }, { status: 403 });
    }

    const fileUpload = await prisma.fileUpload.findUnique({
      where: { id },
      include: {
        user: {
          select: {
            name: true,
            email: true
          }
        }
      }
    });

    if (!fileUpload) {
      return NextResponse.json({ error: 'File not found' }, { status: 404 });
    }

    if (!fileUpload.filePath) {
      return NextResponse.json({ error: 'File path not found' }, { status: 404 });
    }

    const filePath = path.join(process.cwd(), fileUpload.filePath);
    
    try {
      const fileBuffer = await fs.readFile(filePath);
      const response = new NextResponse(fileBuffer);
      response.headers.set('Content-Type', 'application/octet-stream');
      response.headers.set('Content-Disposition', `attachment; filename="${fileUpload.originalName}"`);
      
      return response;
    } catch (fileError) {
      console.error('Error reading file:', fileError);
      return NextResponse.json({ error: 'File not found on server' }, { status: 404 });
    }
  } catch (error) {
    console.error('Error downloading file:', error);
    return NextResponse.json({ error: 'Failed to download file' }, { status: 500 });
  }
} 