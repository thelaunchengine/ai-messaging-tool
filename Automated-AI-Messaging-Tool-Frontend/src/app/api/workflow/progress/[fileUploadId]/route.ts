import { NextRequest, NextResponse } from 'next/server';

export async function GET(
  request: NextRequest,
  { params }: { params: Promise<{ fileUploadId: string }> }
) {
  try {
    const { fileUploadId } = await params;
    
    const backendUrl = process.env.PYTHON_API_URL || 'http://103.215.159.51:8001';
    
    const response = await fetch(`${backendUrl}/api/workflow/progress/${fileUploadId}`, {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
        'Cache-Control': 'no-cache',
        'Pragma': 'no-cache'
      },
    });

    if (!response.ok) {
      const errorText = await response.text();
      console.error('Workflow progress fetch failed:', response.status, errorText);
      return NextResponse.json(
        { error: `Failed to fetch workflow progress: ${response.status}` },
        { status: response.status }
      );
    }

    const data = await response.json();
    return NextResponse.json(data);
    
  } catch (error) {
    console.error('Error fetching workflow progress:', error);
    return NextResponse.json(
      { error: 'Internal server error' },
      { status: 500 }
    );
  }
} 