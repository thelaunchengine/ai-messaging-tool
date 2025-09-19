import { NextRequest, NextResponse } from 'next/server';
import { PrismaClient } from '@prisma/client';

const prisma = new PrismaClient({
  datasources: {
    db: {
      url: 'postgresql://postgres:AiMessaging2024Secure@production-ai-messaging-db.cmpkwkuqu30h.us-east-1.rds.amazonaws.com:5432/ai_messaging'
    }
  }
});

// GET /api/users - List all users with statistics
export async function GET() {
  try {
    const users = await prisma.users.findMany({
      select: {
        id: true,
        name: true,
        email: true,
        username: true,
        role: true,
        createdAt: true,
        updatedAt: true,
        status: true, // Added status to select
        _count: {
          select: {
            file_uploads: true,
            websites: true
          }
        },
        file_uploads: {
          select: {
            id: true,
            status: true,
            totalWebsites: true,
            processedWebsites: true
          }
        },
        websites: {
          select: {
            id: true,
            messageStatus: true,
            sentMessage: true
          }
        }
      }
    });

    // Transform the data to include calculated statistics
    const usersWithStats = users.map(user => {
      const filesUploaded = user._count.file_uploads;
      const websitesProcessed = user._count.websites;
      const messagesSent = user.websites.filter(w => w.sentMessage).length;
      
      return {
        id: user.id,
        name: user.name || 'Unknown User',
        email: user.email,
        username: user.username,
        role: user.role,
        status: user.status, // Use actual status from database
        filesUploaded,
        websitesProcessed,
        messagesSent,
        subscription: user.role === 'ADMIN' ? 'admin' : 'free', // You can enhance this based on your subscription logic
        registeredDate: user.createdAt,
        lastActive: user.updatedAt
      };
    });

    return NextResponse.json({ users: usersWithStats });
  } catch (error) {
    console.error('Error fetching users:', error);
    return NextResponse.json({ error: 'Failed to fetch users' }, { status: 500 });
  } finally {
    await prisma.$disconnect();
  }
}

// POST /api/users - Create a new user
export async function POST(request: NextRequest) {
  try {
    const data = await request.json();
    const { name, email, password } = data;
    
    if (!name || !email || !password) {
      return NextResponse.json({ error: 'Missing required fields: name, email, password' }, { status: 400 });
    }
    
    // Generate username from email
    const generatedUsername = email.split('@')[0];
    
    // Set default role to USER (not admin)
    const userRole = 'USER';
    
    // Check if email or username already exists
    const existingUser = await prisma.users.findFirst({
      where: {
        OR: [
          { email },
          { username: generatedUsername }
        ]
      }
    });
    
    if (existingUser) {
      return NextResponse.json({ error: 'User with this email already exists' }, { status: 400 });
    }
    
    // Hash password
    const bcrypt = require('bcryptjs');
    const hashedPassword = await bcrypt.hash(password, 12);
    
    const user = await prisma.users.create({
      data: {
        id: `user-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`,
        name,
        email,
        username: generatedUsername,
        password: hashedPassword,
        role: userRole,
        status: 'active', // Set default status
        updatedAt: new Date() // Add required updatedAt field
      },
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
    
    return NextResponse.json({ user }, { status: 201 });
  } catch (error) {
    console.error('Error creating user:', error);
    console.error('Error details:', {
      message: error.message,
      code: error.code,
      meta: error.meta
    });
    return NextResponse.json({ 
      error: 'Failed to create user',
      details: error.message 
    }, { status: 500 });
  } finally {
    await prisma.$disconnect();
  }
} 