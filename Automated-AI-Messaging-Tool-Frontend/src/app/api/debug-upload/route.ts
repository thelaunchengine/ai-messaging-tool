import { NextRequest, NextResponse } from 'next/server';

export async function POST(request: NextRequest) {
  try {
    console.log('=== DEBUG UPLOAD START ===');
    
    // Get the request body
    const body = await request.json();
    console.log('Request body:', JSON.stringify(body, null, 2));
    
    if (!body.content) {
      return NextResponse.json({ 
        error: 'Missing required field: content' 
      }, { status: 400 });
    }

    // Convert base64 content back to buffer
    const fileContent = Buffer.from(body.content, 'base64');
    console.log('File content length:', fileContent.length);
    console.log('File content preview:', fileContent.toString('utf8').substring(0, 100));
    
    // Create FormData using native FormData (compatible with Node.js 18+)
    const formData = new FormData();
    
    // Create a Blob from the buffer
    const blob = new Blob([fileContent], { 
      type: body.fileType === 'csv' ? 'text/csv' : 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet' 
    });
    
    // Append the file to FormData
    formData.append('file', blob, body.filename);
    console.log('FormData created with file:', body.filename);
    
    // Forward the request to the backend on port 8001
    const backendUrl = process.env.PYTHON_API_URL || 'http://production-ai-messaging-alb-746376383.us-east-1.elb.amazonaws.com:8001';
    const userId = body.userId || 'cmdi7lqnj0000sbp8h98vwlco';
    
    console.log('Sending to backend:', `${backendUrl}/api/upload-from-frontend?userId=${userId}`);
    
    // Log FormData contents
    console.log('FormData entries:');
    for (const [key, value] of formData.entries()) {
      console.log(`${key}:`, value);
    }
    
    const backendResponse = await fetch(`${backendUrl}/api/upload-from-frontend?userId=${userId}`, {
      method: 'POST',
      body: formData,
      timeout: 30000, // 30 second timeout
      headers: {
        'User-Agent': 'NextJS-Frontend/1.0'
      }
    });

    console.log('Backend response status:', backendResponse.status);
    console.log('Backend response headers:', Object.fromEntries(backendResponse.headers.entries()));

    // Get the response text first to see what we're actually getting
    const responseText = await backendResponse.text();
    console.log('Backend response text:', responseText);
    
    // Try to parse as JSON
    let backendData;
    try {
      backendData = JSON.parse(responseText);
      console.log('Backend response parsed as JSON:', backendData);
    } catch (parseError) {
      console.error('Failed to parse backend response as JSON:', parseError);
      console.log('Response starts with:', responseText.substring(0, 100));
      return NextResponse.json({ 
        error: 'Backend returned non-JSON response',
        details: responseText.substring(0, 200)
      }, { status: 500 });
    }
    
    console.log('=== DEBUG UPLOAD END ===');
    
    // Return the backend response with the same status
    return NextResponse.json(backendData, { status: backendResponse.status });

  } catch (error) {
    console.error('Debug upload error:', error);
    return NextResponse.json({ 
      error: 'Failed to debug upload',
      details: error instanceof Error ? error.message : String(error)
    }, { status: 500 });
  }
}