import { NextRequest, NextResponse } from 'next/server';
import { PrismaClient } from '@prisma/client';
import { promises as fs } from 'fs';
import path from 'path';

const prisma = new PrismaClient({
  datasources: {
    db: {
      url: 'postgresql://postgres:AiMessaging2024Secure@production-ai-messaging-db.cmpkwkuqu30h.us-east-1.rds.amazonaws.com:5432/ai_messaging'
    }
  }
});

export async function GET(
  request: NextRequest,
  { params }: { params: Promise<{ id: string }> }
) {
  try {
    const { id } = await params;
    
    // Get user ID from query parameters (passed from frontend)
    const { searchParams } = new URL(request.url);
    const userId = searchParams.get('userId');

    if (!userId) {
      return NextResponse.json({ error: 'User ID is required' }, { status: 400 });
    }

    // Check if user is admin
    const user = await prisma.users.findUnique({
      where: { id: userId },
      select: { role: true }
    });

    if (user?.role !== 'ADMIN' && user?.role !== 'admin') {
      return NextResponse.json({ error: 'Access denied. Admin privileges required.' }, { status: 403 });
    }

    const fileUpload = await prisma.file_uploads.findUnique({
      where: { id },
      include: {
        users: {
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

    if (!fileUpload.filename) {
      return NextResponse.json({ error: 'File path not found' }, { status: 404 });
    }

    // Files are stored on the backend server, not locally
    // Fetch the file from the backend server
    try {
      const backendUrl = process.env.PYTHON_API_URL || 'http://production-ai-messaging-alb-746376383.us-east-1.elb.amazonaws.com:8001'; // ECS Load Balancer URL
      const fileName = fileUpload.filename.split('/').pop(); // Extract filename from path
      const backendFileUrl = `${backendUrl}/api/download-file/${fileName}`;
      
      console.log('Fetching file from backend:', backendFileUrl);
      
      const backendResponse = await fetch(backendFileUrl);
      
      if (!backendResponse.ok) {
        throw new Error(`Backend server responded with status: ${backendResponse.status}`);
      }
      
      const fileBuffer = await backendResponse.arrayBuffer();
      const response = new NextResponse(fileBuffer);
      response.headers.set('Content-Type', 'application/octet-stream');
      response.headers.set('Content-Disposition', `attachment; filename="${fileUpload.originalName}"`);
      
      return response;
    } catch (backendError) {
      console.error('Error fetching file from backend:', backendError);
      
      // Return a helpful error message
      return NextResponse.json({ 
        error: 'Failed to fetch file from backend server',
        details: `Could not retrieve the file "${fileUpload.originalName}" from the backend server. The file may not exist or the backend server may be unavailable.`,
        originalName: fileUpload.originalName,
        backendError: backendError instanceof Error ? backendError.message : String(backendError)
      }, { status: 404 });
    }
  } catch (error) {
    console.error('Error downloading file:', error);
    return NextResponse.json({ error: 'Failed to download file' }, { status: 500 });
  }
} 