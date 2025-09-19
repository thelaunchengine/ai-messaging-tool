#!/usr/bin/env python3

import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def debug_database():
    print("🔍 DEBUGGING DATABASE AND MESSAGE GENERATOR")
    print("===========================================")
    
    try:
        # Step 1: Test database manager import
        print("\n1️⃣ Testing Database Manager Import...")
        try:
            from database.database_manager import DatabaseManager
            print("✅ Successfully imported DatabaseManager")
        except Exception as e:
            print(f"❌ Error importing DatabaseManager: {e}")
            import traceback
            traceback.print_exc()
            return False
        
        # Step 2: Test database manager initialization
        print("\n2️⃣ Testing Database Manager Initialization...")
        try:
            db_manager = DatabaseManager()
            print("✅ Successfully created DatabaseManager instance")
        except Exception as e:
            print(f"❌ Error creating DatabaseManager: {e}")
            import traceback
            traceback.print_exc()
            return False
        
        # Step 3: Test message generator import
        print("\n3️⃣ Testing Message Generator Import...")
        try:
            from ai.message_generator import GeminiMessageGenerator
            print("✅ Successfully imported GeminiMessageGenerator")
        except Exception as e:
            print(f"❌ Error importing GeminiMessageGenerator: {e}")
            import traceback
            traceback.print_exc()
            return False
        
        # Step 4: Test message generator initialization with db_manager
        print("\n4️⃣ Testing Message Generator Initialization...")
        try:
            ai_generator = GeminiMessageGenerator(db_manager=db_manager)
            print("✅ Successfully created GeminiMessageGenerator with db_manager")
            
            # Check if predefined_integration is properly set
            if ai_generator.predefined_integration:
                print("✅ predefined_integration is properly set")
            else:
                print("❌ predefined_integration is None - this is the problem!")
                return False
                
        except Exception as e:
            print(f"❌ Error creating GeminiMessageGenerator: {e}")
            import traceback
            traceback.print_exc()
            return False
        
        # Step 5: Test actual message generation
        print("\n5️⃣ Testing Actual Message Generation...")
        try:
            website_data = {
                'company_name': 'Test Company',
                'industry': 'Technology',
                'business_type': 'SaaS',
                'about_us_content': 'We are a technology company.'
            }
            
            result = ai_generator.hybrid_message_generation(website_data, 'general')
            print(f"✅ Message generation successful!")
            print(f"📝 Result: {result}")
            
            if result and 'message' in result and result['message']:
                print(f"✅ Message content: {result['message'][:100]}...")
                print(f"✅ Method: {result.get('method', 'unknown')}")
                print(f"✅ Confidence: {result.get('confidence_score', 'unknown')}")
            else:
                print("❌ No message in result")
                return False
                
        except Exception as e:
            print(f"❌ Error in message generation: {e}")
            import traceback
            traceback.print_exc()
            return False
        
        print("\n🎯 ALL DATABASE TESTS PASSED! The issue is elsewhere.")
        return True
        
    except Exception as e:
        print(f"\n💥 CRITICAL ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    debug_database()
