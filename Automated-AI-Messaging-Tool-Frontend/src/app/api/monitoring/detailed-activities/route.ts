import { NextResponse } from 'next/server';

export async function GET() {
  try {
    const backendUrl = process.env.PYTHON_BACKEND_URL || 'http://103.215.159.51:8000';
    const response = await fetch(`${backendUrl}/api/monitoring/detailed-activities`, {
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
    console.error('Error fetching detailed activities:', error);
    return NextResponse.json([], { status: 500 });
  }
} 