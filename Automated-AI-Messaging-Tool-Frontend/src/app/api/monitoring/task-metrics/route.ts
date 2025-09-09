import { NextRequest, NextResponse } from 'next/server';
import { getServerSession } from 'next-auth';
import { authOptions } from '../../_lib/auth';

export async function GET(request: NextRequest) {
  try {
    const session = await getServerSession(authOptions);
    
    if (!session?.user?.id) {
      return NextResponse.json({ error: 'Unauthorized' }, { status: 401 });
    }

    // Fetch task metrics from backend
    const backendUrl = process.env.BACKEND_API_URL || 'http://103.215.159.51:8000';
    const response = await fetch(`${backendUrl}/api/monitoring/task-metrics`, {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
      },
    });

    if (!response.ok) {
      // Return empty array if backend is not available
      return NextResponse.json([]);
    }

    const data = await response.json();
    return NextResponse.json(data);
  } catch (error) {
    console.error('Error fetching task metrics:', error);
    
    // Return empty array on error
    return NextResponse.json([]);
  }
} 