#!/usr/bin/env python3
import sys
import os

# Add the backend directory to Python path
sys.path.append('/home/xb3353/Automated-AI-Messaging-Tool-Backend')

from database.database_manager import DatabaseManager
from ai.message_generator import GeminiMessageGenerator

def debug_ai_generation():
    try:
        print("🔍 Debugging AI generation issue...")
        
        # Initialize database manager
        db_manager = DatabaseManager()
        
        # Get the problematic websites
        upload_id = "79c0c6e3-a67a-453e-91e8-940e43e25ab8"
        websites = db_manager.get_websites_by_file_upload_id(upload_id)
        
        print(f"Found {len(websites)} websites in upload {upload_id}")
        
        for i, website in enumerate(websites):
            if "Please provide me with the Company name" in website.get('generatedMessage', ''):
                print(f"\n🔴 Problematic Website #{i+1}:")
                print(f"   ID: {website.get('id')}")
                print(f"   Company Name: '{website.get('companyName', 'N/A')}'")
                print(f"   Industry: '{website.get('industry', 'N/A')}'")
                print(f"   Business Type: '{website.get('businessType', 'N/A')}'")
                print(f"   Website URL: '{website.get('websiteUrl', 'N/A')}'")
                print(f"   About Us Length: {len(website.get('aboutUsContent', ''))}")
                print(f"   About Us Preview: '{website.get('aboutUsContent', '')[:200]}...'")
                print(f"   Current Message: '{website.get('generatedMessage', '')[:100]}...'")
                
                # Try to regenerate with current data
                print(f"\n🔄 Attempting to regenerate message...")
                try:
                    ai_generator = GeminiMessageGenerator(db_manager=db_manager)
                    
                    # Prepare website data for AI generation
                    ai_data = {
                        'companyName': website.get('companyName', ''),
                        'industry': website.get('industry', ''),
                        'businessType': website.get('businessType', ''),
                        'aboutUsContent': website.get('aboutUsContent', '')
                    }
                    
                    print(f"   Data being sent to AI:")
                    print(f"     Company Name: '{ai_data['companyName']}'")
                    print(f"     Industry: '{ai_data['industry']}'")
                    print(f"     Business Type: '{ai_data['businessType']}'")
                    print(f"     About Us (length): {len(ai_data['aboutUsContent'])}")
                    
                    # Generate new message
                    new_message, confidence = ai_generator.generate_message(ai_data, "general")
                    
                    if new_message and "Please provide me with the Company name" not in new_message:
                        print(f"   ✅ Successfully generated new message:")
                        print(f"   '{new_message[:200]}...'")
                        print(f"   Confidence: {confidence}")
                        
                        # Update the website with the new message
                        update_success = db_manager.update_website_message(
                            website.get('id'),
                            new_message,
                            "GENERATED"
                        )
                        
                        if update_success:
                            print(f"   ✅ Updated website message in database")
                        else:
                            print(f"   ❌ Failed to update website message in database")
                    else:
                        print(f"   ❌ AI still generating problematic message:")
                        print(f"   '{new_message[:200]}...'")
                        
                        # The issue might be with the data itself - let's try to fix it
                        print(f"\n🔧 Attempting to fix the data...")
                        
                        # Extract better company name from the title
                        company_name = website.get('companyName', '')
                        if '|' in company_name:
                            # Take the part after the pipe, which is usually the company name
                            company_name = company_name.split('|')[-1].strip()
                        elif 'Find a' in company_name and 'Agent' in company_name:
                            # For "Find a Farmers Insurance® Agent in Santa Clarita, CA"
                            company_name = "Farmers Insurance"
                        
                        # Better industry and business type detection
                        about_us = website.get('aboutUsContent', '').lower()
                        industry = website.get('industry', '')
                        business_type = website.get('businessType', '')
                        
                        if 'insurance' in about_us or 'insurance' in company_name.lower():
                            industry = 'Insurance'
                            business_type = 'Insurance Services'
                        elif 'auto sales' in about_us or 'auto sales' in company_name.lower():
                            industry = 'Automotive'
                            business_type = 'Auto Sales'
                        
                        print(f"   Fixed Company Name: '{company_name}'")
                        print(f"   Fixed Industry: '{industry}'")
                        print(f"   Fixed Business Type: '{business_type}'")
                        
                        # Update the website data
                        update_data = {
                            'companyName': company_name,
                            'industry': industry,
                            'businessType': business_type
                        }
                        
                        update_success = db_manager.update_website(website.get('id'), update_data)
                        if update_success:
                            print(f"   ✅ Updated website data in database")
                            
                            # Try generating again with fixed data
                            fixed_data = {
                                'companyName': company_name,
                                'industry': industry,
                                'businessType': business_type,
                                'aboutUsContent': website.get('aboutUsContent', '')
                            }
                            
                            new_message, confidence = ai_generator.generate_message(fixed_data, "general")
                            
                            if new_message and "Please provide me with the Company name" not in new_message:
                                print(f"   ✅ Successfully generated message with fixed data:")
                                print(f"   '{new_message[:200]}...'")
                                
                                # Update the website with the new message
                                message_success = db_manager.update_website_message(
                                    website.get('id'),
                                    new_message,
                                    "GENERATED"
                                )
                                
                                if message_success:
                                    print(f"   ✅ Updated website message with fixed data")
                                else:
                                    print(f"   ❌ Failed to update website message")
                            else:
                                print(f"   ❌ Still generating problematic message even with fixed data")
                        else:
                            print(f"   ❌ Failed to update website data in database")
                        
                except Exception as e:
                    print(f"   ❌ Error regenerating message: {e}")
                    import traceback
                    traceback.print_exc()
                
                print(f"\n" + "="*80)
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    debug_ai_generation()
