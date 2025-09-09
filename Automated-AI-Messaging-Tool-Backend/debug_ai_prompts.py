#!/usr/bin/env python3

def debug_ai_prompts():
    # Read the message_generator.py file
    with open('ai/message_generator.py', 'r') as f:
        content = f.read()
    
    # Ultra-simple debug prompts to test basic functionality
    debug_templates = '''
        self.message_templates = {
            'general': {
                'prompt': 'Write a business message for {company_name} in {industry} industry. Keep it professional.',
                'max_tokens': 200
            },
            'partnership': {
                'prompt': 'Write a partnership proposal for {company_name} in {industry} industry.',
                'max_tokens': 200
            },
            'support': {
                'prompt': 'Write a support message for {company_name} in {industry} industry.',
                'max_tokens': 200
            },
            'custom': {
                'prompt': 'Custom message for {company_name} in {industry} industry. Requirements: {custom_prompt}.',
                'max_tokens': 200
            }
        }
'''
    
    # Find and replace the existing message_templates
    if 'self.message_templates = {' in content:
        # Find the start of message_templates
        start_marker = 'self.message_templates = {'
        start_pos = content.find(start_marker)
        
        if start_pos != -1:
            # Find the end of message_templates (look for the closing brace)
            brace_count = 0
            end_pos = start_pos
            
            for i in range(start_pos, len(content)):
                if content[i] == '{':
                    brace_count += 1
                elif content[i] == '}':
                    brace_count -= 1
                    if brace_count == 0:
                        end_pos = i + 1
                        break
            
            # Replace the entire message_templates section
            old_templates = content[start_pos:end_pos]
            new_content = content.replace(old_templates, debug_templates.strip())
            
            # Write the updated content back
            with open('ai/message_generator.py', 'w') as f:
                f.write(new_content)
            
            print("✅ Debug AI prompts applied successfully!")
            print("🎯 Now using ultra-simple prompts for testing")
            print("🔍 This will help identify the core issue")
            return True
        else:
            print("❌ Could not find message_templates section")
            return False
    else:
        print("❌ Could not find message_templates in the file")
        return False

if __name__ == "__main__":
    debug_ai_prompts()
