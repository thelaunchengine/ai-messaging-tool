#!/usr/bin/env python3
"""
Verify that the contact form submission fix worked
"""
import os
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    from database.database_manager import DatabaseManager
    
    print("=== VERIFYING CONTACT FORM SUBMISSION FIX ===")
    upload_id = "cmemjof6m0003py12kmr9fc82"
    print(f"Upload ID: {upload_id}")
    print()
    
    db = DatabaseManager()
    
    # Get websites for this upload
    websites = db.get_websites_by_file_upload_id(upload_id)
    
    if not websites:
        print("❌ No websites found for this upload ID")
        exit()
    
    print(f"Found {len(websites)} websites")
    print("=" * 80)
    
    for i, website in enumerate(websites, 1):
        print(f"🌐 WEBSITE {i}: {website.get('websiteUrl', 'N/A')}")
        print("-" * 60)
        
        # Check all statuses
        print(f"📊 COMPLETE STATUS:")
        print(f"   Scraping: {website.get('scrapingStatus', 'N/A')}")
        print(f"   Message: {website.get('messageStatus', 'N/A')}")
        print(f"   Contact Form: {website.get('submissionStatus', 'N/A')}")
        
        if website.get('submissionError'):
            print(f"   Error: {website.get('submissionError')}")
        
        if website.get('submittedFormFields'):
            print(f"   Form Fields: {website.get('submittedFormFields')}")
        
        if website.get('submissionResponse'):
            print(f"   Response: {website.get('submissionResponse')}")
        
        print()
    
    # Summary
    print("📊 FINAL STATUS SUMMARY:")
    scraping_completed = len([w for w in websites if w.get('scrapingStatus') == 'COMPLETED'])
    messages_generated = len([w for w in websites if w.get('messageStatus') == 'GENERATED'])
    contact_success = len([w for w in websites if w.get('submissionStatus') == 'SUCCESS'])
    contact_no_form = len([w for w in websites if w.get('submissionStatus') == 'NO_FORM_FOUND'])
    contact_failed = len([w for w in websites if w.get('submissionStatus') == 'FAILED'])
    contact_pending = len([w for w in websites if w.get('submissionStatus') == 'PENDING'])
    
    print(f"   ✅ Scraping: {scraping_completed}/{len(websites)}")
    print(f"   🤖 AI Messages: {messages_generated}/{len(websites)}")
    print(f"   📝 Contact Forms - Success: {contact_success}")
    print(f"   📝 Contact Forms - No Form: {contact_no_form}")
    print(f"   📝 Contact Forms - Failed: {contact_failed}")
    print(f"   📝 Contact Forms - Pending: {contact_pending}")
    
    print("\n=== VERIFICATION COMPLETE ===")
    
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
