#!/usr/bin/env python3

def simplify_ai_prompts():
    # Read the message_generator.py file
    with open('ai/message_generator.py', 'r') as f:
        content = f.read()
    
    # Simplified AI prompts that are short but effective
    simplified_templates = '''
        self.message_templates = {
            'general': {
                'prompt': 'Create a unique business outreach message for {company_name} ({industry} industry, {business_type} business). Use their about us info: {about_us_content}. Make it personal and specific to their business. Keep it professional, 150-200 words.',
                'max_tokens': 300
            },
            'partnership': {
                'prompt': 'Write a partnership proposal for {company_name} ({industry} industry). Based on their business: {about_us_content}. Explain specific partnership benefits for their industry. Keep it strategic, 180-250 words.',
                'max_tokens': 400
            },
            'support': {
                'prompt': 'Create a support outreach message for {company_name} ({industry} industry, {business_type}). Using their info: {about_us_content}. Offer relevant support solutions for their business type. Keep it helpful, 150-200 words.',
                'max_tokens': 300
            },
            'custom': {
                'prompt': 'Custom message for {company_name} ({industry} industry). Requirements: {custom_prompt}. Company info: {about_us_content}. Make it specific to their business. Keep it professional, 150-250 words.',
                'max_tokens': 400
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
            new_content = content.replace(old_templates, simplified_templates.strip())
            
            # Write the updated content back
            with open('ai/message_generator.py', 'w') as f:
                f.write(new_content)
            
            print("✅ AI prompts simplified successfully!")
            print("🎯 Now using short, focused prompts")
            print("🚀 Messages will still be unique and contextual")
            return True
        else:
            print("❌ Could not find message_templates section")
            return False
    else:
        print("❌ Could not find message_templates in the file")
        return False

if __name__ == "__main__":
    simplify_ai_prompts()
