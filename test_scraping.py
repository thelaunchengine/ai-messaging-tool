#!/usr/bin/env python3
"""
Test script to manually trigger scraping for upload ID 7bc31633-3551-428b-97f6-462c8a6053a5
"""
import sys
import os

# Add the backend directory to Python path
sys.path.append('/home/xb3353/Automated-AI-Messaging-Tool-Backend')

from celery_tasks.scraping_tasks import scrape_websites_task
from database.database_manager import DatabaseManager

def main():
    print("🚀 Testing manual scraping for upload ID 7bc31633-3551-428b-97f6-462c8a6053a5...")
    
    # Upload ID to test
    upload_id = '7bc31633-3551-428b-97f6-462c8a6053a5'
    
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
        
        # Get website URLs for scraping
        website_urls = [website.get('websiteUrl') for website in websites]
        user_id = websites[0].get('userId')
        
        print(f"🚀 Triggering scraping task for {len(website_urls)} websites...")
        print(f"📋 URLs: {website_urls}")
        
        # Call the scraping task directly (synchronous execution for testing)
        print("📝 Executing scrape_websites_task...")
        result = scrape_websites_task(
            fileUploadId=upload_id,
            userId=user_id,
            websites=website_urls
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
