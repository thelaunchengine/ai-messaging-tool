#!/usr/bin/env python3
"""
Detailed status check for both websites from upload cmemjof6m0003py12kmr9fc82
"""
import os
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    from database.database_manager import DatabaseManager
    
    print("=== DETAILED STATUS CHECK ===")
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
        
        # 1. Check if crawling was successful
        print("1️⃣ CRAWLING STATUS:")
        scraping_status = website.get('scrapingStatus', 'N/A')
        if scraping_status == 'COMPLETED':
            print("   ✅ CRAWLING SUCCESSFUL")
            print(f"   📝 Company Name: {website.get('companyName', 'N/A')}")
            print(f"   🏭 Industry: {website.get('industry', 'N/A')}")
            print(f"   🏢 Business Type: {website.get('businessType', 'N/A')}")
            
            # Check if about us content was scraped
            about_content = website.get('aboutUsContent', '')
            if about_content:
                print(f"   📄 About Us Content: {len(about_content)} characters scraped")
                print(f"   📄 Preview: {about_content[:100]}...")
            else:
                print("   ❌ No About Us content scraped")
        else:
            print(f"   ❌ CRAWLING FAILED - Status: {scraping_status}")
        
        print()
        
        # 2. Check if contact forms were found
        print("2️⃣ CONTACT FORM DETECTION:")
        has_contact_form = website.get('hasContactForm', False)
        contact_form_url = website.get('contactFormUrl', '')
        
        if has_contact_form:
            print("   ✅ CONTACT FORM DETECTED")
            if contact_form_url:
                print(f"   🔗 Contact Form URL: {contact_form_url}")
            else:
                print("   ℹ️  Contact form detected but no URL stored")
        else:
            print("   ❌ NO CONTACT FORM DETECTED")
        
        print()
        
        # 3. Check AI message generation
        print("3️⃣ AI MESSAGE GENERATION:")
        message_status = website.get('messageStatus', 'N/A')
        generated_message = website.get('generatedMessage', '')
        
        if message_status == 'GENERATED':
            print("   ✅ AI MESSAGE GENERATED AUTOMATICALLY")
            if generated_message:
                print(f"   📝 Message Length: {len(generated_message)} characters")
                print(f"   📝 Message Preview: {generated_message[:100]}...")
            else:
                print("   ⚠️  Status shows GENERATED but no message content")
        elif message_status == 'PENDING':
            print("   ⏳ AI MESSAGE GENERATION PENDING")
        elif message_status == 'FAILED':
            print("   ❌ AI MESSAGE GENERATION FAILED")
        else:
            print(f"   ℹ️  AI Message Status: {message_status}")
        
        print()
        
        # 4. Check contact form submission
        print("4️⃣ CONTACT FORM SUBMISSION:")
        submission_status = website.get('submissionStatus', 'N/A')
        submission_error = website.get('submissionError', '')
        submitted_fields = website.get('submittedFormFields', '')
        submission_response = website.get('submissionResponse', '')
        
        if submission_status == 'SUCCESS':
            print("   ✅ CONTACT FORM SUBMITTED AUTOMATICALLY")
            if submitted_fields:
                print(f"   📝 Form Fields Submitted: {submitted_fields}")
            if submission_response:
                print(f"   📨 Server Response: {submission_response}")
        elif submission_status == 'SUBMITTING':
            print("   🔄 CONTACT FORM SUBMISSION IN PROGRESS")
        elif submission_status == 'FAILED':
            print("   ❌ CONTACT FORM SUBMISSION FAILED")
            if submission_error:
                print(f"   ❌ Error: {submission_error}")
        elif submission_status == 'NO_FORM_FOUND':
            print("   ℹ️  NO CONTACT FORM FOUND ON WEBSITE")
        elif submission_status == 'PENDING':
            print("   ⏳ CONTACT FORM SUBMISSION PENDING")
        else:
            print(f"   ℹ️  Submission Status: {submission_status}")
        
        print()
        
        # 5. Check if workflow chain is complete
        print("5️⃣ WORKFLOW CHAIN STATUS:")
        workflow_steps = []
        
        if scraping_status == 'COMPLETED':
            workflow_steps.append("✅ Scraping")
        else:
            workflow_steps.append("❌ Scraping")
            
        if message_status == 'GENERATED':
            workflow_steps.append("✅ AI Message")
        else:
            workflow_steps.append("❌ AI Message")
            
        if submission_status == 'SUCCESS':
            workflow_steps.append("✅ Contact Form")
        elif submission_status in ['FAILED', 'NO_FORM_FOUND']:
            workflow_steps.append("⚠️ Contact Form")
        else:
            workflow_steps.append("❌ Contact Form")
        
        print(f"   Workflow: {' → '.join(workflow_steps)}")
        
        print("=" * 80)
        print()
    
    # Summary
    print("📊 OVERALL SUMMARY:")
    print(f"   Total Websites: {len(websites)}")
    
    scraping_completed = len([w for w in websites if w.get('scrapingStatus') == 'COMPLETED'])
    contact_forms_found = len([w for w in websites if w.get('hasContactForm') == True])
    messages_generated = len([w for w in websites if w.get('messageStatus') == 'GENERATED'])
    forms_submitted = len([w for w in websites if w.get('submissionStatus') == 'SUCCESS'])
    
    print(f"   ✅ Crawling Successful: {scraping_completed}/{len(websites)}")
    print(f"   🔍 Contact Forms Found: {contact_forms_found}/{len(websites)}")
    print(f"   🤖 AI Messages Generated: {messages_generated}/{len(websites)}")
    print(f"   📝 Contact Forms Submitted: {forms_submitted}/{len(websites)}")
    
    print("\n=== DETAILED STATUS CHECK COMPLETE ===")
    
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
