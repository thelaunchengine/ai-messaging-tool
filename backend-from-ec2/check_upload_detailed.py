#!/usr/bin/env python3

def check_upload_detailed():
    try:
        from database.database_manager import DatabaseManager
        import datetime
        
        db = DatabaseManager()
        
        # Check the specific upload
        upload_id = "cme8m9dom000gpyin2i9cuwru"
        upload = db.get_file_upload_by_id(upload_id)
        
        print(f"=== UPLOAD DETAILS ===")
        print(f"ID: {upload.get('id') if upload else 'Not found'}")
        print(f"Filename: {upload.get('originalName') if upload else 'N/A'}")
        print(f"Status: {upload.get('status') if upload else 'N/A'}")
        print(f"Total Websites: {upload.get('totalWebsites') if upload else 'N/A'}")
        print(f"Processed: {upload.get('processedWebsites') if upload else 'N/A'}")
        print(f"Failed: {upload.get('failedWebsites') if upload else 'N/A'}")
        print(f"Total Chunks: {upload.get('totalChunks') if upload else 'N/A'}")
        print(f"Completed Chunks: {upload.get('completedChunks') if upload else 'N/A'}")
        
        if upload:
            created_at = upload.get('createdAt')
            updated_at = upload.get('updatedAt')
            processing_started = upload.get('processingStartedAt')
            processing_completed = upload.get('processingCompletedAt')
            
            if created_at:
                print(f"Created: {created_at}")
            if updated_at:
                print(f"Last Updated: {updated_at}")
            if processing_started:
                print(f"Processing Started: {processing_started}")
            if processing_completed:
                print(f"Processing Completed: {processing_completed}")
                
            # Calculate duration
            if created_at and updated_at:
                try:
                    created = datetime.datetime.fromisoformat(created_at.replace('Z', '+00:00'))
                    updated = datetime.datetime.fromisoformat(updated_at.replace('Z', '+00:00'))
                    duration = updated - created
                    print(f"Total Duration: {duration}")
                except:
                    pass
                    
            if processing_started and processing_completed:
                try:
                    started = datetime.datetime.fromisoformat(processing_started.replace('Z', '+00:00'))
                    completed = datetime.datetime.fromisoformat(processing_completed.replace('Z', '+00:00'))
                    processing_duration = completed - started
                    print(f"Processing Duration: {processing_duration}")
                except:
                    pass
        
        print()
        
        # Check websites with detailed timing
        websites = db.get_websites_by_file_upload_id(upload_id)
        
        if websites:
            print(f"=== WEBSITE DETAILS ({len(websites)} websites) ===")
            
            # Find the specific website
            target_url = "https://www.oralandmaximplants.com"
            target_website = None
            
            for i, website in enumerate(websites, 1):
                print(f"\n{i}. ID: {website.get('id', 'N/A')}")
                print(f"   URL: {website.get('websiteUrl', 'N/A')}")
                print(f"   Company: {website.get('companyName', 'N/A')}")
                print(f"   Industry: {website.get('industry', 'N/A')}")
                print(f"   Scraping Status: {website.get('scrapingStatus', 'N/A')}")
                print(f"   Message Status: {website.get('messageStatus', 'N/A')}")
                print(f"   Generated Message: {'Yes' if website.get('generatedMessage') else 'No'}")
                print(f"   Error: {website.get('errorMessage', 'None')}")
                
                # Check timing
                created_at = website.get('createdAt')
                updated_at = website.get('updatedAt')
                scraping_started = website.get('scrapingStartedAt')
                scraping_completed = website.get('scrapingCompletedAt')
                
                if created_at:
                    print(f"   Created: {created_at}")
                if updated_at:
                    print(f"   Last Updated: {updated_at}")
                if scraping_started:
                    print(f"   Scraping Started: {scraping_started}")
                if scraping_completed:
                    print(f"   Scraping Completed: {scraping_completed}")
                
                # Calculate scraping duration
                if scraping_started and scraping_completed:
                    try:
                        started = datetime.datetime.fromisoformat(scraping_started.replace('Z', '+00:00'))
                        completed = datetime.datetime.fromisoformat(scraping_completed.replace('Z', '+00:00'))
                        scraping_duration = completed - started
                        print(f"   Scraping Duration: {scraping_duration}")
                    except:
                        pass
                
                # Check if this is our target website
                if website.get('websiteUrl') == target_url:
                    target_website = website
                    print(f"   *** TARGET WEBSITE FOUND ***")
                
                print()
            
            # Special analysis for target website
            if target_website:
                print(f"=== TARGET WEBSITE ANALYSIS: {target_url} ===")
                print(f"Status: {target_website.get('scrapingStatus', 'N/A')}")
                print(f"Message Status: {target_website.get('messageStatus', 'N/A')}")
                print(f"Company: {target_website.get('companyName', 'N/A')}")
                print(f"Industry: {target_website.get('industry', 'N/A')}")
                print(f"Error: {target_website.get('errorMessage', 'None')}")
                
                # Check if it's stuck
                if target_website.get('scrapingStatus') == 'IN_PROGRESS':
                    print(f"⚠️  WEBSITE IS STUCK IN PROGRESS!")
                    if scraping_started:
                        try:
                            started = datetime.datetime.fromisoformat(scraping_started.replace('Z', '+00:00'))
                            now = datetime.datetime.now(datetime.timezone.utc)
                            stuck_duration = now - started
                            print(f"   Stuck for: {stuck_duration}")
                        except:
                            pass
            else:
                print(f"❌ TARGET WEBSITE NOT FOUND: {target_url}")
                
        else:
            print("No websites found for this upload")
            
        # Check overall status analysis
        print(f"\n=== OVERALL STATUS ANALYSIS ===")
        if upload:
            if upload.get('status') == 'IN_PROGRESS':
                print("🔄 UPLOAD IS STILL RUNNING")
                if processing_started:
                    try:
                        started = datetime.datetime.fromisoformat(processing_started.replace('Z', '+00:00'))
                        now = datetime.datetime.now(datetime.timezone.utc)
                        running_duration = now - started
                        print(f"   Running for: {running_duration}")
                        print(f"   This is unusually long - should investigate!")
                    except:
                        pass
            elif upload.get('status') == 'COMPLETED':
                print("✅ UPLOAD COMPLETED")
            elif upload.get('status') == 'FAILED':
                print("❌ UPLOAD FAILED")
            else:
                print(f"❓ UNKNOWN STATUS: {upload.get('status')}")
                
        # Check for stuck processes
        if websites:
            stuck_count = sum(1 for w in websites if w.get('scrapingStatus') == 'IN_PROGRESS')
            failed_count = sum(1 for w in websites if w.get('scrapingStatus') == 'FAILED')
            completed_count = sum(1 for w in websites if w.get('scrapingStatus') == 'COMPLETED')
            
            print(f"\nWebsite Status Summary:")
            print(f"   Completed: {completed_count}")
            print(f"   Failed: {failed_count}")
            print(f"   Stuck: {stuck_count}")
            
            if stuck_count > 0:
                print(f"⚠️  {stuck_count} websites are stuck in progress!")
                
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    check_upload_detailed()
