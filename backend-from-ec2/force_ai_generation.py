#!/usr/bin/env python3

def force_ai_generation():
    # Read the message_generator.py file
    with open("ai/message_generator.py", "r") as f:
        content = f.read()
    
    # Simple replacement to prioritize AI generation
    old_text = "if predefined_messages:"
    new_text = "if False and predefined_messages:  # DISABLED: Force AI generation"
    
    if old_text in content:
        new_content = content.replace(old_text, new_text)
        
        # Write the updated content back
        with open("ai/message_generator.py", "w") as f:
            f.write(new_content)
        
        print("✅ AI generation priority enhanced successfully!")
        print("🎯 System now forces pure AI generation")
        print("🚀 Predefined messages disabled")
        return True
    else:
        print("❌ Could not find predefined_messages check")
        return False

if __name__ == "__main__":
    force_ai_generation()
