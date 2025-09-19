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
    const { searchParams } = new URL(request.url);
    const userId = searchParams.get('userId');
    
    if (!userId) {
      return NextResponse.json({ error: 'User ID is required' }, { status: 400 });
    }

    console.log('=== DEBUG USER START ===');
    console.log('Looking for user ID:', userId);

    // First, let's check if the user exists
    const user = await prisma.users.findUnique({
      where: { id: userId },
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

    console.log('User found:', user);

    if (!user) {
      // Let's check what users exist
      const allUsers = await prisma.users.findMany({
        select: {
          id: true,
          name: true,
          email: true,
          username: true
        },
        take: 5
      });
      
      console.log('Available users:', allUsers);
      
      return NextResponse.json({ 
        error: 'User not found',
        searchedId: userId,
        availableUsers: allUsers
      }, { status: 404 });
    }

    console.log('=== DEBUG USER END ===');
    
    return NextResponse.json({ 
      success: true,
      user: user
    });

  } catch (error) {
    console.error('Debug user error:', error);
    return NextResponse.json({ 
      error: 'Failed to debug user',
      details: error instanceof Error ? error.message : String(error)
    }, { status: 500 });
  } finally {
    await prisma.$disconnect();
  }
}
