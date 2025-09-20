import { NextRequest, NextResponse } from 'next/server';

export async function POST(request: NextRequest) {
  try {
    console.log('Test upload endpoint called');
    
    // Get the request body
    const body = await request.json();
    console.log('Request body:', body);
    
    if (!body.content) {
      return NextResponse.json({ 
        error: 'Missing required field: content' 
      }, { status: 400 });
    }

    // Convert base64 content back to buffer
    const fileContent = Buffer.from(body.content, 'base64');
    console.log('File content length:', fileContent.length);
    console.log('File content preview:', fileContent.toString('utf8').substring(0, 100));
    
    // Test the backend directly
    const backendUrl = process.env.PYTHON_API_URL || 'http://98.85.16.204:8001';
    const userId = body.userId || 'cmdi7lqnj0000sbp8h98vwlco';
    
    // Create a simple test file
    const testContent = fileContent.toString('utf8');
    const testFile = new Blob([testContent], { type: 'text/csv' });
    
    const formData = new FormData();
    formData.append('file', testFile, body.filename);
    
    console.log('Sending to backend:', `${backendUrl}/api/upload-from-frontend?userId=${userId}`);
    
    const backendResponse = await fetch(`${backendUrl}/api/upload-from-frontend?userId=${userId}`, {
      method: 'POST',
      body: formData
    });

    console.log('Backend response status:', backendResponse.status);
    console.log('Backend response headers:', Object.fromEntries(backendResponse.headers.entries()));

    // Get the response from backend
    const backendData = await backendResponse.json();
    console.log('Backend response data:', backendData);
    
    // Return the backend response with the same status
    return NextResponse.json(backendData, { status: backendResponse.status });

  } catch (error) {
    console.error('Test upload error:', error);
    return NextResponse.json({ 
      error: 'Failed to test upload',
      details: error instanceof Error ? error.message : String(error)
    }, { status: 500 });
  }
}
