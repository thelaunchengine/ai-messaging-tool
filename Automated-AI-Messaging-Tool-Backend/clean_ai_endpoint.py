from fastapi import FastAPI, HTTPException
from typing import List, Dict, Any
import logging
import sys
import os

# Add the backend directory to Python path
sys.path.append('/home/xb3353/Automated-AI-Messaging-Tool-Backend')

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="AI Message Generator with Gemini", version="1.0.0")

@app.get("/health")
async def health_check():
    return {"status": "healthy", "message": "AI Message Generator with Gemini is running"}

@app.post("/api/ai/generate-real-messages")
async def generate_real_ai_messages(website_data: List[Dict[str, Any]]):
    """Generate real AI messages using Gemini API"""
    try:
        if not website_data:
            raise HTTPException(status_code=400, detail="Website data is required")
        
        logger.info(f"Generating real AI messages for {len(website_data)} websites using Gemini")
        
        # Import the AI components
        try:
            from ai.message_generator import GeminiMessageGenerator
            from database.database_manager import DatabaseManager
            logger.info("Successfully imported AI components")
        except ImportError as e:
            logger.error(f"Failed to import AI components: {e}")
            raise HTTPException(status_code=500, detail=f"AI components not available: {e}")
        
        # Initialize AI generator
        db_manager = DatabaseManager()
        ai_generator = GeminiMessageGenerator(db_manager=db_manager)
        logger.info("Initialized GeminiMessageGenerator")
        
        results = []
        for website in website_data:
            try:
                # Extract website information
                company_name = website.get('companyName') or website.get('company_name', 'Unknown Company')
                industry = website.get('industry', 'Unknown Industry')
                business_type = website.get('businessType') or website.get('business_type', 'Unknown Business Type')
                about_us_content = website.get('aboutUsContent') or website.get('about_us_content', '')
                
                logger.info(f"Processing website: {company_name} - {industry} - {business_type}")
                
                # Create a standardized website object for AI generation
                website_obj = {
                    'company_name': company_name,
                    'industry': industry,
                    'business_type': business_type,
                    'about_us_content': about_us_content,
                    'website_url': website.get('websiteUrl') or website.get('website_url', '')
                }
                
                # Generate message using real AI
                result = ai_generator.hybrid_message_generation(
                    website_obj, 
                    message_type="general"
                )
                
                # Extract message and confidence from result
                message = result.get('message', '')
                confidence = result.get('confidence_score', 0.0)
                
                if message and message.strip():
                    results.append({
                        'website_id': website.get('id'),
                        'url': website_obj['website_url'],
                        'message': message,
                        'confidence': confidence,
                        'success': True,
                        'is_ai_generated': True
                    })
                    logger.info(f"Successfully generated AI message for {company_name}")
                else:
                    results.append({
                        'website_id': website.get('id'),
                        'url': website_obj['website_url'],
                        'message': None,
                        'error': 'AI generation returned empty message',
                        'success': False,
                        'is_ai_generated': False
                    })
                    logger.warning(f"AI generation returned empty message for {company_name}")
                    
            except Exception as e:
                logger.error(f"Error generating AI message for website {website.get('id', 'unknown')}: {e}")
                results.append({
                    'website_id': website.get('id'),
                    'url': website.get('websiteUrl') or website.get('website_url', ''),
                    'message': None,
                    'error': str(e),
                    'success': False,
                    'is_ai_generated': False
                })
        
        # Count successful generations
        successful_count = len([r for r in results if r['success']])
        failed_count = len([r for r in results if not r['success']])
        
        logger.info(f"Real AI message generation completed. Success: {successful_count}, Failed: {failed_count}")
        
        return {
            "success": True,
            "messages": results,
            "total_websites": len(website_data),
            "successful_count": successful_count,
            "failed_count": failed_count,
            "ai_model": "gemini-1.5-flash"
        }
        
    except Exception as e:
        logger.error(f"Error in generate_real_ai_messages: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8002)
