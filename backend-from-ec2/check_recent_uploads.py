#!/usr/bin/env python3
"""
Recent Uploads Check Script
Checks recent uploads and system status
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

def check_recent_uploads():
    """Check recent uploads and system status"""
    
    try:
        logger.info("🔍 Checking recent uploads and system status...")
        
        from database.database_manager import DatabaseManager
        db_manager = DatabaseManager()
        
        # Check 1: Recent file uploads (last 24 hours)
        logger.info("📁 Checking recent file uploads...")
        db_manager.cursor.execute("""
            SELECT id, "userId", status, "totalWebsites", "processedWebsites", 
                   "failedWebsites", "createdAt", "updatedAt"
            FROM file_uploads 
            WHERE "createdAt" >= NOW() - INTERVAL '24 hours'
            ORDER BY "createdAt" DESC
            LIMIT 10
        """)
        
        recent_uploads = db_manager.cursor.fetchall()
        if recent_uploads:
            print(f"✅ Found {len(recent_uploads)} recent uploads (last 24 hours):")
            for upload in recent_uploads:
                columns = [desc[0] for desc in db_manager.cursor.description]
                upload_data = dict(zip(columns, upload))
                print(f"   📁 {upload_data['id']}")
                print(f"      Status: {upload_data['status']}")
                print(f"      Websites: {upload_data['totalWebsites']} total, {upload_data['processedWebsites']} processed, {upload_data['failedWebsites']} failed")
                print(f"      Created: {upload_data['createdAt']}")
                print()
        else:
            print("❌ No recent uploads found in the last 24 hours")
        
        # Check 2: All uploads (last 7 days)
        logger.info("📁 Checking all uploads in last 7 days...")
        db_manager.cursor.execute("""
            SELECT id, "userId", status, "totalWebsites", "processedWebsites", 
                   "failedWebsites", "createdAt", "updatedAt"
            FROM file_uploads 
            WHERE "createdAt" >= NOW() - INTERVAL '7 days'
            ORDER BY "createdAt" DESC
        """)
        
        weekly_uploads = db_manager.cursor.fetchall()
        if weekly_uploads:
            print(f"📊 Weekly Summary ({len(weekly_uploads)} uploads):")
            
            # Count by status
            status_counts = {}
            for upload in weekly_uploads:
                columns = [desc[0] for desc in db_manager.cursor.description]
                upload_data = dict(zip(columns, upload))
                status = upload_data['status']
                status_counts[status] = status_counts.get(status, 0) + 1
            
            for status, count in status_counts.items():
                print(f"   {status}: {count} uploads")
            
            print()
            
            # Show all upload IDs
            print("📋 All Upload IDs (last 7 days):")
            for upload in weekly_uploads:
                columns = [desc[0] for desc in db_manager.cursor.description]
                upload_data = dict(zip(columns, upload))
                print(f"   {upload_data['id']} - {upload_data['status']} - {upload_data['createdAt']}")
        else:
            print("❌ No uploads found in the last 7 days")
        
        # Check 3: System status - active scraping jobs
        logger.info("🔧 Checking active scraping jobs...")
        db_manager.cursor.execute("""
            SELECT id, "fileUploadId", status, "totalWebsites", "processedWebsites", 
                   "failedWebsites", "createdAt", "updatedAt"
            FROM scraping_jobs 
            WHERE status IN ('PENDING', 'PROCESSING')
            ORDER BY "createdAt" DESC
            LIMIT 10
        """)
        
        active_jobs = db_manager.cursor.fetchall()
        if active_jobs:
            print(f"\n🔧 Found {len(active_jobs)} active scraping jobs:")
            for job in active_jobs:
                columns = [desc[0] for desc in db_manager.cursor.description]
                job_data = dict(zip(columns, job))
                print(f"   Job ID: {job_data['id']}")
                print(f"   Upload ID: {job_data['fileUploadId']}")
                print(f"   Status: {job_data['status']}")
                print(f"   Progress: {job_data['processedWebsites']}/{job_data['totalWebsites']}")
                print(f"   Created: {job_data['createdAt']}")
                print()
        else:
            print("\n✅ No active scraping jobs found")
        
        # Check 4: Recent website activity
        logger.info("🌐 Checking recent website activity...")
        db_manager.cursor.execute("""
            SELECT "fileUploadId", COUNT(*) as website_count,
                   COUNT(CASE WHEN "scrapingStatus" = 'COMPLETED' THEN 1 END) as scraped,
                   COUNT(CASE WHEN "messageStatus" = 'GENERATED' THEN 1 END) as messaged,
                   COUNT(CASE WHEN "submissionStatus" = 'SUBMITTED' THEN 1 END) as submitted
            FROM websites 
            WHERE "createdAt" >= NOW() - INTERVAL '24 hours'
            GROUP BY "fileUploadId"
            ORDER BY "fileUploadId"
        """)
        
        recent_activity = db_manager.cursor.fetchall()
        if recent_activity:
            print(f"\n🌐 Recent Website Activity (last 24 hours):")
            for activity in recent_activity:
                print(f"   Upload {activity[0]}: {activity[1]} websites")
                print(f"      Scraped: {activity[2]}, Messages: {activity[3]}, Submissions: {activity[4]}")
        else:
            print("\n❌ No recent website activity found")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Error checking recent uploads: {e}")
        import traceback
        traceback.print_exc()
        return False

def search_upload_by_pattern(pattern: str):
    """Search for uploads by pattern"""
    
    try:
        logger.info(f"🔍 Searching for uploads with pattern: {pattern}")
        
        from database.database_manager import DatabaseManager
        db_manager = DatabaseManager()
        
        # Search for uploads containing the pattern
        db_manager.cursor.execute("""
            SELECT id, "userId", status, "totalWebsites", "processedWebsites", 
                   "failedWebsites", "createdAt", "updatedAt"
            FROM file_uploads 
            WHERE id LIKE %s
            ORDER BY "createdAt" DESC
        """, (f"%{pattern}%",))
        
        matching_uploads = db_manager.cursor.fetchall()
        if matching_uploads:
            print(f"🔍 Found {len(matching_uploads)} upload(s) matching pattern '{pattern}':")
            for upload in matching_uploads:
                columns = [desc[0] for desc in db_manager.cursor.description]
                upload_data = dict(zip(columns, upload))
                print(f"   📁 {upload_data['id']}")
                print(f"      Status: {upload_data['status']}")
                print(f"      Created: {upload_data['createdAt']}")
                print()
        else:
            print(f"❌ No uploads found matching pattern '{pattern}'")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Error searching uploads: {e}")
        return False

def main():
    """Main function"""
    
    print("🔍 Recent Uploads and System Status Check")
    print("=" * 60)
    print(f"📅 Check Time: {datetime.now()}")
    print()
    
    # Check recent uploads
    if check_recent_uploads():
        print("\n✅ Recent uploads check completed!")
    else:
        print("\n❌ Recent uploads check failed!")
    
    print()
    
    # Search for uploads with similar pattern
    print("🔍 Searching for uploads with similar pattern...")
    search_patterns = ["cmelge", "cmel", "cmelg"]
    
    for pattern in search_patterns:
        print(f"\n🔍 Searching pattern: {pattern}")
        search_upload_by_pattern(pattern)

if __name__ == "__main__":
    main()
