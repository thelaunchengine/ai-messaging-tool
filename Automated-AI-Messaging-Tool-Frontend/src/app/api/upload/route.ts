
import { NextRequest, NextResponse } from 'next/server';

export async function POST(request: NextRequest) {
  try {
    // Get the request body
    const body = await request.json();
    
    // Since Node.js doesn't have File/Blob constructors, we'll manually construct
    // the multipart form data that the backend expects
    const boundary = '----WebKitFormBoundary' + Math.random().toString(16).substr(2);
    const formData = [];
    
    if (body.content) {
      // Convert base64 content back to buffer
      const fileContent = Buffer.from(body.content, 'base64');
      
      // Create multipart form data manually
      formData.push(
        `--${boundary}`,
        `Content-Disposition: form-data; name="file"; filename="${body.filename}"`,
        `Content-Type: ${body.fileType === 'csv' ? 'text/csv' : 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'}`,
        '',
        fileContent,
        `--${boundary}--`
      );
    }
    
    // Forward the request to the backend on port 8001
    const backendUrl = process.env.PYTHON_API_URL || 'http://103.215.159.51:8001';
    const userId = body.userId || 'cmdi7lqnj0000sbp8h98vwlco'; // Default test user if not provided
    
    const backendResponse = await fetch(`${backendUrl}/api/upload-from-frontend?userId=${userId}`, {
      method: 'POST',
      headers: {
        'Content-Type': `multipart/form-data; boundary=${boundary}`,
      },
      body: formData.join('\r\n')
    });

    // Get the response from backend
    const backendData = await backendResponse.json();
    
    // Return the backend response with the same status
    return NextResponse.json(backendData, { status: backendResponse.status });

  } catch (error) {
    console.error('Upload proxy error:', error);
    return NextResponse.json({ 
      error: 'Failed to forward request to backend',
      details: error.message 
    }, { status: 500 });
  }
}

export async function GET(request: NextRequest) {
  try {
    // Forward the GET request to the backend on port 8001
    const backendUrl = process.env.PYTHON_API_URL || 'http://103.215.159.51:8001';
    const url = new URL(request.url);
    
    const backendResponse = await fetch(`${backendUrl}/api/upload${url.search}`, {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
      }
    });

    // Get the response from backend
    const backendData = await backendResponse.json();
    
    // Return the backend response with the same status
    return NextResponse.json(backendData, { status: backendResponse.status });

  } catch (error) {
    console.error('Upload GET proxy error:', error);
    return NextResponse.json({ 
      error: 'Failed to forward request to backend',
      details: error.message 
    }, { status: 500 });
  }
}
