#!/usr/bin/env python3
"""
Direct SQL check for current status
"""
import os
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    from database.database_manager import DatabaseManager
    
    print("=== DIRECT SQL STATUS CHECK ===")
    upload_id = "cmemjof6m0003py12kmr9fc82"
    print(f"Upload ID: {upload_id}")
    print()
    
    db = DatabaseManager()
    connection = db.get_connection()
    cursor = connection.cursor()
    
    print("🔍 DIRECT DATABASE QUERY:")
    cursor.execute("""
        SELECT 
            "websiteUrl",
            "scrapingStatus",
            "messageStatus",
            "submissionStatus",
            "submissionError",
            "submittedFormFields",
            "submissionResponse",
            "companyName",
            "industry",
            "hasContactForm",
            "contactFormUrl"
        FROM websites 
        WHERE "fileUploadId" = %s
        ORDER BY "websiteUrl"
    """, (upload_id,))
    
    results = cursor.fetchall()
    
    for i, row in enumerate(results, 1):
        print(f"🌐 WEBSITE {i}: {row[0]}")
        print("-" * 60)
        print(f"   Scraping: {row[1]}")
        print(f"   Message: {row[2]}")
        print(f"   Contact Form: {row[3]}")
        print(f"   Error: {row[4]}")
        print(f"   Form Fields: {row[5]}")
        print(f"   Response: {row[6]}")
        print(f"   Company: {row[7]}")
        print(f"   Industry: {row[8]}")
        print(f"   Has Contact Form: {row[9]}")
        print(f"   Contact Form URL: {row[10]}")
        print()
    
    # Count by status
    print("📊 STATUS COUNTS:")
    submission_statuses = [row[3] for row in results]
    status_counts = {}
    for status in submission_statuses:
        status_counts[status] = status_counts.get(status, 0) + 1
    
    for status, count in status_counts.items():
        print(f"   {status}: {count}")
    
    cursor.close()
    connection.close()
    
    print("\n=== SQL CHECK COMPLETE ===")
    
except Exception as e:
    print(f"❌ SQL check failed: {e}")
    import traceback
    traceback.print_exc()
