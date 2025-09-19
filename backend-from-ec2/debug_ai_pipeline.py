#!/usr/bin/env python3

import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def debug_ai_pipeline():
    print("🔍 DEBUGGING AI GENERATION PIPELINE")
    print("===================================")
    
    try:
        # Step 1: Test environment variables
        print("\n1️⃣ Testing Environment Variables...")
        gemini_key = os.getenv('GEMINI_API_KEY')
        if gemini_key:
            print(f"✅ GEMINI_API_KEY: {gemini_key[:20]}...")
        else:
            print("❌ GEMINI_API_KEY not found")
            return False
        
        # Step 2: Test Gemini API import
        print("\n2️⃣ Testing Gemini API Import...")
        try:
            import google.generativeai as genai
            print("✅ Successfully imported google.generativeai")
        except Exception as e:
            print(f"❌ Error importing Gemini: {e}")
            return False
        
        # Step 3: Test Gemini API configuration
        print("\n3️⃣ Testing Gemini API Configuration...")
        try:
            genai.configure(api_key=gemini_key)
            print("✅ Successfully configured Gemini API")
        except Exception as e:
            print(f"❌ Error configuring Gemini API: {e}")
            return False
        
        # Step 4: Test model creation
        print("\n4️⃣ Testing Model Creation...")
        try:
            model = genai.GenerativeModel('gemini-1.5-flash')
            print("✅ Successfully created Gemini model")
        except Exception as e:
            print(f"❌ Error creating model: {e}")
            return False
        
        # Step 5: Test simple content generation
        print("\n5️⃣ Testing Simple Content Generation...")
        try:
            response = model.generate_content("Write 'Hello World'")
            message = response.text
            print(f"✅ Simple generation successful: {message}")
        except Exception as e:
            print(f"❌ Error in simple generation: {e}")
            return False
        
        # Step 6: Test actual prompt template
        print("\n6️⃣ Testing Actual Prompt Template...")
        try:
            # Simulate the actual prompt used in the system
            template = "Write a business message for {company_name} in {industry} industry. Keep it professional."
            prompt = template.format(
                company_name="Example Corp",
                industry="Technology"
            )
            print(f"📝 Generated prompt: {prompt}")
            
            response = model.generate_content(prompt)
            message = response.text
            print(f"✅ Business message generation successful: {message[:100]}...")
            
            if message and len(message.strip()) > 10:
                print("✅ Message validation passed")
            else:
                print("❌ Message validation failed - message too short or empty")
                return False
                
        except Exception as e:
            print(f"❌ Error in business message generation: {e}")
            return False
        
        # Step 7: Test the actual message generator class
        print("\n7️⃣ Testing Message Generator Class...")
        try:
            from ai.message_generator import GeminiMessageGenerator
            
            # Create instance
            ai_generator = GeminiMessageGenerator()
            print("✅ Successfully created GeminiMessageGenerator instance")
            
            # Test with sample data
            website_data = {
                'company_name': 'Test Company',
                'industry': 'Technology',
                'business_type': 'SaaS',
                'about_us_content': 'We are a technology company.'
            }
            
            # Test hybrid message generation
            result = ai_generator.hybrid_message_generation(website_data, 'general')
            print(f"✅ Hybrid message generation result: {result}")
            
            if result and 'message' in result and result['message']:
                print(f"✅ Message generated successfully: {result['message'][:100]}...")
                print(f"✅ Method: {result.get('method', 'unknown')}")
                print(f"✅ Confidence: {result.get('confidence_score', 'unknown')}")
            else:
                print("❌ No message in result")
                return False
                
        except Exception as e:
            print(f"❌ Error in message generator class: {e}")
            import traceback
            traceback.print_exc()
            return False
        
        print("\n🎯 ALL TESTS PASSED! AI Generation Pipeline is working correctly.")
        return True
        
    except Exception as e:
        print(f"\n💥 CRITICAL ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    debug_ai_pipeline()
