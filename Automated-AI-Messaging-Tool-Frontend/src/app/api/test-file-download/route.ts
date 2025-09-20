import { NextRequest, NextResponse } from 'next/server';
import { promises as fs } from 'fs';
import path from 'path';

export async function GET(request: NextRequest) {
  try {
    // Test with a file that actually exists
    const filePath = '/home/ubuntu/ai-messaging-tool/Automated-AI-Messaging-Tool-Backend/uploads/test-download.csv';
    
    console.log('Testing download with file:', filePath);
    
    try {
      const fileBuffer = await fs.readFile(filePath);
      const response = new NextResponse(fileBuffer);
      response.headers.set('Content-Type', 'text/csv');
      response.headers.set('Content-Disposition', 'attachment; filename="test-download.csv"');
      
      console.log('File downloaded successfully, size:', fileBuffer.length);
      return response;
    } catch (fileError) {
      console.error('Error reading file:', fileError);
      return NextResponse.json({ 
        error: 'File not found on server',
        filePath: filePath,
        details: fileError instanceof Error ? fileError.message : String(fileError)
      }, { status: 404 });
    }
  } catch (error) {
    console.error('Error in test download:', error);
    return NextResponse.json({ 
      error: 'Failed to download file',
      details: error instanceof Error ? error.message : String(error)
    }, { status: 500 });
  }
}
