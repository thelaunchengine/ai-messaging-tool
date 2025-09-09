#!/usr/bin/env python3
"""
Test script to manually trigger AI message generation for upload ID 1dc6d303-a95b-40e5-8882-3e8fb92e9437
"""
import sys
import os

# Add the backend directory to Python path
sys.path.append('/home/xb3353/Automated-AI-Messaging-Tool-Backend')

from celery_tasks.scraping_tasks import generate_messages_task
from database.database_manager import DatabaseManager

def main():
    print("🚀 Testing AI message generation for upload ID 1dc6d303-a95b-40e5-8882-3e8fb92e9437...")
    
    # Upload ID to test
    upload_id = '1dc6d303-a95b-40e5-8882-3e8fb92e9437'
    
    try:
        # Get websites with completed scraping for this upload
        db = DatabaseManager()
        websites = db.get_websites_by_file_upload_id(upload_id)
        
        if not websites:
            print(f"❌ No websites found for upload ID: {upload_id}")
            return
        
        # Filter websites that have completed scraping
        websites_with_completed_scraping = [
            website for website in websites 
            if website.get('scrapingStatus') == 'COMPLETED'
        ]
        
        if not websites_with_completed_scraping:
            print(f"❌ No websites with completed scraping found for upload ID: {upload_id}")
            return
        
        print(f"✅ Found {len(websites_with_completed_scraping)} websites with completed scraping:")
        for website in websites_with_completed_scraping:
            print(f"  - {website.get('websiteUrl')} (ID: {website.get('id')})")
            print(f"    Scraping Status: {website.get('scrapingStatus')}")
            print(f"    Message Status: {website.get('messageStatus')}")
            print(f"    Contact Form URL: {website.get('contactFormUrl')}")
            print()
        
        # Trigger the AI message generation task
        print("🚀 Triggering AI message generation task...")
        
        # Call the task directly (synchronous execution for testing)
        print("📝 Executing generate_messages_task...")
        result = generate_messages_task(
            website_data=websites_with_completed_scraping,
            message_type="general",
            fileUploadId=upload_id,
            userId=websites_with_completed_scraping[0].get('userId')
        )
        
        print("✅ Task completed!")
        print(f"📊 Result: {result}")
        
        # Check the updated database status
        print("\n🔍 Checking updated database status...")
        updated_websites = db.get_websites_by_file_upload_id(upload_id)
        
        for website in updated_websites:
            print(f"  - {website.get('websiteUrl')}")
            print(f"    Message Status: {website.get('messageStatus')}")
            print(f"    Generated Message: {website.get('generatedMessage')[:100] if website.get('generatedMessage') else 'None'}...")
            print()
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
