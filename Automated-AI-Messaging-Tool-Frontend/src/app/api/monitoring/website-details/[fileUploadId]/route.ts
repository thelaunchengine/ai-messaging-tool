import { NextRequest, NextResponse } from 'next/server';

export async function GET(
  request: NextRequest,
  { params }: { params: { fileUploadId: string } }
) {
  try {
    const { fileUploadId } = params;
    const backendUrl = process.env.PYTHON_BACKEND_URL || 'http://103.215.159.51:8000';
    
    const response = await fetch(`${backendUrl}/api/monitoring/website-details/${fileUploadId}`, {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
        'Cache-Control': 'no-cache',
        'Pragma': 'no-cache',
      },
    });

    if (!response.ok) {
      throw new Error(`Backend responded with status: ${response.status}`);
    }

    const data = await response.json();
    return NextResponse.json(data);
  } catch (error) {
    console.error('Error fetching website details:', error);
    return NextResponse.json(
      { error: 'Failed to fetch website details' }, 
      { status: 500 }
    );
  }
} 