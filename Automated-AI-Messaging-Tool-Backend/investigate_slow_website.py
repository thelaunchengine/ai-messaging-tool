#!/usr/bin/env python3

def investigate_slow_website():
    try:
        from database.database_manager import DatabaseManager
        import datetime
        
        db = DatabaseManager()
        
        # Find the specific website
        target_url = "http://www.oceanpearlspa.com/"
        
        # Get all websites to find the one we're looking for
        upload_id = "cme8m9dom000gpyin2i9cuwru"
        websites = db.get_websites_by_file_upload_id(upload_id)
        
        target_website = None
        for website in websites:
            if website.get('websiteUrl') == target_url:
                target_website = website
                break
        
        if not target_website:
            print(f"❌ Website not found: {target_url}")
            return
            
        print(f"=== INVESTIGATING SLOW WEBSITE: {target_url} ===")
        print(f"ID: {target_website.get('id')}")
        print(f"Company: {target_website.get('companyName', 'N/A')}")
        print(f"Industry: {target_website.get('industry', 'N/A')}")
        print(f"Scraping Status: {target_website.get('scrapingStatus', 'N/A')}")
        print(f"Message Status: {target_website.get('messageStatus', 'N/A')}")
        print()
        
        # Detailed timing analysis
        created_at = target_website.get('createdAt')
        updated_at = target_website.get('updatedAt')
        scraping_started = target_website.get('scrapingStartedAt')
        scraping_completed = target_website.get('scrapingCompletedAt')
        
        print(f"=== TIMING BREAKDOWN ===")
        if created_at:
            print(f"Created: {created_at}")
        if updated_at:
            print(f"Last Updated: {updated_at}")
        if scraping_started:
            print(f"Scraping Started: {scraping_started}")
        if scraping_completed:
            print(f"Scraping Completed: {scraping_completed}")
            
        # Calculate durations
        if created_at and updated_at:
            try:
                created = datetime.datetime.fromisoformat(created_at.replace('Z', '+00:00'))
                updated = datetime.datetime.fromisoformat(updated_at.replace('Z', '+00:00'))
                total_duration = updated - created
                print(f"Total Duration: {total_duration}")
            except Exception as e:
                print(f"Error calculating total duration: {e}")
                
        if scraping_started and scraping_completed:
            try:
                started = datetime.datetime.fromisoformat(scraping_started.replace('Z', '+00:00'))
                completed = datetime.datetime.fromisoformat(scraping_completed.replace('Z', '+00:00'))
                scraping_duration = completed - started
                print(f"Scraping Duration: {scraping_duration}")
                
                # Calculate time between creation and scraping start
                if created_at:
                    created = datetime.datetime.fromisoformat(created_at.replace('Z', '+00:00'))
                    queue_time = started - created
                    print(f"Queue Time (creation to start): {queue_time}")
                    
                # Calculate time between scraping completion and last update
                if updated_at:
                    last_updated = datetime.datetime.fromisoformat(updated_at.replace('Z', '+00:00'))
                    post_processing_time = last_updated - completed
                    print(f"Post-Processing Time: {post_processing_time}")
                    
            except Exception as e:
                print(f"Error calculating scraping duration: {e}")
        
        print()
        
        # Check for any error messages or additional data
        print(f"=== ADDITIONAL DATA ===")
        print(f"Generated Message: {'Yes' if target_website.get('generatedMessage') else 'No'}")
        print(f"Error Message: {target_website.get('errorMessage', 'None')}")
        print(f"Scraped Data Length: {len(str(target_website.get('scrapedData', '')))} characters")
        
        # Check if there's detailed scraping data
        scraped_data = target_website.get('scrapedData')
        if scraped_data:
            print(f"\n=== SCRAPED DATA PREVIEW ===")
            if isinstance(scraped_data, dict):
                for key, value in scraped_data.items():
                    if key in ['title', 'description', 'about', 'company', 'industry', 'contact']:
                        print(f"{key}: {str(value)[:100]}...")
            else:
                print(f"Raw data: {str(scraped_data)[:200]}...")
        
        # Compare with other websites to see the pattern
        print(f"\n=== COMPARISON WITH OTHER WEBSITES ===")
        completed_websites = [w for w in websites if w.get('scrapingStatus') == 'COMPLETED']
        
        if completed_websites:
            print(f"Total completed websites: {len(completed_websites)}")
            
            # Find the fastest and slowest
            durations = []
            for website in completed_websites:
                start = website.get('scrapingStartedAt')
                end = website.get('scrapingCompletedAt')
                if start and end:
                    try:
                        start_time = datetime.datetime.fromisoformat(start.replace('Z', '+00:00'))
                        end_time = datetime.datetime.fromisoformat(end.replace('Z', '+00:00'))
                        duration = end_time - start_time
                        durations.append((website.get('websiteUrl'), duration))
                    except:
                        pass
            
            if durations:
                durations.sort(key=lambda x: x[1])
                print(f"\nFastest website: {durations[0][0]} - {durations[0][1]}")
                print(f"Slowest website: {durations[-1][0]} - {durations[-1][1]}")
                
                # Find where our target website ranks
                target_duration = None
                for url, duration in durations:
                    if url == target_url:
                        target_duration = duration
                        break
                
                if target_duration:
                    rank = len([d for d in durations if d[1] < target_duration]) + 1
                    print(f"Target website rank: {rank}/{len(durations)} (slower than {rank-1} others)")
        
        # Check if there are any patterns in the data
        print(f"\n=== PATTERN ANALYSIS ===")
        if scraping_started and scraping_completed:
            try:
                started = datetime.datetime.fromisoformat(scraping_started.replace('Z', '+00:00'))
                completed = datetime.datetime.fromisoformat(scraping_completed.replace('Z', '+00:00'))
                
                # Check if it was processed during peak hours
                hour_started = started.hour
                hour_completed = completed.hour
                
                print(f"Started at: {hour_started}:00")
                print(f"Completed at: {hour_completed}:00")
                
                if hour_started != hour_completed:
                    print(f"⚠️  Processing crossed hour boundary - possible system load issue")
                    
                # Check if it was one of the last websites processed
                all_timestamps = []
                for website in websites:
                    if website.get('scrapingCompletedAt'):
                        try:
                            timestamp = datetime.datetime.fromisoformat(website.get('scrapingCompletedAt').replace('Z', '+00:00'))
                            all_timestamps.append((website.get('websiteUrl'), timestamp))
                        except:
                            pass
                
                if all_timestamps:
                    all_timestamps.sort(key=lambda x: x[1])
                    target_position = None
                    for i, (url, timestamp) in enumerate(all_timestamps):
                        if url == target_url:
                            target_position = i + 1
                            break
                    
                    if target_position:
                        print(f"Processing order: {target_position}/{len(all_timestamps)}")
                        if target_position > len(all_timestamps) * 0.8:
                            print(f"⚠️  Was processed near the end - possible resource exhaustion")
                        
            except Exception as e:
                print(f"Error in pattern analysis: {e}")
                
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    investigate_slow_website()
