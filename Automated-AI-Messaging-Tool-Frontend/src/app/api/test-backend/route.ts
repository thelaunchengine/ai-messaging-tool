import { NextRequest, NextResponse } from 'next/server';

export async function GET(request: NextRequest) {
  try {
    console.log('=== TEST BACKEND START ===');
    
    const backendUrl = process.env.PYTHON_API_URL || 'http://production-ai-messaging-alb-746376383.us-east-1.elb.amazonaws.com:8001';
    
    console.log('Testing backend health endpoint...');
    const healthResponse = await fetch(`${backendUrl}/health`, {
      method: 'GET',
      timeout: 10000
    });
    
    console.log('Health response status:', healthResponse.status);
    const healthText = await healthResponse.text();
    console.log('Health response text:', healthText);
    
    console.log('=== TEST BACKEND END ===');
    
    return NextResponse.json({
      healthStatus: healthResponse.status,
      healthResponse: healthText,
      backendUrl: backendUrl
    });

  } catch (error) {
    console.error('Test backend error:', error);
    return NextResponse.json({ 
      error: 'Failed to test backend',
      details: error instanceof Error ? error.message : String(error)
    }, { status: 500 });
  }
}
