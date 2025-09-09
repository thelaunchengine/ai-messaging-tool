import { NextRequest, NextResponse } from 'next/server';

const BACKEND_URL = process.env.NEXT_PUBLIC_BACKEND_URL || 'http://103.215.159.51:8000';

export async function POST(
  request: NextRequest,
  { params }: { params: Promise<{ fileUploadId: string }> }
) {
  try {
    const { fileUploadId } = await params;
    
    // Get user ID from session if needed
    const userId = request.headers.get('user-id') || 'system';

    // Forward the request to the backend
    const backendResponse = await fetch(`${BACKEND_URL}/api/scraping/trigger-manual/${fileUploadId}`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ user_id: userId }),
    });

    const result = await backendResponse.json();

    if (backendResponse.ok) {
      return NextResponse.json(result);
    } else {
      return NextResponse.json(
        { 
          status: 'error', 
          message: result.detail || 'Failed to trigger scraping' 
        },
        { status: backendResponse.status }
      );
    }
  } catch (error) {
    console.error('Error in trigger-manual API:', error);
    return NextResponse.json(
      { 
        status: 'error', 
        message: 'Internal server error' 
      },
      { status: 500 }
    );
  }
} 