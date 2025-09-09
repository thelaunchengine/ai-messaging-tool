import { NextRequest, NextResponse } from 'next/server';
import { getServerSession } from 'next-auth';
import { authOptions } from '../../../../utils/authOptions';

// Gemini API configuration
const GEMINI_API_KEY = 'AIzaSyANDNgkwSUbg5xXyGYIJIcs2W-REhNjk6I';
const GEMINI_API_URL = 'https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent';

export async function POST(request: NextRequest) {
  try {
    const body = await request.json();
    const session = await getServerSession(authOptions);
    
    // Extract website_data from the request body
    const websiteData = body.website_data || [];
    const messageType = body.message_type || 'general';
    const customPrompt = body.custom_prompt || '';
    
    console.log('🚀 Generating AI messages directly with Gemini for:', websiteData.length, 'websites');
    console.log('📊 Message type:', messageType);
    console.log('📝 Custom prompt:', customPrompt);
    
    const results = [];
    
    for (const website of websiteData) {
      try {
        // Extract website information
        const companyName = website.companyName || website.company_name || 'Unknown Company';
        const industry = website.industry || 'Unknown Industry';
        const businessType = website.businessType || website.business_type || 'Unknown Business Type';
        const aboutUsContent = website.aboutUsContent || website.about_us_content || '';
        const websiteUrl = website.websiteUrl || website.website_url || '';
        
        console.log(`🤖 Processing: ${companyName} - ${industry} - ${businessType}`);
        
        // Create the AI prompt
        let prompt = `You are writing a professional business outreach message. Write a complete, ready-to-send message with NO placeholders or brackets.

Company: ${companyName}
Industry: ${industry}
Business Type: ${businessType}
About Us: ${aboutUsContent ? aboutUsContent.substring(0, 300) + '...' : 'Information not available'}

Message Type: ${messageType}`;

        if (customPrompt) {
          prompt += `\n\nCustom Requirements: ${customPrompt}`;
        }

        prompt += `\n\nWrite a professional business outreach message that:
1. Uses ${companyName} as the actual company name (not [Company Name])
2. References their ${industry} industry and ${businessType} business type
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
          console.error(`❌ Gemini API error for ${companyName}:`, errorData);
          
          results.push({
            website_id: website.id,
            url: websiteUrl,
            message: null,
            error: `Gemini API error: ${errorData.error?.message || 'Unknown error'}`,
            success: false,
            is_ai_generated: false
          });
          continue;
        }

        const geminiData = await geminiResponse.json();
        console.log(`✅ Gemini API response for ${companyName}:`, geminiData);
        
        // Extract the generated message
        const generatedMessage = geminiData.candidates?.[0]?.content?.parts?.[0]?.text;
        
        if (generatedMessage && generatedMessage.trim()) {
          results.push({
            website_id: website.id,
            url: websiteUrl,
            message: generatedMessage.trim(),
            confidence: 0.9, // High confidence for direct API calls
            success: true,
            is_ai_generated: true,
            ai_model: 'gemini-1.5-flash'
          });
          console.log(`🎉 Successfully generated AI message for ${companyName}`);
        } else {
          results.push({
            website_id: website.id,
            url: websiteUrl,
            message: null,
            error: 'Gemini API returned empty message',
            success: false,
            is_ai_generated: false
          });
          console.log(`⚠️ Empty message from Gemini for ${companyName}`);
        }
        
      } catch (error) {
        console.error(`💥 Error processing website ${website.id}:`, error);
        
        results.push({
          website_id: website.id,
          url: website.websiteUrl || website.website_url || '',
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
    
    return NextResponse.json({
      success: true,
      messages: results,
      total_websites: websiteData.length,
      successful_count: successfulCount,
      failed_count: failedCount,
      ai_model: 'gemini-1.5-flash',
      generated_directly: true
    });
    
  } catch (error) {
    console.error('💥 Error in direct Gemini AI generation:', error);
    
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