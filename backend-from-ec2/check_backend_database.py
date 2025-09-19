#!/usr/bin/env python3
"""
Backend Database Check Script
Checks what's in the backend database vs frontend
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

def check_backend_database():
    """Check backend database for uploads"""
    
    try:
        logger.info("🔍 Checking backend database...")
        
        from database.database_manager import DatabaseManager
        db_manager = DatabaseManager()
        
        # Check 1: All file uploads in backend
        logger.info("📁 Checking all file uploads in backend...")
        db_manager.cursor.execute("""
            SELECT id, "userId", status, "totalWebsites", "processedWebsites", 
                   "failedWebsites", "createdAt", "updatedAt", filename, "originalName"
            FROM file_uploads 
            ORDER BY "createdAt" DESC
            LIMIT 20
        """)
        
        backend_uploads = db_manager.cursor.fetchall()
        if backend_uploads:
            print(f"📊 Backend database contains {len(backend_uploads)} file uploads:")
            for upload in backend_uploads:
                columns = [desc[0] for desc in db_manager.cursor.description]
                upload_data = dict(zip(columns, upload))
                print(f"   📁 {upload_data['id']}")
                print(f"      Status: {upload_data['status']}")
                print(f"      User ID: {upload_data['userId']}")
                print(f"      Original Name: {upload_data['originalName']}")
                print(f"      Backend Path: {upload_data['filename']}")
                print(f"      Created: {upload_data['createdAt']}")
                print()
        else:
            print("❌ No file uploads found in backend database!")
        
        # Check 2: Check if the specific upload ID exists
        target_upload_id = "cmelge11r000qpy2h0aahoxmk"
        logger.info(f"🔍 Checking for specific upload ID: {target_upload_id}")
        
        db_manager.cursor.execute("""
            SELECT id, "userId", status, "totalWebsites", "processedWebsites", 
                   "failedWebsites", "createdAt", "updatedAt", filename, "originalName"
            FROM file_uploads 
            WHERE id = %s
        """, (target_upload_id,))
        
        specific_upload = db_manager.cursor.fetchone()
        if specific_upload:
            columns = [desc[0] for desc in db_manager.cursor.description]
            upload_data = dict(zip(columns, specific_upload))
            print(f"✅ Found upload {target_upload_id} in backend database:")
            print(f"   Status: {upload_data['status']}")
            print(f"   User ID: {upload_data['userId']}")
            print(f"   Original Name: {upload_data['originalName']}")
            print(f"   Backend Path: {upload_data['filename']}")
            print(f"   Created: {upload_data['createdAt']}")
        else:
            print(f"❌ Upload ID {target_upload_id} NOT found in backend database!")
        
        # Check 3: Check file system for uploaded files
        logger.info("📁 Checking backend uploads directory...")
        upload_dir = "uploads"
        if os.path.exists(upload_dir):
            files = os.listdir(upload_dir)
            if files:
                print(f"\n📁 Backend uploads directory contains {len(files)} files:")
                for file in files[:10]:  # Show first 10
                    file_path = os.path.join(upload_dir, file)
                    if os.path.isfile(file_path):
                        size = os.path.getsize(file_path)
                        mtime = datetime.fromtimestamp(os.path.getmtime(file_path))
                        print(f"   📄 {file} ({size} bytes, modified: {mtime})")
                
                if len(files) > 10:
                    print(f"   ... and {len(files) - 10} more files")
            else:
                print(f"📁 Backend uploads directory is empty")
        else:
            print(f"📁 Backend uploads directory does not exist")
        
        # Check 4: Check for any recent uploads (last 24 hours)
        logger.info("🕐 Checking recent uploads (last 24 hours)...")
        db_manager.cursor.execute("""
            SELECT id, "userId", status, "totalWebsites", "processedWebsites", 
                   "failedWebsites", "createdAt", "updatedAt", filename, "originalName"
            FROM file_uploads 
            WHERE "createdAt" >= NOW() - INTERVAL '24 hours'
            ORDER BY "createdAt" DESC
        """)
        
        recent_uploads = db_manager.cursor.fetchall()
        if recent_uploads:
            print(f"\n🕐 Found {len(recent_uploads)} recent uploads (last 24 hours):")
            for upload in recent_uploads:
                columns = [desc[0] for desc in db_manager.cursor.description]
                upload_data = dict(zip(columns, upload))
                print(f"   📁 {upload_data['id']}")
                print(f"      Status: {upload_data['status']}")
                print(f"      Original Name: {upload_data['originalName']}")
                print(f"      Created: {upload_data['createdAt']}")
        else:
            print("\n❌ No recent uploads found in backend database")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Error checking backend database: {e}")
        import traceback
        traceback.print_exc()
        return False

def check_database_connection():
    """Check if we can connect to the database"""
    
    try:
        logger.info("🔌 Testing database connection...")
        
        from database.database_manager import DatabaseManager
        db_manager = DatabaseManager()
        
        # Test simple query
        db_manager.cursor.execute("SELECT 1")
        result = db_manager.cursor.fetchone()
        
        if result:
            print("✅ Database connection successful")
            return True
        else:
            print("❌ Database connection failed")
            return False
            
    except Exception as e:
        logger.error(f"❌ Database connection error: {e}")
        return False

def main():
    """Main function"""
    
    print("🔍 Backend Database Investigation")
    print("=" * 60)
    print(f"📅 Check Time: {datetime.now()}")
    print()
    
    # Check database connection first
    if check_database_connection():
        print("\n✅ Database connection successful, proceeding with investigation...")
        
        # Check backend database
        if check_backend_database():
            print("\n✅ Backend database check completed!")
        else:
            print("\n❌ Backend database check failed!")
    else:
        print("\n❌ Cannot connect to database!")

if __name__ == "__main__":
    main()
