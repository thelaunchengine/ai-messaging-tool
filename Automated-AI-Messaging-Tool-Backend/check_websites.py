#!/usr/bin/env python3

import pg8000

def check_websites():
    try:
        conn = pg8000.connect(
            host="localhost", 
            database="ai_messaging_tool", 
            user="postgres", 
            password="postgres"
        )
        cursor = conn.cursor()
        
        # Check websites for the specific upload ID
        cursor.execute("""
            SELECT id, "websiteUrl", "scrapingStatus", "messageStatus", "generatedMessage" 
            FROM websites 
            WHERE "fileUploadId" = %s
        """, ("cmel5qptv000ipy2h0wrmrc0j",))
        
        results = cursor.fetchall()
        
        print(f"Websites for upload cmel5qptv000ipy2h0wrmrc0j:")
        print(f"Total websites found: {len(results)}")
        
        for i, row in enumerate(results, 1):
            website_id, url, scraping_status, message_status, generated_message = row
            print(f"\n{i}. Website ID: {website_id}")
            print(f"   URL: {url}")
            print(f"   Scraping Status: {scraping_status}")
            print(f"   Message Status: {message_status}")
            print(f"   Generated Message: {generated_message[:100] if generated_message else 'None'}...")
        
        # Check file upload status
        cursor.execute("""
            SELECT id, status, "totalWebsites", "processedWebsites", "createdAt", "updatedAt"
            FROM "fileUploads" 
            WHERE id = %s
        """, ("cmel5qptv000ipy2h0wrmrc0j",))
        
        upload_result = cursor.fetchone()
        if upload_result:
            upload_id, status, total_websites, processed_websites, created_at, updated_at = upload_result
            print(f"\nFile Upload Status:")
            print(f"   ID: {upload_id}")
            print(f"   Status: {status}")
            print(f"   Total Websites: {total_websites}")
            print(f"   Processed Websites: {processed_websites}")
            print(f"   Created: {created_at}")
            print(f"   Updated: {updated_at}")
        
        conn.close()
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    check_websites()
