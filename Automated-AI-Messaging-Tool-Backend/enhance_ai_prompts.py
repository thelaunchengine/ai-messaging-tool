#!/usr/bin/env python3

def enhance_ai_prompts():
    # Read the message_generator.py file
    with open('ai/message_generator.py', 'r') as f:
        content = f.read()
    
    # Enhanced AI prompts that will generate truly dynamic content
    enhanced_templates = '''
        self.message_templates = {
            'general': {
                'prompt': """
                You are an expert business development professional. Analyze this company's information and generate a unique, personalized outreach message.

                COMPANY INFORMATION:
                - Company Name: {company_name}
                - Industry: {industry}
                - Business Type: {business_type}
                - About Us Content: {about_us_content}

                INSTRUCTIONS:
                1. Analyze their industry and business type to understand their market position
                2. Extract key insights from their about us content
                3. Identify potential collaboration opportunities based on their business
                4. Create a message that shows genuine understanding of their specific business
                5. Make it clear you've researched their company, not using a generic template
                6. Include specific references to their industry, business type, or about us content
                7. Propose relevant collaboration opportunities based on their business model
                8. Keep it professional but conversational (150-200 words)

                IMPORTANT: Do NOT use generic phrases like "I came across your business" or "I believe there could be opportunities". Instead, reference specific details from their company information to show genuine interest and understanding.

                Generate a completely unique message that demonstrates you understand their specific business context.
                """,
                'max_tokens': 400
            },
            'partnership': {
                'prompt': """
                You are a strategic partnership specialist. Analyze this company and create a compelling partnership proposal.

                COMPANY INFORMATION:
                - Company Name: {company_name}
                - Industry: {industry}
                - Business Type: {business_type}
                - About Us Content: {about_us_content}

                INSTRUCTIONS:
                1. Deeply analyze their industry landscape and business model
                2. Identify specific partnership opportunities based on their business type
                3. Reference concrete details from their about us content
                4. Explain how a partnership could benefit their specific business
                5. Show understanding of their market challenges and opportunities
                6. Propose specific collaboration areas relevant to their industry
                7. Demonstrate you've done your homework on their company
                8. Keep it strategic and value-focused (180-250 words)

                CRITICAL: Avoid generic partnership language. Instead, reference their specific industry challenges, business model, or market position to show genuine strategic thinking.
                """,
                'max_tokens': 500
            },
            'support': {
                'prompt': """
                You are a customer support specialist. Analyze this company and create a personalized support outreach message.

                COMPANY INFORMATION:
                - Company Name: {company_name}
                - Industry: {industry}
                - Business Type: {business_type}
                - About Us Content: {about_us_content}

                INSTRUCTIONS:
                1. Understand their business context and typical support needs
                2. Identify industry-specific challenges they might face
                3. Reference their business type to offer relevant support solutions
                4. Show understanding of their operational context
                5. Offer specific support services relevant to their industry
                6. Demonstrate you understand their business model
                7. Keep it helpful and solution-focused (150-200 words)

                ESSENTIAL: Don't use generic support language. Instead, reference their specific industry needs or business model to show you understand their support requirements.
                """,
                'max_tokens': 400
            },
            'custom': {
                'prompt': """
                You are a business communication expert. Create a personalized message based on the custom requirements.

                COMPANY INFORMATION:
                - Company Name: {company_name}
                - Industry: {industry}
                - Business Type: {business_type}
                - About Us Content: {about_us_content}

                CUSTOM REQUIREMENTS:
                {custom_prompt}

                INSTRUCTIONS:
                1. Analyze their business context thoroughly
                2. Incorporate the custom requirements naturally
                3. Reference specific details from their company information
                4. Show genuine understanding of their business
                5. Create a message that feels personal and researched
                6. Avoid generic language - make it specific to their company
                7. Follow the custom requirements while maintaining professionalism
                8. Keep it contextual and relevant (150-250 words)

                CRITICAL: This must be a unique message that shows you've analyzed their specific business, not a template with variables substituted.
                """,
                'max_tokens': 500
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
            new_content = content.replace(old_templates, enhanced_templates.strip())
            
            # Write the updated content back
            with open('ai/message_generator.py', 'w') as f:
                f.write(new_content)
            
            print("✅ AI prompts enhanced successfully!")
            print("🎯 Now using truly dynamic, contextual AI generation")
            print("🚀 Messages will be unique based on company analysis")
            return True
        else:
            print("❌ Could not find message_templates section")
            return False
    else:
        print("❌ Could not find message_templates in the file")
        return False

if __name__ == "__main__":
    enhance_ai_prompts()
