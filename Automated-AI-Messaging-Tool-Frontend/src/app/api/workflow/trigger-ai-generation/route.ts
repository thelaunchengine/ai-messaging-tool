import { NextRequest, NextResponse } from 'next/server';
import { getServerSession } from 'next-auth';
import { authOptions } from '../../../../utils/authOptions';

// Gemini API configuration
const GEMINI_API_KEY = 'AIzaSyANDNgkwSUbg5xXyGYIJIcs2W-REhNjk6I';
const GEMINI_API_URL = 'https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent';

export async function POST(request: NextRequest) {
  try {
    const body = await request.json();
    const { fileUploadId, messageType = 'general', customPrompt = '', aiModel = 'gemini' } = body;
    const session = await getServerSession(authOptions);
    
    if (!fileUploadId) {
      return NextResponse.json({ error: 'File upload ID is required' }, { status: 400 });
    }

    console.log('🚀 Triggering AI message generation for file upload:', fileUploadId);
    console.log('📊 Message type:', messageType);
    console.log('📝 Custom prompt:', customPrompt);

    // Get all websites for this file upload from the database
    const websitesResponse = await fetch(`${process.env.NEXTAUTH_URL || 'http://localhost:3000'}/api/websites/by-file-upload/${fileUploadId}`);
    
    if (!websitesResponse.ok) {
      return NextResponse.json(
        { error: 'Failed to fetch websites for file upload' },
        { status: 500 }
      );
    }

    const websitesData = await websitesResponse.json();
    const websites = websitesData.websites || [];
    
    if (websites.length === 0) {
      return NextResponse.json(
        { error: 'No websites found for this file upload' },
        { status: 404 }
      );
    }

    // Filter websites that have been successfully scraped
    const scrapedWebsites = websites.filter((w: any) => w.scrapingStatus === 'COMPLETED');
    
    if (scrapedWebsites.length === 0) {
      return NextResponse.json(
        { error: 'No successfully scraped websites found. Please wait for scraping to complete.' },
        { status: 400 }
      );
    }

    console.log(`📈 Found ${scrapedWebsites.length} scraped websites out of ${websites.length} total`);

    // Prepare website data for AI generation
    const websiteData = scrapedWebsites.map((website: any) => ({
      id: website.id,
      companyName: website.companyName || 'Unknown Company',
      industry: website.industry || 'Unknown Industry',
      businessType: website.businessType || 'Unknown Business Type',
      aboutUsContent: website.aboutUsContent || '',
      websiteUrl: website.websiteUrl || ''
    }));

    // Generate AI messages using our direct Gemini API
    const results = [];
    
    for (const website of websiteData) {
      try {
        console.log(`🤖 Processing: ${website.companyName} - ${website.industry} - ${website.businessType}`);
        
        // Create the AI prompt
        let prompt = `You are writing a professional business outreach message. Write a complete, ready-to-send message with NO placeholders or brackets.

Company: ${website.companyName}
Industry: ${website.industry}
Business Type: ${website.businessType}
About Us: ${website.aboutUsContent ? website.aboutUsContent.substring(0, 300) + '...' : 'Information not available'}

Message Type: ${messageType}`;

        if (customPrompt) {
          prompt += `\n\nCustom Requirements: ${customPrompt}`;
        }

        prompt += `\n\nWrite a professional business outreach message that:
1. Uses ${website.companyName} as the actual company name (not [Company Name])
2. References their ${website.industry} industry and ${website.businessType} business type
3. Is professional, courteous, and outreach-focused
4. Encourages scheduling appointments or meetings to discuss services
5. Has a clear call to action focused on collaboration opportunities
6. Is 3-4 paragraphs maximum
7. Is COMPLETE and ready to send - NO [Your Name], NO [Your Company], NO placeholders
8. Sounds like a real business professional writing to them
9. Emphasizes the value of meeting to discuss potential partnerships or services
10. Maintains a tone that encourages response and engagement

IMPORTANT: Keep the message under 500 characters total. Focus on being concise yet professional.

Write the entire message as if you are actually sending it. Make up realistic details for the sender but keep it professional and business-focused.`;

        // Call Gemini API directly
        const geminiResponse = await fetch(`${GEMINI_API_URL}?key=${GEMINI_API_KEY}`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            contents: [{
              parts: [{
                text: prompt
              }]
            }],
            generationConfig: {
              temperature: 0.7,
              topK: 40,
              topP: 0.95,
              maxOutputTokens: 800,
            }
          })
        });

        if (!geminiResponse.ok) {
          const errorData = await geminiResponse.json();
          console.error(`❌ Gemini API error for ${website.companyName}:`, errorData);
          
          results.push({
            website_id: website.id,
            url: website.websiteUrl,
            message: null,
            error: `Gemini API error: ${errorData.error?.message || 'Unknown error'}`,
            success: false,
            is_ai_generated: false
          });
          continue;
        }

        const geminiData = await geminiResponse.json();
        console.log(`✅ Gemini API response for ${website.companyName}:`, geminiData);
        
        // Extract the generated message
        const generatedMessage = geminiData.candidates?.[0]?.content?.parts?.[0]?.text;
        
        if (generatedMessage && generatedMessage.trim()) {
          results.push({
            website_id: website.id,
            url: website.websiteUrl,
            message: generatedMessage.trim(),
            confidence: 0.9,
            success: true,
            is_ai_generated: true,
            ai_model: 'gemini-1.5-flash'
          });
          console.log(`🎉 Successfully generated AI message for ${website.companyName}`);
        } else {
          results.push({
            website_id: website.id,
            url: website.websiteUrl,
            message: null,
            error: 'Gemini API returned empty message',
            success: false,
            is_ai_generated: false
          });
          console.log(`⚠️ Empty message from Gemini for ${website.companyName}`);
        }
        
      } catch (error) {
        console.error(`💥 Error processing website ${website.id}:`, error);
        
        results.push({
          website_id: website.id,
          url: website.websiteUrl,
          message: null,
          error: error instanceof Error ? error.message : 'Unknown error',
          success: false,
          is_ai_generated: false
        });
      }
    }

    // Count successful generations
    const successfulCount = results.filter(r => r.success).length;
    const failedCount = results.filter(r => !r.success).length;
    
    console.log(`🎯 AI generation completed. Success: ${successfulCount}, Failed: ${failedCount}`);

    // Store the generated messages in the database (optional)
    // This would require updating the website records with the generated messages
    
    return NextResponse.json({
      success: true,
      task_id: `workflow_${fileUploadId}_${Date.now()}`,
      status: 'completed',
      message: `AI message generation completed for ${scrapedWebsites.length} websites. Success: ${successfulCount}, Failed: ${failedCount}`,
      results: results,
      total_websites: scrapedWebsites.length,
      successful_count: successfulCount,
      failed_count: failedCount,
      ai_model: 'gemini-1.5-flash',
      generated_directly: true
    });
    
  } catch (error) {
    console.error('💥 Error in workflow AI generation:', error);
    
    return NextResponse.json(
      { 
        error: 'Internal server error', 
        details: error instanceof Error ? error.message : 'Unknown error',
        stack: error instanceof Error ? error.stack : undefined
      },
      { status: 500 }
    );
  }
}
