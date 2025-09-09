#!/usr/bin/env python3

def simple_investigation():
    try:
        from database.database_manager import DatabaseManager
        import datetime
        
        db = DatabaseManager()
        
        # Find the specific website
        target_url = "http://www.oceanpearlspa.com/"
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
        
        # Show all available fields
        print(f"=== ALL AVAILABLE FIELDS ===")
        for key, value in target_website.items():
            print(f"{key}: {value}")
        print()
        
        # Check timing fields specifically
        print(f"=== TIMING FIELDS ===")
        timing_fields = ['createdAt', 'updatedAt', 'scrapingStartedAt', 'scrapingCompletedAt', 'processingStartedAt', 'processingCompletedAt']
        
        for field in timing_fields:
            value = target_website.get(field)
            if value:
                print(f"{field}: {value}")
            else:
                print(f"{field}: NOT SET")
        print()
        
        # Calculate duration if we have the timestamps
        created_at = target_website.get('createdAt')
        updated_at = target_website.get('updatedAt')
        
        if created_at and updated_at:
            try:
                created = datetime.datetime.fromisoformat(created_at.replace('Z', '+00:00'))
                updated = datetime.datetime.fromisoformat(updated_at.replace('Z', '+00:00'))
                total_duration = updated - created
                print(f"Total Duration: {total_duration}")
                
                # Check if it was processed in chunks
                minutes_diff = total_duration.total_seconds() / 60
                print(f"Duration in minutes: {minutes_diff:.2f}")
                
            except Exception as e:
                print(f"Error calculating duration: {e}")
        
        # Check if there are any other websites with similar timing
        print(f"\n=== COMPARISON WITH OTHER WEBSITES ===")
        completed_websites = [w for w in websites if w.get('scrapingStatus') == 'COMPLETED']
        
        if completed_websites:
            print(f"Total completed websites: {len(completed_websites)}")
            
            # Show timing for all completed websites
            for i, website in enumerate(completed_websites[:10], 1):  # Show first 10
                url = website.get('websiteUrl', 'N/A')
                created = website.get('createdAt')
                updated = website.get('updatedAt')
                
                if created and updated:
                    try:
                        created_time = datetime.datetime.fromisoformat(created.replace('Z', '+00:00'))
                        updated_time = datetime.datetime.fromisoformat(updated.replace('Z', '+00:00'))
                        duration = updated_time - created_time
                        minutes = duration.total_seconds() / 60
                        print(f"{i}. {url}: {minutes:.2f} minutes")
                    except:
                        print(f"{i}. {url}: Error calculating time")
                else:
                    print(f"{i}. {url}: Missing timestamps")
                    
        # Check if there are any patterns
        print(f"\n=== PATTERN ANALYSIS ===")
        if created_at and updated_at:
            try:
                created = datetime.datetime.fromisoformat(created_at.replace('Z', '+00:00'))
                updated = datetime.datetime.fromisoformat(updated_at.replace('Z', '+00:00'))
                
                # Check if it was one of the last processed
                all_timestamps = []
                for website in websites:
                    if website.get('updatedAt'):
                        try:
                            timestamp = datetime.datetime.fromisoformat(website.get('updatedAt').replace('Z', '+00:00'))
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
                        elif target_position < len(all_timestamps) * 0.2:
                            print(f"✅ Was processed early - good performance")
                        else:
                            print(f"🔄 Was processed in the middle")
                        
            except Exception as e:
                print(f"Error in pattern analysis: {e}")
                
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    simple_investigation()
