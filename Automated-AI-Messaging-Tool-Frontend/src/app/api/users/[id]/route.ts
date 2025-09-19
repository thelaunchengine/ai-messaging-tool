import { NextRequest, NextResponse } from 'next/server';
import { PrismaClient } from '@prisma/client';

const prisma = new PrismaClient({
  datasources: {
    db: {
      url: 'postgresql://postgres:AiMessaging2024Secure@production-ai-messaging-db.cmpkwkuqu30h.us-east-1.rds.amazonaws.com:5432/ai_messaging'
    }
  }
});

export async function GET(request: NextRequest, { params }: { params: Promise<{ id: string }> }) {
  try {
    const { id: userId } = await params;

    // Get user with comprehensive data
    const user = await prisma.users.findUnique({
      where: { id: userId },
      include: {
        file_uploads: {
          select: {
            id: true,
            filename: true,
            originalName: true,
            status: true,
            totalWebsites: true,
            createdAt: true,
            updatedAt: true
          },
          orderBy: { createdAt: 'desc' }
        },
        websites: {
          select: {
            id: true,
            websiteUrl: true,
            contactFormUrl: true,
            hasContactForm: true,
            scrapingStatus: true,
            messageStatus: true,
            createdAt: true
          }
        }
      }
    });

    if (!user) {
      return NextResponse.json({ error: 'User not found' }, { status: 404 });
    }

    // Calculate user statistics
    const totalFiles = user.file_uploads.length;
    const totalWebsites = user.websites.length;
    const processedWebsites = user.websites.filter(w => w.scrapingStatus === 'COMPLETED').length;
    const failedWebsites = user.websites.filter(w => w.scrapingStatus === 'FAILED').length;
    const messagesSent = user.websites.filter(w => w.messageStatus === 'SENT').length;
    const activeFiles = user.file_uploads.filter(f => f.status === 'PROCESSING').length;

    const userStats = {
      id: user.id,
      name: user.name,
      email: user.email,
      username: user.username,
      role: user.role,
      status: user.status,
      createdAt: user.createdAt,
      totalFiles,
      totalWebsites,
      processedWebsites,
      failedWebsites,
      messagesSent,
      activeFiles,
      lastActive: user.updatedAt || user.createdAt
    };

    return NextResponse.json({ user: userStats });
  } catch (error) {
    console.error('Error fetching user:', error);
    return NextResponse.json({ error: 'Failed to fetch user' }, { status: 500 });
  }
}

export async function PUT(request: NextRequest, { params }: { params: Promise<{ id: string }> }) {
  try {
    const { id: userId } = await params;
    const data = await request.json();
    const { name, email, username, password, role, status } = data;
    
    // Check if email is being updated and if it already exists for another user
    if (email) {
      const existingUser = await prisma.users.findFirst({
        where: {
          email: email,
          id: { not: userId } // Exclude current user
        }
      });
      
      if (existingUser) {
        return NextResponse.json({ error: 'Email already exists for another user' }, { status: 400 });
      }
    }
    
    const updateData: any = {};
    if (name) updateData.name = name;
    if (email) updateData.email = email;
    if (username) updateData.username = username;
    if (role) updateData.role = role;
    if (status) updateData.status = status;
    if (password) {
      const bcrypt = require('bcryptjs');
      updateData.password = await bcrypt.hash(password, 12);
    }
    
    const user = await prisma.users.update({
      where: { id: userId },
      data: updateData,
      select: {
        id: true,
        name: true,
        email: true,
        username: true,
        role: true,
        status: true,
        createdAt: true,
        updatedAt: true
      }
    });
    return NextResponse.json({ user });
  } catch (error) {
    console.error('Error updating user:', error);
    return NextResponse.json({ error: 'Failed to update user' }, { status: 500 });
  }
}

export async function DELETE(request: NextRequest, { params }: { params: Promise<{ id: string }> }) {
  try {
    const { id: userId } = await params;
    await prisma.users.delete({ where: { id: userId } });
    return NextResponse.json({ success: true });
  } catch (error) {
    console.error('Error deleting user:', error);
    return NextResponse.json({ error: 'Failed to delete user' }, { status: 500 });
  }
} 