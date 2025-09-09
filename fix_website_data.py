#!/usr/bin/env python3
import sys
import os

# Add the backend directory to Python path
sys.path.append('/home/xb3353/Automated-AI-Messaging-Tool-Backend')

from database.database_manager import DatabaseManager

def fix_website_data():
    try:
        print("🔧 Fixing website data...")
        
        # Initialize database manager
        db_manager = DatabaseManager()
        
        # Define the fixes for each problematic website
        website_fixes = [
            {
                'id': '40e733dd-774a-4798-889e-9744824ef54a',
                'current_name': 'Find a Farmers Insurance® Agent in Santa Clarita, CA | Farmers Insurance®',
                'fixes': {
                    'companyName': 'Farmers Insurance',
                    'industry': 'Insurance',
                    'businessType': 'Insurance Services'
                }
            },
            {
                'id': 'aae08cca-a243-4dec-a7bc-cf1a46ee370a',
                'current_name': 'A&R Auto Sales LLC',
                'fixes': {
                    'companyName': 'A&R Auto Sales LLC',  # This one is correct
                    'industry': 'Automotive',
                    'businessType': 'Auto Sales'
                }
            }
        ]
        
        for fix in website_fixes:
            print(f"\n🔄 Fixing website: {fix['current_name']}")
            print(f"   ID: {fix['id']}")
            
            try:
                # Use direct SQL update
                conn = db_manager.get_connection()
                cursor = conn.cursor()
                
                # Update the website data
                cursor.execute("""
                    UPDATE websites 
                    SET "companyName" = %s, "industry" = %s, "businessType" = %s, "updatedAt" = CURRENT_TIMESTAMP
                    WHERE id = %s
                """, (
                    fix['fixes']['companyName'],
                    fix['fixes']['industry'],
                    fix['fixes']['businessType'],
                    fix['id']
                ))
                
                # Clear the problematic generated message so it can be regenerated
                cursor.execute("""
                    UPDATE websites 
                    SET "generatedMessage" = %s, "messageStatus" = %s, "updatedAt" = CURRENT_TIMESTAMP
                    WHERE id = %s
                """, ("", "PENDING", fix['id']))
                
                conn.commit()
                cursor.close()
                conn.close()
                
                print(f"   ✅ Updated website data:")
                for key, value in fix['fixes'].items():
                    print(f"     {key}: '{value}'")
                print(f"   ✅ Cleared problematic message - ready for regeneration")
                
            except Exception as e:
                print(f"   ❌ Failed to update website: {e}")
        
        print(f"\n📊 Summary:")
        print(f"   Fixed data for {len(website_fixes)} problematic websites")
        print(f"   Messages cleared and ready for regeneration")
        print(f"   Next step: Run AI message generation task for upload '79c0c6e3-a67a-453e-91e8-940e43e25ab8'")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    fix_website_data()
