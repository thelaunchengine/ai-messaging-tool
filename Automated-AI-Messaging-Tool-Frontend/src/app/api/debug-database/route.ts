import { NextRequest, NextResponse } from 'next/server';
import { PrismaClient } from '@prisma/client';

const prisma = new PrismaClient({
  datasources: {
    db: {
      url: 'postgresql://postgres:AiMessaging2024Secure@production-ai-messaging-db.cmpkwkuqu30h.us-east-1.rds.amazonaws.com:5432/ai_messaging'
    }
  }
});

export async function GET(request: NextRequest) {
  try {
    // Check total file uploads
    const totalFiles = await prisma.file_uploads.count();
    
    // Check total websites
    const totalWebsites = await prisma.websites.count();
    
    // Check file uploads by user
    const fileUploadsByUser = await prisma.users.findMany({
      select: {
        id: true,
        email: true,
        name: true,
        file_uploads: {
          select: {
            id: true
          }
        }
      }
    });
    
    // Check websites by user
    const websitesByUser = await prisma.users.findMany({
      select: {
        id: true,
        email: true,
        name: true,
        websites: {
          select: {
            id: true
          }
        }
      }
    });
    
    // Format the data
    const fileUploadsData = fileUploadsByUser.map(user => ({
      email: user.email,
      name: user.name,
      fileCount: user.file_uploads.length
    })).sort((a, b) => b.fileCount - a.fileCount);
    
    const websitesData = websitesByUser.map(user => ({
      email: user.email,
      name: user.name,
      websiteCount: user.websites.length
    })).sort((a, b) => b.websiteCount - a.websiteCount);
    
    return NextResponse.json({
      totalFiles,
      totalWebsites,
      fileUploadsByUser: fileUploadsData.slice(0, 10),
      websitesByUser: websitesData.slice(0, 10)
    });
    
  } catch (error) {
    console.error('Database debug error:', error);
    return NextResponse.json(
      { error: 'Failed to fetch database data', details: error.message },
      { status: 500 }
    );
  } finally {
    await prisma.$disconnect();
  }
}
