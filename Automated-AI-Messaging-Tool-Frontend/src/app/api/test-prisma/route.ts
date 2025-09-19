import { NextRequest, NextResponse } from 'next/server';
import { PrismaClient } from '@prisma/client';

export async function GET(request: NextRequest) {
  try {
    console.log('Testing Prisma connection...');
    
    const prisma = new PrismaClient();
    console.log('Prisma client created:', !!prisma);
    
    // Test basic connection
    const result = await prisma.$queryRaw`SELECT 1 as test`;
    console.log('Database query result:', result);
    
    await prisma.$disconnect();
    
    return NextResponse.json({ 
      success: true, 
      message: 'Prisma connection successful',
      result 
    });
  } catch (error) {
    console.error('Prisma connection error:', error);
    return NextResponse.json(
      { 
        success: false, 
        error: error instanceof Error ? error.message : 'Unknown error',
        stack: error instanceof Error ? error.stack : undefined
      },
      { status: 500 }
    );
  }
}
