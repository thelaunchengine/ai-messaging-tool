import { NextRequest, NextResponse } from 'next/server';

export async function GET(request: NextRequest, { params }: { params: Promise<{ id: string }> }) {
  try {
    const { id: fileUploadId } = await params;
    const { searchParams } = new URL(request.url);
    
    // Build backend API URL with query parameters
    const backendUrl = new URL(`http://103.215.159.51:8001/api/upload/${fileUploadId}/websites`);
    
    // Add query parameters
    searchParams.forEach((value, key) => {
      backendUrl.searchParams.append(key, value);
    });
    
    // Call backend API
    const response = await fetch(backendUrl.toString(), {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
      },
    });
    
    if (!response.ok) {
      throw new Error(`Backend API responded with status: ${response.status}`);
    }
    
    const data = await response.json();
    
    return NextResponse.json(data);
  } catch (error) {
    console.error('Error fetching websites from backend:', error);
    return NextResponse.json({ error: 'Failed to fetch websites' }, { status: 500 });
  }
}
