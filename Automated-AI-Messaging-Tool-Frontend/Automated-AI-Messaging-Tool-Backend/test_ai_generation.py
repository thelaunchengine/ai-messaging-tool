#!/usr/bin/env python3

from celery_tasks.scraping_tasks import generate_messages_task
from database.database_manager import DatabaseManager

def test_ai_generation():
    print("=== TESTING AI MESSAGE GENERATION WITH NEW API KEY ===")
    
    db = DatabaseManager()
    websites_without_messages = db.get_websites_without_messages()
    
    print(f"Total websites waiting for AI messages: {len(websites_without_messages)}")
    
    if websites_without_messages:
        # Get the first website's file upload ID
        test_website = websites_without_messages[0]
        file_upload_id = test_website.get('fileUploadId')
        
        print(f"\nTesting with FileUploadID: {file_upload_id}")
        print(f"Website ID: {test_website.get('id')}")
        
        try:
            # Submit the task
            result = generate_messages_task.delay(file_upload_id)
            print(f"✅ Task submitted successfully!")
            print(f"Task ID: {result.id}")
            print(f"Status: {result.status}")
            
            return result.id
            
        except Exception as e:
            print(f"❌ Error submitting task: {e}")
            return None
    else:
        print("No websites waiting for AI messages")
        return None

if __name__ == "__main__":
    test_ai_generation()
