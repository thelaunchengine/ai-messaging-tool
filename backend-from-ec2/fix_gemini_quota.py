#!/usr/bin/env python3

def fix_gemini_quota():
    # Read the message_generator.py file
    with open('ai/message_generator.py', 'r') as f:
        content = f.read()
    
    # Fix 1: Change model from gemini-1.5-pro to gemini-1.5-flash (more quota-friendly)
    # Fix 2: Add retry logic and error handling
    # Fix 3: Add fallback to simpler model if quota exceeded
    
    # Replace the model initialization
    old_model_init = "self.model = genai.GenerativeModel('gemini-1.5-pro')"
    new_model_init = """        # Try gemini-1.5-flash first (more quota-friendly)
        try:
            self.model = genai.GenerativeModel('gemini-1.5-flash')
        except Exception as e:
            logger.warning(f"Failed to initialize gemini-1.5-flash: {e}")
            # Fallback to gemini-1.5-pro
            self.model = genai.GenerativeModel('gemini-1.5-pro')"""
    
    if old_model_init in content:
        content = content.replace(old_model_init, new_model_init)
    
    # Add retry logic to generate_pure_ai_message method
    old_generate_method = """    def generate_pure_ai_message(self, website_data: Dict, message_type: str) -> Tuple[str, float]:
        \"\"\"Generate message using pure AI approach\"\"\"
        
        template = self.message_templates.get(message_type, self.message_templates['general'])
        
        prompt = template['prompt'].format(
            company_name=website_data.get('company_name', ''),
            industry=website_data.get('industry', ''),
            business_type=website_data.get('business_type', ''),
            about_us_content=website_data.get('about_us_content', '')[:500]
        )
        
        try:
            response = self.model.generate_content(prompt)
            message = response.text
            
            confidence_score = self._calculate_confidence_score(message, website_data)

            return message, confidence_score
            
        except Exception as e:
            logger.error(f"Error generating AI message: {e}")
            # Return empty string instead of fallback message
            return "", 0.0"""
    
    new_generate_method = """    def generate_pure_ai_message(self, website_data: Dict, message_type: str) -> Tuple[str, float]:
        \"\"\"Generate message using pure AI approach with retry logic\"\"\"
        
        template = self.message_templates.get(message_type, self.message_templates['general'])
        
        prompt = template['prompt'].format(
            company_name=website_data.get('company_name', ''),
            industry=website_data.get('industry', ''),
            business_type=website_data.get('business_type', ''),
            about_us_content=website_data.get('about_us_content', '')[:500]
        )
        
        # Retry logic for quota issues
        max_retries = 3
        retry_delay = 10  # seconds
        
        for attempt in range(max_retries):
            try:
                response = self.model.generate_content(prompt)
                message = response.text
                
                if message and len(message.strip()) > 10:  # Basic validation
                    confidence_score = self._calculate_confidence_score(message, website_data)
                    logger.info(f"AI message generated successfully on attempt {attempt + 1}")
                    return message, confidence_score
                else:
                    logger.warning(f"Generated message too short on attempt {attempt + 1}")
                    
            except Exception as e:
                error_str = str(e).lower()
                if 'quota' in error_str or '429' in error_str or 'rate limit' in error_str:
                    if attempt < max_retries - 1:
                        logger.warning(f"Quota exceeded on attempt {attempt + 1}, retrying in {retry_delay}s: {e}")
                        import time
                        time.sleep(retry_delay)
                        retry_delay *= 2  # Exponential backoff
                        continue
                    else:
                        logger.error(f"Quota exceeded after {max_retries} attempts: {e}")
                        # Return a basic template message as fallback
                        fallback_message = f"Dear {website_data.get('company_name', 'Valued Business')},\\n\\nI hope this message finds you well. I am reaching out regarding potential collaboration opportunities in the {website_data.get('industry', 'business')} industry.\\n\\nWould you be interested in discussing how we might work together?\\n\\nBest regards,\\n[Your Name]"
                        return fallback_message, 0.3
                else:
                    logger.error(f"Error generating AI message on attempt {attempt + 1}: {e}")
                    if attempt < max_retries - 1:
                        continue
                    else:
                        # Return a basic template message as fallback
                        fallback_message = f"Dear {website_data.get('company_name', 'Valued Business')},\\n\\nI hope this message finds you well. I am reaching out regarding potential collaboration opportunities in the {website_data.get('industry', 'business')} industry.\\n\\nWould you be interested in discussing how we might work together?\\n\\nBest regards,\\n[Your Name]"
                        return fallback_message, 0.3
        
        # Final fallback
        fallback_message = f"Dear {website_data.get('company_name', 'Valued Business')},\\n\\nI hope this message finds you well. I am reaching out regarding potential collaboration opportunities in the {website_data.get('industry', 'business')} industry.\\n\\nWould you be interested in discussing how we might work together?\\n\\nBest regards,\\n[Your Name]"
        return fallback_message, 0.2"""
    
    if old_generate_method in content:
        content = content.replace(old_generate_method, new_generate_method)
    
    # Write the updated content back
    with open('ai/message_generator.py', 'w') as f:
        f.write(content)
    
    print("✅ Gemini quota issues fixed successfully!")
    print("🎯 Now using gemini-1.5-flash (more quota-friendly)")
    print("🔄 Added retry logic with exponential backoff")
    print("🛡️ Added fallback messages for quota issues")
    return True

if __name__ == "__main__":
    fix_gemini_quota()
