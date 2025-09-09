#!/usr/bin/env python3
"""
Test script to manually trigger contact form submission for upload ID 1dc6d303-a95b-40e5-8882-3e8fb92e9437
This will test the updated functionality that saves form fields and response data
"""
import sys
import os

# Add the backend directory to Python path
sys.path.append('/home/xb3353/Automated-AI-Messaging-Tool-Backend')

from celery_tasks.form_submission_tasks import submit_contact_forms_task
from database.database_manager import DatabaseManager

def main():
    print("🚀 Testing updated contact form submission for upload ID 1dc6d303-a95b-40e5-8882-3e8fb92e9437...")
    
    # Upload ID to test
    upload_id = '1dc6d303-a95b-40e5-8882-3e8fb92e9437'
    
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
            print(f"    Submission Status: {website.get('submissionStatus')}")
            print(f"    Contact Form URL: {website.get('contactFormUrl')}")
            print()
        
        # Get websites with messages for contact form submission
        websites_with_messages = []
        for website in websites:
            if website.get('generatedMessage') and website.get('contactFormUrl'):
                websites_with_messages.append(website)
        
        if not websites_with_messages:
            print("❌ No websites with generated messages and contact forms found")
            return
        
        print(f"🚀 Triggering contact form submission for {len(websites_with_messages)} websites...")
        
        # Call the contact form submission task directly (synchronous execution for testing)
        print("📝 Executing submit_contact_forms_task...")
        result = submit_contact_forms_task(
            websites_with_messages=websites_with_messages,
            user_config=None
        )
        
        print("✅ Task completed!")
        print(f"📊 Result: {result}")
        
        # Check the updated database status
        print("\n🔍 Checking updated database status...")
        updated_websites = db.get_websites_by_file_upload_id(upload_id)
        
        for website in updated_websites:
            print(f"  - {website.get('websiteUrl')}")
            print(f"    Submission Status: {website.get('submissionStatus')}")
            print(f"    Submission Response: {website.get('submissionResponse')[:100] if website.get('submissionResponse') else 'None'}...")
            print(f"    Submission Error: {website.get('submissionError')}")
            print(f"    Submitted Form Fields: {website.get('submittedFormFields')[:100] if website.get('submittedFormFields') else 'None'}...")
            print()
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
