#!/usr/bin/env python3
import sys
import os

# Add the backend directory to Python path
sys.path.append('/home/xb3353/Automated-AI-Messaging-Tool-Backend')

from database.database_manager import DatabaseManager

def check_upload_status(upload_id):
    try:
        db = DatabaseManager()
        
        # Get the upload
        upload = db.get_file_upload_by_id(upload_id)
        
        if not upload:
            print(f"❌ Upload with ID {upload_id} not found!")
            return
        
        print(f"📁 Upload Details:")
        print(f"   ID: {upload.get('id', 'N/A')}")
        print(f"   Status: {upload.get('status', 'N/A')}")
        print(f"   Created: {upload.get('createdAt', 'N/A')}")
        print(f"   File Path: {upload.get('filePath', 'N/A')}")
        print(f"   Total Records: {upload.get('totalRecords', 'N/A')}")
        print(f"   Processed Records: {upload.get('processedRecords', 'N/A')}")
        print(f"   Contact Forms Processed: {upload.get('contactFormsProcessed', 'N/A')}")
        print(f"   AI Messages Generated: {upload.get('aiMessagesGenerated', 'N/A')}")
        print(f"   Last Updated: {upload.get('updatedAt', 'N/A')}")
        
        # Also check websites for this upload
        print("\n🌐 Websites:")
        websites = db.get_websites_by_file_upload_id(upload_id)
        print(f"   Total Websites: {len(websites)}")
        
        if websites:
            completed_scraping = [w for w in websites if w.get('scrapingStatus') == 'COMPLETED']
            completed_messages = [w for w in websites if w.get('messageStatus') == 'GENERATED']
            
            print(f"   ✅ Scraping completed: {len(completed_scraping)}")
            print(f"   💬 Messages generated: {len(completed_messages)}")
            
            print('\n📋 Sample websites with messages:')
            for i, w in enumerate(websites[:5]):
                print(f'   {i+1}. {w.get("companyName", "Unknown")}')
                print(f'      URL: {w.get("websiteUrl", "N/A")}')
                print(f'      Scraping: {w.get("scrapingStatus", "Unknown")}')
                print(f'      Message: {w.get("messageStatus", "Unknown")}')
                print(f'      Has Message: {"Yes" if w.get("generatedMessage") else "No"}')
                if w.get("generatedMessage"):
                    print(f'      Message Content: {w.get("generatedMessage")[:200]}...')
                print()
            
            if len(websites) > 5:
                print(f'   ... and {len(websites) - 5} more websites')
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    upload_id = "b1eb86d5-6293-4d90-b3f4-d093b42c0c7d"
    check_upload_status(upload_id)
