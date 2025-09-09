#!/usr/bin/env python3

import os
import sys

# Add the current directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    from database.database_manager import DatabaseManager
    
    print("=== DATABASE STATUS CHECK ===")
    print("Upload ID: cmemgg6ya000bpyytazafznr4")
    print()
    
    db = DatabaseManager()
    
    # Check websites table
    print("=== WEBSITES TABLE ===")
    websites = db.get_websites_by_file_upload_id('cmemgg6ya000bpyytazafznr4')
    
    for website in websites:
        print(f"URL: {website['websiteUrl']}")
        print(f"  messageStatus: {website['messageStatus']}")
        print(f"  generatedMessage: {website['generatedMessage'] is not None}")
        print(f"  scrapingStatus: {website['scrapingStatus']}")
        print(f"  companyName: {website['companyName']}")
        print("---")
    
    # Check file uploads table
    print("\n=== FILE UPLOADS TABLE ===")
    try:
        file_upload = db.get_file_upload_by_id('cmemgg6ya000bpyytazafznr4')
        if file_upload:
            print(f"Status: {file_upload.get('status', 'N/A')}")
            print(f"Total Websites: {file_upload.get('totalWebsites', 'N/A')}")
            print(f"Processed Websites: {file_upload.get('processedWebsites', 'N/A')}")
        else:
            print("File upload not found")
    except Exception as e:
        print(f"Error checking file uploads: {e}")
    
    # Check contact inquiries table
    print("\n=== CONTACT INQUIRIES TABLE ===")
    try:
        inquiries = db.get_contact_inquiries_by_file_upload_id('cmemgg6ya000bpyytazafznr4')
        if inquiries:
            for inquiry in inquiries:
                print(f"Website: {inquiry.get('websiteUrl', 'N/A')}")
                print(f"  Status: {inquiry.get('status', 'N/A')}")
                print(f"  Message: {inquiry.get('message', 'N/A')[:100]}...")
                print("---")
        else:
            print("No contact inquiries found")
    except Exception as e:
        print(f"Error checking contact inquiries: {e}")
    
    print("\n=== DATABASE CHECK COMPLETE ===")
    
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
