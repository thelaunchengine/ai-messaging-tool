#!/usr/bin/env python3

from database.database_manager import DatabaseManager

def check_uploads():
    db = DatabaseManager()
    
    print('=== RECENT FILE UPLOADS ===')
    uploads = db.get_all_file_uploads()
    print(f'Total uploads: {len(uploads)}')
    
    # Sort by creation date (newest first)
    recent_uploads = sorted(uploads, key=lambda x: x['createdAt'], reverse=True)[:10]
    
    for i, upload in enumerate(recent_uploads):
        print(f'\n{i+1}. Upload ID: {upload["id"]}')
        print(f'   Filename: {upload["filename"]}')
        print(f'   Status: {upload["status"]}')
        print(f'   Created: {upload["createdAt"]}')
        print(f'   Websites: {upload["processedWebsites"]}/{upload["totalWebsites"]}')
        print(f'   Failed: {upload["failedWebsites"]}')
    
    print('\n=== WEBSITES WITH MESSAGES ===')
    websites_with_messages = db.get_websites_with_messages()
    print(f'Websites with messages: {len(websites_with_messages)}')
    
    print('\n=== WEBSITES WITHOUT MESSAGES ===')
    websites_without_messages = db.get_websites_without_messages()
    print(f'Websites without messages: {len(websites_without_messages)}')
    
    if websites_without_messages:
        print('\nSample websites without messages:')
        for i, website in enumerate(websites_without_messages[:5]):
            print(f'  {i+1}. ID: {website.get("id")}, URL: {website.get("url")}, FileUploadID: {website.get("fileUploadId")}')

if __name__ == '__main__':
    check_uploads()
