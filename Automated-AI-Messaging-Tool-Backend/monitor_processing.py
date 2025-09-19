#!/usr/bin/env python3
"""
File Processing Monitor
Monitors file upload processing status and provides detailed debugging information
"""

import os
import sys
import psycopg2
from psycopg2.extras import RealDictCursor
from dotenv import load_dotenv
import json
from datetime import datetime
import time

load_dotenv()

class ProcessingMonitor:
    def __init__(self):
        self.db_url = os.getenv('DATABASE_URL', 'postgresql://postgres:AiMessaging2024Secure@production-ai-messaging-db.cmpkwkuqu30h.us-east-1.rds.amazonaws.com:5432/ai_messaging')
    
    def get_connection(self):
        return psycopg2.connect(self.db_url)
    
    def get_file_upload_status(self, file_upload_id=None):
        """Get status of file uploads"""
        conn = self.get_connection()
        try:
            with conn.cursor(cursor_factory=RealDictCursor) as cursor:
                if file_upload_id:
                    cursor.execute("""
                        SELECT * FROM file_uploads 
                        WHERE id = %s
                    """, (file_upload_id,))
                    result = cursor.fetchone()
                    return result
                else:
                    cursor.execute("""
                        SELECT * FROM file_uploads 
                        ORDER BY "createdAt" DESC 
                        LIMIT 10
                    """)
                    return cursor.fetchall()
        finally:
            conn.close()
    
    def get_chunks_status(self, file_upload_id):
        """Get status of processing chunks"""
        conn = self.get_connection()
        try:
            with conn.cursor(cursor_factory=RealDictCursor) as cursor:
                cursor.execute("""
                    SELECT * FROM processing_chunks 
                    WHERE "fileUploadId" = %s 
                    ORDER BY "chunkNumber"
                """, (file_upload_id,))
                return cursor.fetchall()
        finally:
            conn.close()
    
    def get_websites_status(self, file_upload_id):
        """Get status of websites"""
        conn = self.get_connection()
        try:
            with conn.cursor(cursor_factory=RealDictCursor) as cursor:
                cursor.execute("""
                    SELECT * FROM websites 
                    WHERE "fileUploadId" = %s 
                    ORDER BY "createdAt"
                """, (file_upload_id,))
                return cursor.fetchall()
        finally:
            conn.close()
    
    def get_scraping_jobs_status(self, file_upload_id):
        """Get status of scraping jobs"""
        conn = self.get_connection()
        try:
            with conn.cursor(cursor_factory=RealDictCursor) as cursor:
                cursor.execute("""
                    SELECT * FROM scraping_jobs 
                    WHERE "fileUploadId" = %s 
                    ORDER BY "createdAt" DESC
                """, (file_upload_id,))
                return cursor.fetchall()
        finally:
            conn.close()
    
    def monitor_file_upload(self, file_upload_id):
        """Monitor a specific file upload"""
        print(f"🔍 Monitoring File Upload: {file_upload_id}")
        print("=" * 60)
        
        # Get file upload status
        file_upload = self.get_file_upload_status(file_upload_id)
        if not file_upload:
            print(f"❌ File upload {file_upload_id} not found")
            return
        
        print(f"📁 File: {file_upload['originalName']}")
        print(f"📊 Status: {file_upload['status']}")
        print(f"👤 User: {file_upload['userId']}")
        print(f"📅 Created: {file_upload['createdAt']}")
        print(f"🔄 Updated: {file_upload['updatedAt']}")
        
        if file_upload['processingStartedAt']:
            print(f"⏱️  Processing Started: {file_upload['processingStartedAt']}")
        if file_upload['processingCompletedAt']:
            print(f"✅ Processing Completed: {file_upload['processingCompletedAt']}")
        
        print(f"📈 Progress: {file_upload['processedWebsites']}/{file_upload['totalWebsites']} websites")
        print(f"📦 Chunks: {file_upload['completedChunks']}/{file_upload['totalChunks']} completed")
        
        if file_upload.get('errorMessage'):
            print(f"❌ Error: {file_upload['errorMessage']}")
        
        print("\n" + "=" * 60)
        
        # Get chunks status
        chunks = self.get_chunks_status(file_upload_id)
        if chunks:
            print(f"📦 Processing Chunks ({len(chunks)} total):")
            for chunk in chunks:
                print(f"  Chunk {chunk['chunkNumber']}: {chunk['status']}")
                print(f"    Rows: {chunk['startRow']}-{chunk['endRow']} ({chunk['totalRecords']} total)")
                print(f"    Processed: {chunk['processedRecords']}, Failed: {chunk['failedRecords']}")
                if chunk['startedAt']:
                    print(f"    Started: {chunk['startedAt']}")
                if chunk['completedAt']:
                    print(f"    Completed: {chunk['completedAt']}")
                if chunk['errorMessage']:
                    print(f"    Error: {chunk['errorMessage']}")
                print()
        else:
            print("📦 No processing chunks found")
        
        # Get websites status
        websites = self.get_websites_status(file_upload_id)
        if websites:
            print(f"🌐 Websites ({len(websites)} total):")
            status_counts = {}
            for website in websites:
                status = website['scrapingStatus']
                status_counts[status] = status_counts.get(status, 0) + 1
            
            for status, count in status_counts.items():
                print(f"  {status}: {count} websites")
            
            # Show some sample websites
            print("\n📋 Sample Websites:")
            for website in websites[:5]:
                print(f"  {website['websiteUrl']} - {website['scrapingStatus']}")
        else:
            print("🌐 No websites found")
        
        # Get scraping jobs status
        scraping_jobs = self.get_scraping_jobs_status(file_upload_id)
        if scraping_jobs:
            print(f"\n🔧 Scraping Jobs ({len(scraping_jobs)} total):")
            for job in scraping_jobs:
                print(f"  Job {job['id']}: {job['status']}")
                print(f"    Websites: {job['processedWebsites']}/{job['totalWebsites']}")
                if job['startedAt']:
                    print(f"    Started: {job['startedAt']}")
                if job['completedAt']:
                    print(f"    Completed: {job['completedAt']}")
                if job['errorMessage']:
                    print(f"    Error: {job['errorMessage']}")
        else:
            print("🔧 No scraping jobs found")
    
    def list_recent_uploads(self):
        """List recent file uploads"""
        print("📋 Recent File Uploads:")
        print("=" * 60)
        
        uploads = self.get_file_upload_status()
        for upload in uploads:
            print(f"ID: {upload['id']}")
            print(f"File: {upload['originalName']}")
            print(f"Status: {upload['status']}")
            print(f"User: {upload['userId']}")
            print(f"Created: {upload['createdAt']}")
            print(f"Progress: {upload['processedWebsites']}/{upload['totalWebsites']} websites")
            if upload.get('errorMessage'):
                print(f"Error: {upload['errorMessage']}")
            print("-" * 40)
    
    def check_celery_workers(self):
        """Check if Celery workers are running"""
        print("🔧 Checking Celery Workers:")
        print("=" * 60)
        
        import subprocess
        try:
            result = subprocess.run(['ps', 'aux'], capture_output=True, text=True)
            celery_processes = [line for line in result.stdout.split('\n') if 'celery' in line.lower()]
            
            if celery_processes:
                print("✅ Celery workers found:")
                for process in celery_processes[:5]:  # Show first 5
                    print(f"  {process}")
            else:
                print("❌ No Celery workers found")
        except Exception as e:
            print(f"❌ Error checking Celery workers: {e}")
    
    def check_redis_connection(self):
        """Check Redis connection"""
        print("🔧 Checking Redis Connection:")
        print("=" * 60)
        
        try:
            import redis
            r = redis.Redis(host='localhost', port=6379, db=0)
            r.ping()
            print("✅ Redis connection successful")
            
            # Check for Celery tasks
            keys = r.keys('celery*')
            print(f"📊 Celery keys in Redis: {len(keys)}")
            
        except Exception as e:
            print(f"❌ Redis connection failed: {e}")
    
    def real_time_monitor(self, file_upload_id, interval=5):
        """Real-time monitoring of file upload"""
        print(f"🔄 Real-time monitoring for file upload: {file_upload_id}")
        print(f"⏱️  Update interval: {interval} seconds")
        print("Press Ctrl+C to stop")
        print("=" * 60)
        
        try:
            while True:
                os.system('clear' if os.name == 'posix' else 'cls')
                self.monitor_file_upload(file_upload_id)
                time.sleep(interval)
        except KeyboardInterrupt:
            print("\n🛑 Monitoring stopped")

def main():
    monitor = ProcessingMonitor()
    
    if len(sys.argv) < 2:
        print("Usage:")
        print("  python monitor_processing.py list                    # List recent uploads")
        print("  python monitor_processing.py monitor <upload_id>     # Monitor specific upload")
        print("  python monitor_processing.py realtime <upload_id>    # Real-time monitoring")
        print("  python monitor_processing.py check                   # Check system status")
        return
    
    command = sys.argv[1]
    
    if command == "list":
        monitor.list_recent_uploads()
    
    elif command == "monitor":
        if len(sys.argv) < 3:
            print("❌ Please provide file upload ID")
            return
        file_upload_id = sys.argv[2]
        monitor.monitor_file_upload(file_upload_id)
    
    elif command == "realtime":
        if len(sys.argv) < 3:
            print("❌ Please provide file upload ID")
            return
        file_upload_id = sys.argv[2]
        interval = int(sys.argv[3]) if len(sys.argv) > 3 else 5
        monitor.real_time_monitor(file_upload_id, interval)
    
    elif command == "check":
        monitor.check_celery_workers()
        print()
        monitor.check_redis_connection()
    
    else:
        print(f"❌ Unknown command: {command}")

if __name__ == "__main__":
    main() 