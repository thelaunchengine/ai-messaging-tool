#!/usr/bin/env python3
"""
Direct database fix for contact form submission status
"""
import os
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    from database.database_manager import DatabaseManager
    
    print("=== DIRECT DATABASE FIX ===")
    upload_id = "cmemjof6m0003py12kmr9fc82"
    print(f"Upload ID: {upload_id}")
    print()
    
    db = DatabaseManager()
    connection = db.get_connection()
    cursor = connection.cursor()
    
    print("🔍 CURRENT DATABASE STATE:")
    cursor.execute("""
        SELECT "websiteUrl", "submissionStatus", "submissionError", "submittedFormFields", "submissionResponse"
        FROM websites 
        WHERE "fileUploadId" = %s
        ORDER BY "websiteUrl"
    """, (upload_id,))
    
    current_state = cursor.fetchall()
    for row in current_state:
        print(f"   {row[0]}: submissionStatus={row[1]}, error={row[2]}, fields={row[3]}, response={row[4]}")
    
    print()
    print("🔧 APPLYING FIXES:")
    
    # Fix 1: Update arauto505.com (has contact form, waiting for message)
    print("1️⃣ Fixing arauto505.com...")
    cursor.execute("""
        UPDATE websites 
        SET "submissionStatus" = 'PENDING'
        WHERE "websiteUrl" = %s AND "fileUploadId" = %s
    """, ('https://www.arauto505.com/about-us/', upload_id))
    
    if cursor.rowcount > 0:
        print("   ✅ Updated arauto505.com to PENDING")
    else:
        print("   ⚠️  No rows updated for arauto505.com")
    
    # Fix 2: Update farmers.com (has contact form, message generated, but no URL)
    print("2️⃣ Fixing farmers.com...")
    cursor.execute("""
        UPDATE websites 
        SET "submissionStatus" = 'NO_FORM_FOUND',
            "submissionError" = 'Contact form detected but no URL stored'
        WHERE "websiteUrl" = %s AND "fileUploadId" = %s
    """, ('https://www.farmers.com/contact-us/', upload_id))
    
    if cursor.rowcount > 0:
        print("   ✅ Updated farmers.com to NO_FORM_FOUND")
    else:
        print("   ⚠️  No rows updated for farmers.com")
    
    # Commit changes
    connection.commit()
    print("✅ Database changes committed!")
    
    print()
    print("🔍 VERIFYING FIXES:")
    cursor.execute("""
        SELECT "websiteUrl", "submissionStatus", "submissionError", "submittedFormFields", "submissionResponse"
        FROM websites 
        WHERE "fileUploadId" = %s
        ORDER BY "websiteUrl"
    """, (upload_id,))
    
    final_state = cursor.fetchall()
    for row in final_state:
        print(f"   {row[0]}: submissionStatus={row[1]}, error={row[2]}, fields={row[3]}, response={row[4]}")
    
    cursor.close()
    connection.close()
    
    print()
    print("=== DIRECT FIX COMPLETED ===")
    print("✅ Contact form submission statuses updated")
    print("✅ Check the upload results page to see the changes")
    
except Exception as e:
    print(f"❌ Direct fix failed: {e}")
    import traceback
    traceback.print_exc()
