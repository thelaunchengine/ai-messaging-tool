#!/usr/bin/env python3
"""
AI Workflow Integration - Connects Optimized Scraping with Gemini AI Message Generation
Automatically generates AI messages after websites are scraped in the CSV workflow
"""

import asyncio
import json
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime
import aiohttp
from celery import Celery
from database_manager import DatabaseManager

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AIWorkflowIntegration:
    """Main AI workflow integration class"""
    
    def __init__(self):
        self.gemini_api_key = "AIzaSyANDNgkwSUbg5xXyGYIJIcs2W-REhNjk6I"
        self.gemini_base_url = "https://generativelanguage.googleapis.com/v1beta/models"
        self.model = "gemini-1.5-flash"
        self.db_manager = DatabaseManager()
        
    async def generate_ai_message_for_website(self, website_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate AI message for a single website using Gemini"""
        try:
            # Extract website information
            company_name = website_data.get('company_name', 'Company')
            industry = website_data.get('industry', 'business')
            about_content = website_data.get('about_content', '')
            website_url = website_data.get('website_url', '')
            
            # Create optimized prompt for Gemini
            prompt = self._create_optimized_prompt(company_name, industry, about_content, website_url)
            
            # Call Gemini API
            ai_message = await self._call_gemini_api(prompt)
            
            # Return structured response
            return {
                'website_id': website_data.get('id'),
                'company_name': company_name,
                'industry': industry,
                'ai_message': ai_message,
                'generated_at': datetime.utcnow().isoformat(),
                'status': 'success'
            }
            
        except Exception as e:
            logger.error(f"Error generating AI message for {website_data.get('company_name', 'Unknown')}: {str(e)}")
            return {
                'website_id': website_data.get('id'),
                'company_name': website_data.get('company_name', 'Unknown'),
                'ai_message': f"Error generating message: {str(e)}",
                'generated_at': datetime.utcnow().isoformat(),
                'status': 'error',
                'error': str(e)
            }
    
    def _create_optimized_prompt(self, company_name: str, industry: str, about_content: str, website_url: str) -> str:
        """Create optimized prompt for Gemini AI"""
        
        # Simple, focused prompt for better results
        prompt = f"""
Generate a professional business outreach message for {company_name} in the {industry} industry.

Company: {company_name}
Industry: {industry}
Website: {website_url}

About: {about_content[:500] if about_content else 'Information not available'}

Requirements:
- Professional and friendly tone
- Mention their industry and company specifically
- Keep it under 150 words
- Include a clear call-to-action
- NO placeholders or brackets
- Make it personal and relevant

Generate a complete message that sounds natural and professional.
"""
        return prompt.strip()
    
    async def _call_gemini_api(self, prompt: str) -> str:
        """Call Gemini API with retry logic"""
        max_retries = 3
        retry_delay = 1
        
        for attempt in range(max_retries):
            try:
                async with aiohttp.ClientSession() as session:
                    url = f"{self.gemini_base_url}/{self.model}:generateContent"
                    
                    headers = {
                        "Content-Type": "application/json",
                        "x-goog-api-key": self.gemini_api_key
                    }
                    
                    data = {
                        "contents": [{
                            "parts": [{"text": prompt}]
                        }],
                        "generationConfig": {
                            "temperature": 0.7,
                            "topK": 40,
                            "topP": 0.95,
                            "maxOutputTokens": 500
                        }
                    }
                    
                    async with session.post(url, headers=headers, json=data) as response:
                        if response.status == 200:
                            result = await response.json()
                            ai_message = result['candidates'][0]['content']['parts'][0]['text']
                            return ai_message.strip()
                        elif response.status == 429:  # Rate limit
                            if attempt < max_retries - 1:
                                await asyncio.sleep(retry_delay * (2 ** attempt))
                                continue
                            else:
                                return "Rate limit exceeded. Please try again later."
                        else:
                            error_text = await response.text()
                            logger.error(f"Gemini API error: {response.status} - {error_text}")
                            return f"API error: {response.status}"
                            
            except Exception as e:
                logger.error(f"Attempt {attempt + 1} failed: {str(e)}")
                if attempt < max_retries - 1:
                    await asyncio.sleep(retry_delay)
                else:
                    return f"Failed to generate message after {max_retries} attempts: {str(e)}"
        
        return "Failed to generate AI message"
    
    async def process_bulk_ai_generation(self, file_upload_id: str) -> Dict[str, Any]:
        """Process bulk AI generation for all websites in a file upload"""
        try:
            # Get all websites for this file upload
            websites = await self.db_manager.get_websites_by_file_upload(file_upload_id)
            
            if not websites:
                return {
                    'status': 'error',
                    'message': 'No websites found for this file upload',
                    'file_upload_id': file_upload_id
                }
            
            logger.info(f"Starting bulk AI generation for {len(websites)} websites")
            
            # Process websites in batches for better performance
            batch_size = 10
            results = []
            
            for i in range(0, len(websites), batch_size):
                batch = websites[i:i + batch_size]
                logger.info(f"Processing batch {i//batch_size + 1}: {len(batch)} websites")
                
                # Process batch concurrently
                batch_tasks = [
                    self.generate_ai_message_for_website(website) 
                    for website in batch
                ]
                
                batch_results = await asyncio.gather(*batch_tasks, return_exceptions=True)
                results.extend(batch_results)
                
                # Small delay between batches to avoid overwhelming the API
                if i + batch_size < len(websites):
                    await asyncio.sleep(2)
            
            # Update database with AI messages
            await self._update_database_with_ai_messages(results)
            
            # Generate summary
            success_count = sum(1 for r in results if r.get('status') == 'success')
            error_count = len(results) - success_count
            
            return {
                'status': 'completed',
                'file_upload_id': file_upload_id,
                'total_websites': len(websites),
                'successful_generations': success_count,
                'failed_generations': error_count,
                'results': results,
                'completed_at': datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error in bulk AI generation: {str(e)}")
            return {
                'status': 'error',
                'message': f'Bulk AI generation failed: {str(e)}',
                'file_upload_id': file_upload_id,
                'error': str(e)
            }
    
    async def _update_database_with_ai_messages(self, results: List[Dict[str, Any]]):
        """Update database with generated AI messages"""
        try:
            for result in results:
                if result.get('status') == 'success':
                    await self.db_manager.update_website_ai_message(
                        website_id=result['website_id'],
                        ai_message=result['ai_message'],
                        generated_at=result['generated_at']
                    )
            logger.info(f"Updated database with {len(results)} AI messages")
        except Exception as e:
            logger.error(f"Error updating database: {str(e)}")

# Celery task for background processing
celery_app = Celery('ai_workflow')

@celery_app.task
def generate_ai_messages_bulk_task(file_upload_id: str) -> Dict[str, Any]:
    """Celery task for bulk AI message generation"""
    try:
        integration = AIWorkflowIntegration()
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        result = loop.run_until_complete(
            integration.process_bulk_ai_generation(file_upload_id)
        )
        
        loop.close()
        return result
        
    except Exception as e:
        logger.error(f"Celery task error: {str(e)}")
        return {
            'status': 'error',
            'message': f'Celery task failed: {str(e)}',
            'file_upload_id': file_upload_id,
            'error': str(e)
        }

if __name__ == "__main__":
    # Test the integration
    async def test():
        integration = AIWorkflowIntegration()
        
        # Test data
        test_website = {
            'id': 'test123',
            'company_name': 'Test Company',
            'industry': 'Technology',
            'about_content': 'A leading technology company specializing in AI solutions.',
            'website_url': 'https://testcompany.com'
        }
        
        result = await integration.generate_ai_message_for_website(test_website)
        print("Test Result:", json.dumps(result, indent=2))
    
    asyncio.run(test())
