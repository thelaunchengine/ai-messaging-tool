import { NextRequest, NextResponse } from 'next/server';

// GET - Retrieve scraping configuration
export async function GET(request: NextRequest) {
  try {
    // For now, return default configuration
    // In a real implementation, this would be stored in database or environment variables
    const config = {
      maxConcurrentScrapes: 5,
      requestDelay: 2,
      timeout: 30,
      retryAttempts: 3,
      enableSelenium: true,
      enableProxy: false,
      userAgent: 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    };

    return NextResponse.json({ config });
  } catch (error) {
    console.error('Error fetching scraping config:', error);
    return NextResponse.json({ error: 'Failed to fetch scraping configuration' }, { status: 500 });
  }
}

// POST - Update scraping configuration
export async function POST(request: NextRequest) {
  try {
    const body = await request.json();

    // Validate configuration
    const requiredFields = ['maxConcurrentScrapes', 'requestDelay', 'timeout', 'retryAttempts'];
    for (const field of requiredFields) {
      if (typeof body[field] !== 'number' || body[field] < 0) {
        return NextResponse.json({ error: `Invalid value for ${field}` }, { status: 400 });
      }
    }

    // In a real implementation, this would be saved to database or environment variables
    // For now, we'll just return success
    const config = {
      maxConcurrentScrapes: body.maxConcurrentScrapes,
      requestDelay: body.requestDelay,
      timeout: body.timeout,
      retryAttempts: body.retryAttempts,
      enableSelenium: body.enableSelenium || false,
      enableProxy: body.enableProxy || false,
      userAgent: body.userAgent || 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    };

    return NextResponse.json({
      config,
      message: 'Scraping configuration updated successfully'
    });
  } catch (error) {
    console.error('Error updating scraping config:', error);
    return NextResponse.json({ error: 'Failed to update scraping configuration' }, { status: 500 });
  }
}
