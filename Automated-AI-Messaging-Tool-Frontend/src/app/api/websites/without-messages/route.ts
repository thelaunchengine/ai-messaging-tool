import { NextRequest, NextResponse } from 'next/server';
import { getServerSession } from 'next-auth';
import { authOptions } from '../../../../utils/authOptions';

export async function GET(request: NextRequest) {
  try {
    const { searchParams } = new URL(request.url);
    const fileUploadId = searchParams.get('file_upload_id');
    const userId = searchParams.get('user_id');
    const session = await getServerSession(authOptions);
    
    // Build query parameters
    const params = new URLSearchParams();
    if (fileUploadId) params.append('file_upload_id', fileUploadId);
    if (userId) params.append('user_id', userId);
    
    // Call Python backend API
    const response = await fetch(`${process.env.PYTHON_BACKEND_URL || 'http://localhost:8000'}/api/websites/without-messages?${params.toString()}`, {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': session?.accessToken ? `Bearer ${session.accessToken}` : '',
      },
    });

    if (!response.ok) {
      const errorData = await response.json();
      return NextResponse.json(
        { error: errorData.detail || 'Failed to fetch websites without messages' },
        { status: response.status }
      );
    }

    const data = await response.json();
    return NextResponse.json(data);
  } catch (error) {
    console.error('Error fetching websites without messages:', error);
    return NextResponse.json(
      { error: 'Internal server error' },
      { status: 500 }
    );
  }
} 