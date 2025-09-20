import { NextRequest, NextResponse } from 'next/server';

export async function GET(request: NextRequest) {
  try {
    const { searchParams } = new URL(request.url);
    const userId = searchParams.get('userId');
    
    console.log('Test download API called with userId:', userId);
    
    return NextResponse.json({ 
      success: true, 
      message: 'Test download API working',
      userId: userId 
    });
  } catch (error) {
    console.error('Test download error:', error);
    return NextResponse.json({ error: 'Test failed' }, { status: 500 });
  }
}
