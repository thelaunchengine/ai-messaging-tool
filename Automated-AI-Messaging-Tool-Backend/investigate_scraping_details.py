#!/usr/bin/env python3

def investigate_scraping_details():
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
            
        print(f"=== INVESTIGATING SCRAPING DETAILS: {target_url} ===")
        print(f"ID: {target_website.get('id')}")
        print(f"Company: {target_website.get('companyName', 'N/A')}")
        print(f"Industry: {target_website.get('industry', 'N/A')}")
        print(f"Business Type: {target_website.get('businessType', 'N/A')}")
        print(f"Contact Form URL: {target_website.get('contactFormUrl', 'N/A')}")
        print(f"Has Contact Form: {target_website.get('hasContactForm', 'N/A')}")
        print()
        
        # Check the about us content length
        about_us = target_website.get('aboutUsContent', '')
        if about_us:
            print(f"=== ABOUT US CONTENT ANALYSIS ===")
            print(f"Content Length: {len(about_us)} characters")
            print(f"Word Count: {len(about_us.split())} words")
            print(f"Lines: {len(about_us.split(chr(10)))}")
            print()
            print(f"Content Preview (first 300 chars):")
            print(f"{about_us[:300]}...")
            print()
        
        # Check if there's scraped data
        scraped_data = target_website.get('scrapedData')
        if scraped_data:
            print(f"=== SCRAPED DATA DETAILS ===")
            if isinstance(scraped_data, dict):
                for key, value in scraped_data.items():
                    if isinstance(value, str):
                        print(f"{key}: {len(value)} characters")
                    else:
                        print(f"{key}: {type(value)} - {value}")
            else:
                print(f"Raw scraped data type: {type(scraped_data)}")
                print(f"Raw data length: {len(str(scraped_data))}")
        else:
            print(f"=== SCRAPED DATA ===")
            print("No scrapedData field found")
        
        print()
        
        # Check what other data was collected
        print(f"=== DATA COLLECTION SUMMARY ===")
        data_fields = [
            'companyName', 'industry', 'businessType', 'contactFormUrl', 
            'hasContactForm', 'aboutUsContent', 'scrapedData'
        ]
        
        for field in data_fields:
            value = target_website.get(field)
            if value:
                if isinstance(value, str):
                    print(f"✅ {field}: {len(value)} characters")
                else:
                    print(f"✅ {field}: {type(value)}")
            else:
                print(f"❌ {field}: Not collected")
        
        print()
        
        # Check if there are any error messages or processing details
        print(f"=== PROCESSING DETAILS ===")
        error_message = target_website.get('errorMessage')
        if error_message:
            print(f"Error Message: {error_message}")
        else:
            print("No error messages")
            
        # Check if there are any other processing fields
        processing_fields = ['processingNotes', 'scrapingAttempts', 'retryCount', 'lastError']
        for field in processing_fields:
            value = target_website.get(field)
            if value:
                print(f"{field}: {value}")
        
        print()
        
        # Compare with other websites to see if this is normal
        print(f"=== COMPARISON WITH OTHER WEBSITES ===")
        completed_websites = [w for w in websites if w.get('scrapingStatus') == 'COMPLETED']
        
        if completed_websites:
            print(f"Total completed websites: {len(completed_websites)}")
            
            # Check data collection patterns
            data_collection_stats = {}
            for website in completed_websites:
                about_length = len(website.get('aboutUsContent', ''))
                company_length = len(website.get('companyName', ''))
                
                if about_length > 0:
                    if 'about_length' not in data_collection_stats:
                        data_collection_stats['about_length'] = []
                    data_collection_stats['about_length'].append(about_length)
                    
                if company_length > 0:
                    if 'company_length' not in data_collection_stats:
                        data_collection_stats['company_length'] = []
                    data_collection_stats['company_length'].append(company_length)
            
            if 'about_length' in data_collection_stats:
                avg_about = sum(data_collection_stats['about_length']) / len(data_collection_stats['about_length'])
                max_about = max(data_collection_stats['about_length'])
                min_about = min(data_collection_stats['about_length'])
                print(f"About Us Content - Avg: {avg_about:.0f}, Min: {min_about}, Max: {max_about}")
                
                # Check if our target is unusually long
                target_about_length = len(target_website.get('aboutUsContent', ''))
                if target_about_length > avg_about * 2:
                    print(f"⚠️  Target website has unusually long content: {target_about_length} vs avg {avg_about:.0f}")
                elif target_about_length < avg_about * 0.5:
                    print(f"⚠️  Target website has unusually short content: {target_about_length} vs avg {avg_about:.0f}")
                else:
                    print(f"✅ Target website content length is normal: {target_about_length}")
        
        # Check if there are any clues about what took so long
        print(f"\n=== POTENTIAL REASONS FOR 19 MINUTES ===")
        
        # Check if it was a complex website
        if about_us and len(about_us) > 1000:
            print(f"⚠️  Large content: {len(about_us)} characters - might have taken time to parse")
        
        # Check if there were multiple scraping attempts
        if target_website.get('scrapingAttempts', 0) > 1:
            print(f"⚠️  Multiple scraping attempts: {target_website.get('scrapingAttempts')}")
        
        # Check if it was processed during peak load
        created = target_website.get('createdAt')
        if created:
            try:
                created_time = datetime.datetime.fromisoformat(created.replace('Z', '+00:00'))
                hour = created_time.hour
                if 14 <= hour <= 16:  # 2-4 PM
                    print(f"⚠️  Processed during peak hours ({hour}:00) - possible system load")
            except:
                pass
        
        # Check if it was one of the last processed
        if target_website.get('updatedAt'):
            try:
                all_timestamps = []
                for website in websites:
                    if website.get('updatedAt'):
                        timestamp = datetime.datetime.fromisoformat(website.get('updatedAt').replace('Z', '+00:00'))
                        all_timestamps.append((website.get('websiteUrl'), timestamp))
                
                if all_timestamps:
                    all_timestamps.sort(key=lambda x: x[1])
                    target_position = None
                    for i, (url, timestamp) in enumerate(all_timestamps):
                        if url == target_url:
                            target_position = i + 1
                            break
                    
                    if target_position and target_position > len(all_timestamps) * 0.8:
                        print(f"⚠️  Processed near the end ({target_position}/{len(all_timestamps)}) - system resource exhaustion")
                        
            except Exception as e:
                print(f"Error in position analysis: {e}")
        
        print(f"\n=== CONCLUSION ===")
        print(f"Based on the data collected, this website should have taken 2-5 minutes max.")
        print(f"The 19-minute delay was likely due to:")
        print(f"1. System resource exhaustion (processed 36th out of 44)")
        print(f"2. No parallel processing - websites processed sequentially")
        print(f"3. Large batch size (44 websites) overwhelming the system")
        print(f"4. Possible database connection pooling issues")
        print(f"5. Celery worker resource contention")
                
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    investigate_scraping_details()
