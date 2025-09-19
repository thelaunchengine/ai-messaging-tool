#!/usr/bin/env python3
from database.database_manager import DatabaseManager

def check_upload(upload_id):
    db = DatabaseManager()
    target = db.get_file_upload_by_id(upload_id)
    print('Upload:', target if target else 'Not found')
    
    if target:
        websites = db.get_websites_by_file_upload_id(upload_id)
        print(f'Websites found: {len(websites)}')
        for i, w in enumerate(websites[:5]):
            print(f'Website {i+1}: {w.get("websiteUrl", "No URL")} - Status: {w.get("scrapingStatus", "Unknown")} - Message: {w.get("messageStatus", "Unknown")}')

if __name__ == "__main__":
    check_upload('2a8436b7-e60a-490a-ac9d-e64fde33a258')
