#!/usr/bin/env python3
"""
Debug why AI message generation is not being triggered
"""
import os
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    from database.database_manager import DatabaseManager
    
    print("=== DEBUGGING AI MESSAGE TRIGGER ===")
    upload_id = "cmeml6uyh0005py12ma2gu6ki"
    print(f"Upload ID: {upload_id}")
    print()
    
    db = DatabaseManager()
    
    # Check file upload status
    print("=== FILE UPLOAD STATUS ===")
    try:
        file_upload = db.get_file_upload_by_id(upload_id)
        if file_upload:
            print(f"✅ File upload found:")
            print(f"  Status: {file_upload.get('status', 'N/A')}")
            print(f"  Total Websites: {file_upload.get('totalWebsites', 'N/A')}")
            print(f"  Processed Websites: {file_upload.get('processedWebsites', 'N/A')}")
            print(f"  Created: {file_upload.get('createdAt', 'N/A')}")
            print(f"  Updated: {file_upload.get('updatedAt', 'N/A')}")
        else:
            print(f"❌ File upload NOT found")
    except Exception as e:
        print(f"❌ Error checking file upload: {e}")
    
    print()
    
    # Check if scraping jobs exist
    print("=== SCRAPING JOBS STATUS ===")
    try:
        connection = db.get_connection()
        cursor = connection.cursor()
        
        cursor.execute("""
            SELECT id, status, "createdAt", "updatedAt"
            FROM scraping_jobs 
            WHERE "fileUploadId" = %s
            ORDER BY "createdAt" DESC
        """, (upload_id,))
        
        scraping_jobs = cursor.fetchall()
        if scraping_jobs:
            print(f"✅ Found {len(scraping_jobs)} scraping jobs:")
            for job in scraping_jobs:
                print(f"  Job ID: {job[0]}")
                print(f"    Status: {job[1]}")
                print(f"    Created: {job[2]}")
                print(f"    Updated: {job[3]}")
                print("    ---")
        else:
            print(f"❌ No scraping jobs found for this upload")
        
        cursor.close()
        connection.close()
    except Exception as e:
        print(f"❌ Error checking scraping jobs: {e}")
    
    print()
    
    # Check websites status
    print("=== WEBSITES STATUS ===")
    try:
        websites = db.get_websites_by_file_upload_id(upload_id)
        if websites:
            print(f"✅ Found {len(websites)} websites:")
            print()
            
            for i, website in enumerate(websites, 1):
                print(f"🌐 Website {i}: {website.get('websiteUrl', 'N/A')}")
                print(f"     Company: {website.get('companyName', 'N/A')}")
                print(f"     Industry: {website.get('industry', 'N/A')}")
                print(f"     Scraping: {website.get('scrapingStatus', 'N/A')}")
                print(f"     Message: {website.get('messageStatus', 'N/A')}")
                print(f"     Contact Form: {website.get('submissionStatus', 'N/A')}")
                print("     ---")
        else:
            print(f"❌ No websites found for this upload ID")
    except Exception as e:
        print(f"❌ Error checking websites: {e}")
    
    print()
    
    # Check if there are any active Celery tasks
    print("=== CELERY TASK STATUS ===")
    try:
        # This would require Redis connection to check active tasks
        print("ℹ️  Celery task status requires Redis connection")
        print("   Check the Celery worker logs for task execution")
    except Exception as e:
        print(f"❌ Error checking Celery tasks: {e}")
    
    print()
    
    # Check recent logs for this upload
    print("=== RECENT LOGS CHECK ===")
    print("ℹ️  Check the following log files for this upload ID:")
    print("   - logs/celery-worker-*.log")
    print("   - logs/fastapi-*.log")
    print("   - Look for: cmeml6uyh0005py12ma2gu6ki")
    
    print("\n=== DEBUG COMPLETE ===")
    print("🔍 NEXT STEPS:")
    print("1. Check if scraping jobs were created")
    print("2. Check Celery worker logs for task execution")
    print("3. Verify the workflow integration is working")
    
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
