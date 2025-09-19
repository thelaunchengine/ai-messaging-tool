#!/usr/bin/env python3
"""
Script to clear old fallback messages and regenerate proper AI messages
"""

import os
import sys
import logging
from typing import List, Dict, Any

# Add the current directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from database.database_manager import DatabaseManager
from ai.message_generator import GeminiMessageGenerator

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def clear_and_regenerate_messages(file_upload_id: str):
    """Clear old fallback messages and regenerate proper AI messages"""
    
    try:
        # Initialize database manager and AI generator
        db_manager = DatabaseManager()
        ai_generator = GeminiMessageGenerator()
        
        # Get all websites for this upload
        websites = db_manager.get_website_data_by_file_upload(file_upload_id)
        
        if not websites:
            logger.error(f"No websites found for upload {file_upload_id}")
            return
        
        logger.info(f"Found {len(websites)} websites for upload {file_upload_id}")
        
        # Process each website
        for website in websites:
            website_id = website['id']
            website_url = website['websiteUrl']
            company_name = website['companyName']
            industry = website['industry']
            business_type = website['businessType']
            about_us_content = website['aboutUsContent']
            
            logger.info(f"Processing website: {website_url}")
            
            # Skip if no company name or about content (failed scraping)
            if not company_name or not about_us_content:
                logger.info(f"Skipping {website_url} - no company name or about content")
                # Clear the old fallback message
                db_manager.update_website_message(website_id, "", "PENDING")
                continue
            
            # Prepare data for AI generation
            website_data = {
                'id': website_id,
                'website_url': website_url,
                'company_name': company_name,
                'industry': industry,
                'business_type': business_type,
                'about_us_content': about_us_content
            }
            
            try:
                # Generate AI message
                message, confidence = ai_generator.generate_message(website_data, "general")
                
                if message and confidence > 0.0:
                    # Update with new AI-generated message
                    db_manager.update_website_message(website_id, message, "GENERATED")
                    logger.info(f"✅ Generated AI message for {website_url} (confidence: {confidence:.2f})")
                else:
                    # Clear message if AI generation failed
                    db_manager.update_website_message(website_id, "", "FAILED")
                    logger.warning(f"❌ AI generation failed for {website_url}")
                    
            except Exception as e:
                logger.error(f"Error generating message for {website_url}: {e}")
                # Clear message on error
                db_manager.update_website_message(website_id, "", "FAILED")
        
        logger.info(f"✅ Completed message regeneration for upload {file_upload_id}")
        
    except Exception as e:
        logger.error(f"Error in clear_and_regenerate_messages: {e}")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python update_messages.py <file_upload_id>")
        sys.exit(1)
    
    file_upload_id = sys.argv[1]
    clear_and_regenerate_messages(file_upload_id) 