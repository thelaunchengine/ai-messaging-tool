#!/usr/bin/env python3
"""
System Status Check Script
Checks for stuck uploads and system issues
"""

import sys
import os
import logging
from datetime import datetime, timedelta

# Add the project root to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def check_system_status():
    """Check overall system status"""
    
    try:
        logger.info("🔍 Checking system status...")
        
        from database.database_manager import DatabaseManager
        db_manager = DatabaseManager()
        
        # Check 1: All uploads regardless of date
        logger.info("📁 Checking all uploads in database...")
        db_manager.cursor.execute("""
            SELECT id, "userId", status, "totalWebsites", "processedWebsites", 
                   "failedWebsites", "createdAt", "updatedAt"
            FROM file_uploads 
            ORDER BY "createdAt" DESC
            LIMIT 20
        """)
        
        all_uploads = db_manager.cursor.fetchall()
        if all_uploads:
            print(f"📊 Database contains {len(all_uploads)} total uploads:")
            for upload in all_uploads:
                columns = [desc[0] for desc in db_manager.cursor.description]
                upload_data = dict(zip(columns, upload))
                print(f"   📁 {upload_data['id']}")
                print(f"      Status: {upload_data['status']}")
                print(f"      Created: {upload_data['createdAt']}")
                print(f"      Updated: {upload_data['updatedAt']}")
                print()
        else:
            print("❌ No uploads found in database at all!")
        
        # Check 2: Stuck uploads (PROCESSING for more than 1 hour)
        logger.info("🔍 Checking for stuck uploads...")
        db_manager.cursor.execute("""
            SELECT id, "userId", status, "totalWebsites", "processedWebsites", 
                   "failedWebsites", "createdAt", "updatedAt"
            FROM file_uploads 
            WHERE status = 'PROCESSING' 
            AND "updatedAt" < NOW() - INTERVAL '1 hour'
            ORDER BY "updatedAt" ASC
        """)
        
        stuck_uploads = db_manager.cursor.fetchall()
        if stuck_uploads:
            print(f"⚠️ Found {len(stuck_uploads)} potentially stuck upload(s):")
            for upload in stuck_uploads:
                columns = [desc[0] for desc in db_manager.cursor.description]
                upload_data = dict(zip(columns, upload))
                print(f"   📁 {upload_data['id']}")
                print(f"      Stuck since: {upload_data['updatedAt']}")
                print(f"      Progress: {upload_data['processedWebsites']}/{upload_data['totalWebsites']}")
                print()
        else:
            print("✅ No stuck uploads found")
        
        # Check 3: Scraping jobs status
        logger.info("🔧 Checking scraping jobs...")
        db_manager.cursor.execute("""
            SELECT id, "fileUploadId", status, "totalWebsites", "processedWebsites", 
                   "failedWebsites", "createdAt", "updatedAt"
            FROM scraping_jobs 
            ORDER BY "createdAt" DESC
            LIMIT 10
        """)
        
        all_jobs = db_manager.cursor.fetchall()
        if all_jobs:
            print(f"🔧 Found {len(all_jobs)} scraping job(s):")
            for job in all_jobs:
                columns = [desc[0] for desc in db_manager.cursor.description]
                job_data = dict(zip(columns, job))
                print(f"   Job ID: {job_data['id']}")
                print(f"   Upload ID: {job_data['fileUploadId']}")
                print(f"   Status: {job_data['status']}")
                print(f"   Progress: {job_data['processedWebsites']}/{job_data['totalWebsites']}")
                print(f"   Created: {job_data['createdAt']}")
                print()
        else:
            print("❌ No scraping jobs found")
        
        # Check 4: Website counts by upload
        logger.info("🌐 Checking website counts by upload...")
        db_manager.cursor.execute("""
            SELECT "fileUploadId", COUNT(*) as website_count,
                   COUNT(CASE WHEN "scrapingStatus" = 'COMPLETED' THEN 1 END) as scraped,
                   COUNT(CASE WHEN "messageStatus" = 'GENERATED' THEN 1 END) as messaged,
                   COUNT(CASE WHEN "submissionStatus" = 'SUBMITTED' THEN 1 END) as submitted
            FROM websites 
            GROUP BY "fileUploadId"
            ORDER BY "fileUploadId"
        """)
        
        website_counts = db_manager.cursor.fetchall()
        if website_counts:
            print(f"🌐 Website counts by upload:")
            for count in website_counts:
                print(f"   Upload {count[0]}: {count[1]} websites")
                print(f"      Scraped: {count[2]}, Messages: {count[3]}, Submissions: {count[4]}")
        else:
            print("❌ No websites found in database")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Error checking system status: {e}")
        import traceback
        traceback.print_exc()
        return False

def check_file_system():
    """Check if there are any files in the upload directory"""
    
    try:
        logger.info("📁 Checking file system for uploads...")
        
        # Check common upload directories
        upload_dirs = [
            "uploads",
            "temp",
            "files",
            "data"
        ]
        
        for dir_name in upload_dirs:
            if os.path.exists(dir_name):
                files = os.listdir(dir_name)
                if files:
                    print(f"📁 Directory '{dir_name}' contains {len(files)} files:")
                    for file in files[:5]:  # Show first 5
                        file_path = os.path.join(dir_name, file)
                        if os.path.isfile(file_path):
                            size = os.path.getsize(file_path)
                            mtime = datetime.fromtimestamp(os.path.getmtime(file_path))
                            print(f"   📄 {file} ({size} bytes, modified: {mtime})")
                    
                    if len(files) > 5:
                        print(f"   ... and {len(files) - 5} more files")
                else:
                    print(f"📁 Directory '{dir_name}' is empty")
            else:
                print(f"📁 Directory '{dir_name}' does not exist")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Error checking file system: {e}")
        return False

def main():
    """Main function"""
    
    print("🔍 System Status and Stuck Uploads Check")
    print("=" * 60)
    print(f"📅 Check Time: {datetime.now()}")
    print()
    
    # Check system status
    if check_system_status():
        print("\n✅ System status check completed!")
    else:
        print("\n❌ System status check failed!")
    
    print()
    
    # Check file system
    if check_file_system():
        print("\n✅ File system check completed!")
    else:
        print("\n❌ File system check failed!")

if __name__ == "__main__":
    main()
