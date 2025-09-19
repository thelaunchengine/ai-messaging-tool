#!/usr/bin/env python3
"""
Check status of new upload ID
"""
import os
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    from database.database_manager import DatabaseManager
    
    print("=== NEW UPLOAD STATUS CHECK ===")
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
    
    # Check websites status
    print("=== WEBSITES STATUS ===")
    try:
        websites = db.get_websites_by_file_upload_id(upload_id)
        if websites:
            print(f"✅ Found {len(websites)} websites:")
            print()
            
            # Count by status
            scraping_completed = len([w for w in websites if w.get('scrapingStatus') == 'COMPLETED'])
            scraping_failed = len([w for w in websites if w.get('scrapingStatus') == 'FAILED'])
            scraping_pending = len([w for w in websites if w.get('scrapingStatus') == 'PENDING'])
            
            message_generated = len([w for w in websites if w.get('messageStatus') == 'GENERATED'])
            message_failed = len([w for w in websites if w.get('messageStatus') == 'FAILED'])
            message_pending = len([w for w in websites if w.get('messageStatus') == 'PENDING'])
            
            contact_success = len([w for w in websites if w.get('submissionStatus') == 'SUCCESS'])
            contact_failed = len([w for w in websites if w.get('submissionStatus') == 'FAILED'])
            contact_pending = len([w for w in websites if w.get('submissionStatus') == 'PENDING'])
            contact_submitting = len([w for w in websites if w.get('submissionStatus') == 'SUBMITTING'])
            contact_no_form = len([w for w in websites if w.get('submissionStatus') == 'NO_FORM_FOUND'])
            
            print(f"📊 STATUS SUMMARY:")
            print(f"  Scraping: {scraping_completed} completed, {scraping_failed} failed, {scraping_pending} pending")
            print(f"  Messages: {message_generated} generated, {message_failed} failed, {message_pending} pending")
            print(f"  Contact Forms: {contact_success} success, {contact_failed} failed, {contact_pending} pending, {contact_submitting} submitting, {contact_no_form} no form")
            print()
            
            # Show individual websites
            for i, website in enumerate(websites, 1):
                print(f"🌐 Website {i}: {website.get('websiteUrl', 'N/A')}")
                print(f"     Company: {website.get('companyName', 'N/A')}")
                print(f"     Industry: {website.get('industry', 'N/A')}")
                print(f"     Scraping: {website.get('scrapingStatus', 'N/A')}")
                print(f"     Message: {website.get('messageStatus', 'N/A')}")
                print(f"     Contact Form: {website.get('submissionStatus', 'N/A')}")
                if website.get('submissionError'):
                    print(f"     Error: {website.get('submissionError')}")
                if website.get('submittedFormFields'):
                    print(f"     Form Fields: {website.get('submittedFormFields')}")
                if website.get('submissionResponse'):
                    print(f"     Response: {website.get('submissionResponse')}")
                print("     ---")
        else:
            print(f"❌ No websites found for this upload ID")
    except Exception as e:
        print(f"❌ Error checking websites: {e}")
    
    print()
    
    # Check contact inquiries
    print("=== CONTACT INQUIRIES STATUS ===")
    try:
        inquiries = db.get_all_contact_inquiries()
        if inquiries:
            upload_inquiries = [i for i in inquiries if i.get('fileUploadId') == upload_id]
            if upload_inquiries:
                print(f"✅ Found {len(upload_inquiries)} contact inquiries:")
                for i, inquiry in enumerate(upload_inquiries, 1):
                    print(f"  {i}. Website: {inquiry.get('websiteUrl', 'N/A')}")
                    print(f"     Status: {inquiry.get('status', 'N/A')}")
                    print(f"     Submission: {inquiry.get('submissionStatus', 'N/A')}")
                    print("     ---")
            else:
                print(f"ℹ️  No contact inquiries found for this upload ID")
        else:
            print(f"ℹ️  No contact inquiries found in database")
    except Exception as e:
        print(f"❌ Error checking contact inquiries: {e}")
    
    print("\n=== STATUS CHECK COMPLETE ===")
    
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
