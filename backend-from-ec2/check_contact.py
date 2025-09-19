#!/usr/bin/env python3

import os
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    from database.database_manager import DatabaseManager
    
    print('=== CONTACT FORM SUBMISSION STATUS ===')
    print('Upload ID: cmemgg6ya000bpyytazafznr4')
    print()
    
    db = DatabaseManager()
    
    # Check contact inquiries table
    print('=== CONTACT INQUIRIES TABLE ===')
    inquiries = db.get_contact_inquiries_by_file_upload_id('cmemgg6ya000bpyytazafznr4')
    
    if inquiries:
        for inquiry in inquiries:
            print(f'Website: {inquiry.get("websiteUrl", "N/A")}')
            print(f'  Status: {inquiry.get("status", "N/A")}')
            print(f'  Message: {inquiry.get("message", "N/A")[:100]}...')
            print('---')
    else:
        print('No contact inquiries found')
    
    print('\n=== CHECKING WEBSITES FOR CONTACT FORM STATUS ===')
    websites = db.get_websites_by_file_upload_id('cmemgg6ya000bpyytazafznr4')
    
    for website in websites:
        print(f'Website: {website["websiteUrl"]}')
        print(f'  messageStatus: {website["messageStatus"]}')
        print(f'  generatedMessage: {website["generatedMessage"] is not None}')
        print(f'  scrapingStatus: {website["scrapingStatus"]}')
        # Check if there are additional contact form fields
        if hasattr(website, 'submissionStatus'):
            print(f'  submissionStatus: {website.get("submissionStatus", "N/A")}')
        print('---')
    
    print('\n=== CONTACT FORM CHECK COMPLETE ===')
    
except Exception as e:
    print(f'Error: {e}')
    import traceback
    traceback.print_exc()
