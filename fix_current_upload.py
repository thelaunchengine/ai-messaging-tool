#!/usr/bin/env python3
import sys
import os
import re
sys.path.append('/home/xb3353/Automated-AI-Messaging-Tool-Backend')

from database.database_manager import DatabaseManager

def clean_company_name(title):
    """Clean company name from various title formats"""
    
    # Start with the original title
    cleaned = title
    
    # Pattern 1: Remove "Find a X Agent in Y, Z | Company" format
    # Example: "Find a Farmers Insurance® Agent in Santa Clarita, CA | Farmers Insurance®"
    cleaned = re.sub(r'^Find a [^|]+Agent in [^|]+\s*[-|]\s*', '', cleaned, flags=re.IGNORECASE)
    
    # Pattern 2: Remove business category prefixes
    # Example: "Used Cars | Albuquerque, NM | One Express Motors LLC"
    cleaned = re.sub(r'^(Used Cars|New Cars|Auto Sales|Car Dealership|Auto Dealership)\s*[-|]\s*', '', cleaned, flags=re.IGNORECASE)
    
    # Pattern 3: Remove location patterns (state abbreviations) - more aggressive
    # Example: "Albuquerque, NM | One Express Motors LLC"
    cleaned = re.sub(r'\s*[-|]\s*[A-Za-z\s,]+(?:NM|CA|TX|NY|FL|IL|PA|OH|GA|NC|MI|NJ|VA|WA|AZ|CO|TN|IN|MO|MD|MN|WI|AL|SC|LA|KY|OR|OK|CT|IA|MS|AR|KS|UT|NV|WV|NE|ID|HI|NH|ME|MT|RI|DE|SD|ND|AK|VT|WY)\s*[-|]?', '', cleaned, flags=re.IGNORECASE)
    
    # Pattern 4: Remove city, state patterns at the beginning
    # Example: "New York, NY | Business Solutions Inc"
    cleaned = re.sub(r'^[A-Za-z\s,]+(?:NM|CA|TX|NY|FL|IL|PA|OH|GA|NC|MI|NJ|VA|WA|AZ|CO|TN|IN|MO|MD|MN|WI|AL|SC|LA|KY|OR|OK|CT|IA|MS|AR|KS|UT|NV|WV|NE|ID|HI|NH|ME|MT|RI|DE|SD|ND|AK|VT|WY)\s*[-|]\s*', '', cleaned, flags=re.IGNORECASE)
    
    # Pattern 5: Remove common suffixes
    # Example: "A&R Auto Sales LLC - Home"
    cleaned = re.sub(r'\s*[-|]\s*(Home|Welcome|Official Site|Official Website|Dealership|Auto|Cars).*$', '', cleaned, flags=re.IGNORECASE)
    
    # Pattern 6: Remove "Welcome to" prefixes
    # Example: "Welcome to ABC Company | Official Site"
    cleaned = re.sub(r'^Welcome to\s+', '', cleaned, flags=re.IGNORECASE)
    
    # Pattern 7: Remove "Official Site" and similar
    cleaned = re.sub(r'\s*[-|]\s*Official Site.*$', '', cleaned, flags=re.IGNORECASE)
    
    # Clean up extra separators
    cleaned = re.sub(r'\s*[-|]\s*$', '', cleaned)
    cleaned = re.sub(r'^\s*[-|]\s*', '', cleaned)
    
    # Final cleanup
    cleaned = cleaned.strip()
    
    return cleaned

def fix_current_upload():
    """Fix the current upload data using improved logic"""
    try:
        print("🔧 Fixing current upload data...")
        db_manager = DatabaseManager()
        
        upload_id = "b1eb86d5-6293-4d90-b3f4-d093b42c0c7d"
        websites = db_manager.get_websites_by_file_upload_id(upload_id)
        
        print(f"Found {len(websites)} websites in upload {upload_id}")
        
        for i, website in enumerate(websites):
            print(f"\n🔄 Fixing website #{i+1}:")
            print(f"   Current company name: '{website.get('companyName', 'N/A')}'")
            print(f"   Current industry: '{website.get('industry', 'N/A')}'")
            print(f"   Current business type: '{website.get('businessType', 'N/A')}'")
            
            # Clean company name
            old_company_name = website.get('companyName', '')
            new_company_name = clean_company_name(old_company_name)
            
            print(f"   Cleaned company name: '{new_company_name}'")
            
            # Determine correct industry and business type
            new_industry = 'Automotive'  # Based on the URL and content
            new_business_type = 'Auto Dealership'  # Based on the content
            
            print(f"   New industry: '{new_industry}'")
            print(f"   New business type: '{new_business_type}'")
            
            # Update the website data
            try:
                conn = db_manager.get_connection()
                cursor = conn.cursor()
                
                cursor.execute("""
                    UPDATE websites
                    SET "companyName" = %s, "industry" = %s, "businessType" = %s, 
                        "generatedMessage" = %s, "messageStatus" = %s, "updatedAt" = CURRENT_TIMESTAMP
                    WHERE id = %s
                """, (new_company_name, new_industry, new_business_type, "", "PENDING", website.get('id')))
                
                conn.commit()
                cursor.close()
                conn.close()
                
                print(f"   ✅ Successfully updated website data")
                print(f"   ✅ Message cleared and ready for regeneration")
                
            except Exception as e:
                print(f"   ❌ Failed to update website: {e}")
                import traceback
                traceback.print_exc()
        
        print(f"\n📊 Summary:")
        print(f"   Fixed data for {len(websites)} websites")
        print(f"   Messages cleared and ready for regeneration")
        print(f"   Next step: Run AI message generation task for upload '{upload_id}'")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    fix_current_upload()

