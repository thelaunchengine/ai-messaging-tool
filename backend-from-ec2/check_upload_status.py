#!/usr/bin/env python3
"""
Upload Status Investigation Script
Checks what happened to a specific upload ID
"""

import sys
import os
import logging
from datetime import datetime

# Add the project root to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def investigate_upload(upload_id: str):
    """Investigate what happened to a specific upload"""
    
    try:
        logger.info(f"🔍 Investigating upload ID: {upload_id}")
        
        from database.database_manager import DatabaseManager
        db_manager = DatabaseManager()
        
        # Check 1: File upload status
        logger.info("📁 Checking file upload status...")
        db_manager.cursor.execute("""
            SELECT id, "userId", status, "totalWebsites", "processedWebsites", 
                   "failedWebsites", "createdAt", "updatedAt"
            FROM file_uploads 
            WHERE id = %s
        """, (upload_id,))
        
        upload_result = db_manager.cursor.fetchone()
        if upload_result:
            columns = [desc[0] for desc in db_manager.cursor.description]
            upload_data = dict(zip(columns, upload_result))
            
            print(f"✅ File Upload Found:")
            print(f"   ID: {upload_data['id']}")
            print(f"   User ID: {upload_data['userId']}")
            print(f"   Status: {upload_data['status']}")
            print(f"   Total Websites: {upload_data['totalWebsites']}")
            print(f"   Processed: {upload_data['processedWebsites']}")
            print(f"   Failed: {upload_data['failedWebsites']}")
            print(f"   Created: {upload_data['createdAt']}")
            print(f"   Updated: {upload_data['updatedAt']}")
        else:
            print(f"❌ File upload {upload_id} not found!")
            return
        
        # Check 2: Websites from this upload
        logger.info("🌐 Checking websites from this upload...")
        websites = db_manager.get_websites_by_file_upload_id(upload_id)
        
        if websites:
            print(f"\n✅ Found {len(websites)} websites:")
            for i, website in enumerate(websites[:5], 1):  # Show first 5
                print(f"   {i}. {website.get('companyName', 'Unknown')}")
                print(f"      URL: {website.get('websiteUrl', 'N/A')}")
                print(f"      Scraping Status: {website.get('scrapingStatus', 'N/A')}")
                print(f"      Message Status: {website.get('messageStatus', 'N/A')}")
                print(f"      Has Contact Form: {website.get('hasContactForm', 'N/A')}")
                print(f"      Submission Status: {website.get('submissionStatus', 'N/A')}")
                print()
            
            if len(websites) > 5:
                print(f"   ... and {len(websites) - 5} more websites")
        else:
            print(f"❌ No websites found for upload {upload_id}")
        
        # Check 3: Scraping jobs
        logger.info("🔧 Checking scraping jobs...")
        db_manager.cursor.execute("""
            SELECT id, status, "totalWebsites", "processedWebsites", "failedWebsites",
                   "createdAt", "updatedAt"
            FROM scraping_jobs 
            WHERE "fileUploadId" = %s
            ORDER BY "createdAt" DESC
        """, (upload_id,))
        
        jobs = db_manager.cursor.fetchall()
        if jobs:
            print(f"\n🔧 Found {len(jobs)} scraping job(s):")
            for job in jobs:
                columns = [desc[0] for desc in db_manager.cursor.description]
                job_data = dict(zip(columns, job))
                print(f"   Job ID: {job_data['id']}")
                print(f"   Status: {job_data['status']}")
                print(f"   Total: {job_data['totalWebsites']}, Processed: {job_data['processedWebsites']}, Failed: {job_data['failedWebsites']}")
                print(f"   Created: {job_data['createdAt']}")
                print()
        else:
            print(f"❌ No scraping jobs found for upload {upload_id}")
        
        # Check 4: Contact form submissions
        logger.info("📝 Checking contact form submissions...")
        submissions = db_manager.get_submissions_by_file_upload(upload_id)
        
        if submissions:
            print(f"\n📝 Found {len(submissions)} contact form submission(s):")
            for submission in submissions:
                print(f"   Submission ID: {submission['id']}")
                print(f"   Website: {submission['companyName']}")
                print(f"   Status: {submission['submission_status']}")
                print(f"   Method: {submission['submission_method']}")
                print(f"   Created: {submission['created_at']}")
                print()
        else:
            print(f"❌ No contact form submissions found for upload {upload_id}")
        
        # Check 5: Recent activity logs
        logger.info("📋 Checking recent activity...")
        db_manager.cursor.execute("""
            SELECT "websiteUrl", "scrapingStatus", "messageStatus", "updatedAt"
            FROM websites 
            WHERE "fileUploadId" = %s
            ORDER BY "updatedAt" DESC
            LIMIT 10
        """, (upload_id,))
        
        recent_activity = db_manager.cursor.fetchall()
        if recent_activity:
            print(f"\n📋 Recent Activity (Last 10 updates):")
            for activity in recent_activity:
                print(f"   {activity[0]} - Scraping: {activity[1]}, Message: {activity[2]}, Updated: {activity[3]}")
        
        # Summary
        print(f"\n🔍 Investigation Summary for Upload {upload_id}:")
        print(f"   📁 File Upload: {'✅ Found' if upload_result else '❌ Not Found'}")
        print(f"   🌐 Websites: {'✅ Found' if websites else '❌ Not Found'}")
        print(f"   🔧 Scraping Jobs: {'✅ Found' if jobs else '❌ Not Found'}")
        print(f"   📝 Contact Form Submissions: {'✅ Found' if submissions else '❌ Not Found'}")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Error investigating upload: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Main investigation function"""
    
    upload_id = "cmelge11r000qpy2h0aahoxmk"
    
    print(f"🔍 Upload Investigation: {upload_id}")
    print("=" * 60)
    print(f"📅 Investigation Time: {datetime.now()}")
    print()
    
    if investigate_upload(upload_id):
        print("\n✅ Investigation completed successfully!")
    else:
        print("\n❌ Investigation failed!")

if __name__ == "__main__":
    main()
