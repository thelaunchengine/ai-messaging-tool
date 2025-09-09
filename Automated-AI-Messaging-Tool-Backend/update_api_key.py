#!/usr/bin/env python3

def update_api_key():
    old_key = "AIzaSyCRuMCZJgkAfIG54850ZFxvHJg3DIoC3_c"
    new_key = "AIzaSyANDNgkwSUbg5xXyGYIJIcs2W-REhNjk6I"
    
    print(f"🔄 Updating Gemini API Key...")
    print(f"📤 Old Key: {old_key[:20]}...")
    print(f"📥 New Key: {new_key[:20]}...")
    
    # Update .env file
    try:
        with open('.env', 'r') as f:
            content = f.read()
        
        if old_key in content:
            content = content.replace(old_key, new_key)
            with open('.env', 'w') as f:
                f.write(content)
            print("✅ .env file updated successfully")
        else:
            print("⚠️  Old key not found in .env file")
    except Exception as e:
        print(f"❌ Error updating .env: {e}")
    
    # Update deploy.sh file
    try:
        with open('deploy.sh', 'r') as f:
            content = f.read()
        
        if old_key in content:
            content = content.replace(old_key, new_key)
            with open('deploy.sh', 'w') as f:
                f.write(content)
            print("✅ deploy.sh file updated successfully")
        else:
            print("⚠️  Old key not found in deploy.sh file")
    except Exception as e:
        print(f"❌ Error updating deploy.sh: {e}")
    
    # Update ai/message_generator.py file
    try:
        with open('ai/message_generator.py', 'r') as f:
            content = f.read()
        
        if old_key in content:
            content = content.replace(old_key, new_key)
            with open('ai/message_generator.py', 'w') as f:
                f.write(content)
            print("✅ message_generator.py file updated successfully")
        else:
            print("⚠️  Old key not found in message_generator.py file")
    except Exception as e:
        print(f"❌ Error updating message_generator.py: {e}")
    
    print("\n🎯 API Key update completed!")
    print("🔄 Please restart the backend services to apply the new key")
    return True

if __name__ == "__main__":
    update_api_key()
