#!/usr/bin/env python3
"""
Test script to manually trigger contact form submission for recent upload
"""
import sys
import os

# Add the backend directory to Python path
sys.path.append('/home/xb3353/Automated-AI-Messaging-Tool-Backend')

from celery_tasks.form_submission_tasks import submit_contact_forms_task
from database.database_manager import DatabaseManager

def main():
    print("🚀 Testing contact form submission for recent upload...")
    
    # Upload ID to test
    upload_id = '4fa544ae-84c5-4981-be2e-f46766fefff1'
    
    try:
        # Get websites with generated messages for this upload
        db = DatabaseManager()
        websites = db.get_websites_by_file_upload_id(upload_id)
        
        if not websites:
            print(f"❌ No websites found for upload ID: {upload_id}")
            return
        
        # Filter websites that have generated messages
        websites_with_messages = [
            website for website in websites 
            if website.get('messageStatus') == 'GENERATED' and website.get('generatedMessage')
        ]
        
        if not websites_with_messages:
            print(f"❌ No websites with generated messages found for upload ID: {upload_id}")
            return
        
        print(f"✅ Found {len(websites_with_messages)} websites with generated messages:")
        for website in websites_with_messages:
            print(f"  - {website.get('websiteUrl')} (ID: {website.get('id')})")
            print(f"    Contact Form: {website.get('contactFormUrl')}")
            print(f"    Message Status: {website.get('messageStatus')}")
            print(f"    Submission Status: {website.get('submissionStatus')}")
            print()
        
        # Trigger the contact form submission task
        print("🚀 Triggering contact form submission task...")
        
        # Prepare the data in the format expected by the task
        websites_data = []
        for website in websites_with_messages:
            website_data = {
                'id': website.get('id'),
                'websiteUrl': website.get('websiteUrl'),
                'contactFormUrl': website.get('contactFormUrl'),
                'generatedMessage': website.get('generatedMessage'),
                'companyName': website.get('companyName'),
                'businessType': website.get('businessType'),
                'industry': website.get('industry')
            }
            websites_data.append(website_data)
        
        # Call the task directly (synchronous execution for testing)
        print("📝 Executing submit_contact_forms_task...")
        result = submit_contact_forms_task(websites_with_messages=websites_data)
        
        print("✅ Task completed!")
        print(f"📊 Result: {result}")
        
        # Check the updated database status
        print("\n🔍 Checking updated database status...")
        updated_websites = db.get_websites_by_file_upload_id(upload_id)
        
        for website in updated_websites:
            if website.get('messageStatus') == 'GENERATED':
                print(f"  - {website.get('websiteUrl')}")
                print(f"    Submission Status: {website.get('submissionStatus')}")
                print(f"    Submission Error: {website.get('submissionError')}")
                print()
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
