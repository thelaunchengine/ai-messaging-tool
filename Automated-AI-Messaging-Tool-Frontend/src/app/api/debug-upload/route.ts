import { NextRequest, NextResponse } from 'next/server';

export async function POST(request: NextRequest) {
  try {
    console.log('Debug upload API called');
    
    // Test 1: Basic request parsing
    const body = await request.json();
    console.log('Request body parsed successfully:', { filename: body.filename, fileSize: body.fileSize });
    
    // Test 2: Import auth
    console.log('Testing auth import...');
    const { getServerSession } = await import('next-auth');
    const { authOptions } = await import('../_lib/auth');
    console.log('Auth imports successful');
    
    // Test 3: Test Prisma connection
    console.log('Testing Prisma connection...');
    const { prisma } = await import('../_lib/prisma');
    const userCount = await prisma.users.count();
    console.log('Prisma connection successful, user count:', userCount);
    
    return NextResponse.json({ 
      message: 'All tests passed',
      userCount,
      body: { filename: body.filename, fileSize: body.fileSize }
    });
    
  } catch (error) {
    console.error('Debug upload API error:', error);
    return NextResponse.json({ 
      error: 'Debug test failed', 
      details: error instanceof Error ? error.message : 'Unknown error',
      stack: error instanceof Error ? error.stack : undefined
    }, { status: 500 });
  }
}
