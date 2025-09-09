#!/usr/bin/env python3
"""
Test script to manually trigger AI message generation for upload ID ad18b573-e776-4f54-ba65-288dfbdedd3a
This will test if the auto-triggering is working after the fixes
"""
import sys
import os

# Add the backend directory to Python path
sys.path.append('/home/xb3353/Automated-AI-Messaging-Tool-Backend')

from celery_tasks.scraping_tasks import generate_messages_task
from database.database_manager import DatabaseManager

def main():
    print("🚀 Testing manual AI message generation for upload ID ad18b573-e776-4f54-ba65-288dfbdedd3a...")
    
    # Upload ID to test
    upload_id = 'ad18b573-e776-4f54-ba65-288dfbdedd3a'
    
    try:
        # Get websites for this upload
        db = DatabaseManager()
        websites = db.get_websites_by_file_upload_id(upload_id)
        
        if not websites:
            print(f"❌ No websites found for upload ID: {upload_id}")
            return
        
        print(f"✅ Found {len(websites)} websites:")
        for website in websites:
            print(f"  - {website.get('websiteUrl')} (ID: {website.get('id')})")
            print(f"    Scraping Status: {website.get('scrapingStatus')}")
            print(f"    Message Status: {website.get('messageStatus')}")
            print()
        
        # Get websites with generated messages for AI generation
        websites_with_messages = []
        for website in websites:
            if website.get('generatedMessage'):
                websites_with_messages.append(website)
        
        if not websites_with_messages:
            print("❌ No websites with generated messages found")
            return
        
        print(f"🚀 Triggering AI message generation for {len(websites_with_messages)} websites...")
        
        # Call the AI message generation task directly (synchronous execution for testing)
        print("📝 Executing generate_messages_task...")
        result = generate_messages_task(
            website_data=websites_with_messages,
            message_type="general",
            fileUploadId=upload_id,
            userId=websites[0].get('userId')
        )
        
        print("✅ Task completed!")
        print(f"📊 Result: {result}")
        
        # Check the updated database status
        print("\n🔍 Checking updated database status...")
        updated_websites = db.get_websites_by_file_upload_id(upload_id)
        
        for website in updated_websites:
            print(f"  - {website.get('websiteUrl')}")
            print(f"    Scraping Status: {website.get('scrapingStatus')}")
            print(f"    Message Status: {website.get('messageStatus')}")
            print()
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
