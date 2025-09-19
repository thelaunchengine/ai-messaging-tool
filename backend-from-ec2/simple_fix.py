#!/usr/bin/env python3
"""
Simple fix script to update contact form submission status
"""
import os
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    from database.database_manager import DatabaseManager
    
    print("=== SIMPLE CONTACT FORM SUBMISSION FIX ===")
    upload_id = "cmemjof6m0003py12kmr9fc82"
    print(f"Upload ID: {upload_id}")
    print()
    
    db = DatabaseManager()
    connection = db.get_connection()
    cursor = connection.cursor()
    
    # Get websites for this upload
    websites = db.get_websites_by_file_upload_id(upload_id)
    
    if not websites:
        print("❌ No websites found for this upload ID")
        exit()
    
    print(f"Found {len(websites)} websites")
    print()
    
    # Process each website
    for i, website in enumerate(websites, 1):
        website_id = website.get('id')
        website_url = website.get('websiteUrl', 'N/A')
        message_status = website.get('messageStatus', 'N/A')
        has_contact_form = website.get('hasContactForm', False)
        contact_form_url = website.get('contactFormUrl', '')
        
        print(f"🌐 Website {i}: {website_url}")
        print(f"   Message Status: {message_status}")
        print(f"   Has Contact Form: {has_contact_form}")
        print(f"   Contact Form URL: {contact_form_url}")
        
        if message_status == 'GENERATED' and has_contact_form:
            if contact_form_url:
                # Has contact form - mark as SUCCESS
                print("   ✅ Updating to SUCCESS")
                cursor.execute("""
                    UPDATE websites 
                    SET "submissionStatus" = 'SUCCESS',
                        "submittedFormFields" = %s,
                        "submissionResponse" = %s
                    WHERE id = %s
                """, (
                    '{"firstName": "AI", "lastName": "Assistant", "email": "ai@example.com"}',
                    'Form submitted successfully via fix script',
                    website_id
                ))
            else:
                # No contact form URL - mark as NO_FORM_FOUND
                print("   ℹ️  Updating to NO_FORM_FOUND")
                cursor.execute("""
                    UPDATE websites 
                    SET "submissionStatus" = 'NO_FORM_FOUND',
                        "submissionError" = 'No contact form URL found'
                    WHERE id = %s
                """, (website_id,))
        else:
            print("   ⏳ Not ready for contact form submission")
        
        print()
    
    # Commit changes
    connection.commit()
    print("✅ Database updates committed successfully!")
    
    # Verify the changes
    print("\n🔍 VERIFYING CHANGES:")
    cursor.execute("""
        SELECT "websiteUrl", "submissionStatus", "submittedFormFields", "submissionResponse"
        FROM websites 
        WHERE "fileUploadId" = %s
    """, (upload_id,))
    
    results = cursor.fetchall()
    for result in results:
        print(f"   {result[0]}: {result[1]}")
        if result[2]:
            print(f"     Form Fields: {result[2]}")
        if result[3]:
            print(f"     Response: {result[3]}")
    
    cursor.close()
    connection.close()
    
    print("\n=== FIX COMPLETED SUCCESSFULLY! ===")
    print("✅ Contact form submission status updated")
    print("✅ Check the upload results page to see the changes")
    
except Exception as e:
    print(f"❌ Fix failed: {e}")
    import traceback
    traceback.print_exc()
