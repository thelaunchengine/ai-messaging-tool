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
    print('=== ALL CONTACT INQUIRIES ===')
    inquiries = db.get_all_contact_inquiries()
    
    if inquiries:
        print(f'Total inquiries found: {len(inquiries)}')
        for i, inquiry in enumerate(inquiries[:5]):
            print(f'Inquiry {i+1}:')
            print(f'  Website: {inquiry.get("websiteUrl", "N/A")}')
            print(f'  Status: {inquiry.get("status", "N/A")}')
            print(f'  FileUploadId: {inquiry.get("fileUploadId", "N/A")}')
            print('---')
    else:
        print('No contact inquiries found')
    
    # Check if there are inquiries for our specific upload
    print('\n=== CHECKING FOR OUR UPLOAD ID ===')
    our_inquiries = [i for i in inquiries if i.get('fileUploadId') == 'cmemgg6ya000bpyytazafznr4'] if inquiries else []
    
    if our_inquiries:
        print(f'Found {len(our_inquiries)} inquiries for our upload:')
        for inquiry in our_inquiries:
            print(f'  Website: {inquiry.get("websiteUrl", "N/A")}')
            print(f'  Status: {inquiry.get("status", "N/A")}')
            print('---')
    else:
        print('No contact inquiries found for our upload ID')
    
    print('\n=== CONTACT FORM CHECK COMPLETE ===')
    
except Exception as e:
    print(f'Error: {e}')
    import traceback
    traceback.print_exc()
