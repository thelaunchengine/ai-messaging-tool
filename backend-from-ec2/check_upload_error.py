#!/usr/bin/env python3
"""
Check specific upload ID for errors
"""
import os
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    from database.database_manager import DatabaseManager
    
    print("=== CHECKING UPLOAD ID FOR ERRORS ===")
    upload_id = "cmemitmdx0001py5zlqrte41k"
    print(f"Upload ID: {upload_id}")
    print()
    
    db = DatabaseManager()
    
    # Check if file upload exists
    try:
        file_upload = db.get_file_upload_by_id(upload_id)
        if file_upload:
            print(f"✅ File upload found:")
            print(f"  Status: {file_upload.get('status', 'N/A')}")
            print(f"  Total Websites: {file_upload.get('totalWebsites', 'N/A')}")
            print(f"  Processed Websites: {file_upload.get('processedWebsites', 'N/A')}")
        else:
            print(f"❌ File upload NOT found")
    except Exception as e:
        print(f"❌ Error checking file upload: {e}")
    
    print()
    
    # Check websites
    try:
        websites = db.get_websites_by_file_upload_id(upload_id)
        if websites:
            print(f"✅ Found {len(websites)} websites:")
            for i, website in enumerate(websites[:3], 1):
                print(f"  {i}. {website.get('websiteUrl', 'N/A')}")
                print(f"     Status: {website.get('scrapingStatus', 'N/A')}")
                print(f"     Message: {website.get('messageStatus', 'N/A')}")
                print(f"     Contact Form: {website.get('submissionStatus', 'N/A')}")
                print("     ---")
        else:
            print(f"❌ No websites found for this upload ID")
    except Exception as e:
        print(f"❌ Error checking websites: {e}")
    
    print("\n=== CHECK COMPLETE ===")
    
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
