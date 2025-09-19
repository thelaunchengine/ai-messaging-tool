#!/usr/bin/env python3

def add_message_generator_logging():
    # Read the message_generator.py file
    with open('ai/message_generator.py', 'r') as f:
        content = f.read()
    
    # Add logging to hybrid_message_generation method
    old_hybrid_start = '''    def hybrid_message_generation(self, website_data: Dict, message_type: str) -> Dict[str, Any]:
        """Generate message using both AI and predefined templates"""
        
        # Get relevant predefined messages
        predefined_messages = self.predefined_integration.get_relevant_predefined_messages(website_data)'''
    
    new_hybrid_start = '''    def hybrid_message_generation(self, website_data: Dict, message_type: str) -> Dict[str, Any]:
        """Generate message using both AI and predefined templates"""
        
        import logging
        logger = logging.getLogger(__name__)
        
        logger.info(f"🔍 DEBUG: hybrid_message_generation called with message_type: {message_type}")
        logger.info(f"🔍 DEBUG: website_data keys: {list(website_data.keys()) if website_data else 'None'}")
        logger.info(f"🔍 DEBUG: self.predefined_integration: {self.predefined_integration}")
        
        # Get relevant predefined messages
        try:
            predefined_messages = self.predefined_integration.get_relevant_predefined_messages(website_data)
            logger.info(f"🔍 DEBUG: predefined_messages retrieved: {len(predefined_messages) if predefined_messages else 0} messages")
        except Exception as e:
            logger.error(f"🔍 DEBUG: Error getting predefined messages: {e}")
            predefined_messages = []'''
    
    if old_hybrid_start in content:
        content = content.replace(old_hybrid_start, new_hybrid_start)
        print("✅ Added comprehensive logging to hybrid_message_generation start")
    else:
        print("⚠️  Could not find hybrid_message_generation start to replace")
    
    # Add logging to the fallback AI generation
    old_fallback = '''        # Fallback to pure AI generation
        message, confidence = self.generate_pure_ai_message(website_data, message_type)'''
    
    new_fallback = '''        # Fallback to pure AI generation
        logger.info(f"🔍 DEBUG: Falling back to pure AI generation...")
        try:
            message, confidence = self.generate_pure_ai_message(website_data, message_type)
            logger.info(f"🔍 DEBUG: generate_pure_ai_message returned - message: {type(message)}, confidence: {confidence}")
            if message:
                logger.info(f"🔍 DEBUG: AI message content preview: {message[:100]}...")
            else:
                logger.info(f"🔍 DEBUG: AI message is None or empty")
        except Exception as e:
            logger.error(f"🔍 DEBUG: Error in generate_pure_ai_message: {e}")
            import traceback
            logger.error(f"🔍 DEBUG: Traceback: {traceback.format_exc()}")
            message, confidence = "", 0.0'''
    
    if old_fallback in content:
        content = content.replace(old_fallback, new_fallback)
        print("✅ Added comprehensive logging to fallback AI generation")
    else:
        print("⚠️  Could not find fallback AI generation to replace")
    
    # Add logging to generate_pure_ai_message method
    old_pure_ai_start = '''    def generate_pure_ai_message(self, website_data: Dict, message_type: str) -> Tuple[str, float]:
        """Generate message using pure AI approach"""
        
        template = self.message_templates.get(message_type, self.message_templates['general'])'''
    
    new_pure_ai_start = '''    def generate_pure_ai_message(self, website_data: Dict, message_type: str) -> Tuple[str, float]:
        """Generate message using pure AI approach"""
        
        import logging
        logger = logging.getLogger(__name__)
        
        logger.info(f"🔍 DEBUG: generate_pure_ai_message called with message_type: {message_type}")
        logger.info(f"🔍 DEBUG: Available message_templates: {list(self.message_templates.keys())}")
        
        template = self.message_templates.get(message_type, self.message_templates['general'])
        logger.info(f"🔍 DEBUG: Selected template: {template}")'''
    
    if old_pure_ai_start in content:
        content = content.replace(old_pure_ai_start, new_pure_ai_start)
        print("✅ Added comprehensive logging to generate_pure_ai_message start")
    else:
        print("⚠️  Could not find generate_pure_ai_message start to replace")
    
    # Add logging to prompt generation
    old_prompt = '''        prompt = template['prompt'].format(
            company_name=website_data.get('companyName', ''),
            industry=website_data.get('industry', ''),
            business_type=website_data.get('businessType', ''),
            about_us_content=website_data.get('aboutUsContent', '')[:500]
        )'''
    
    new_prompt = '''        logger.info(f"🔍 DEBUG: Formatting prompt with website data...")
        logger.info(f"🔍 DEBUG: companyName: {website_data.get('companyName', 'NOT_FOUND')}")
        logger.info(f"🔍 DEBUG: industry: {website_data.get('industry', 'NOT_FOUND')}")
        logger.info(f"🔍 DEBUG: businessType: {website_data.get('businessType', 'NOT_FOUND')}")
        logger.info(f"🔍 DEBUG: aboutUsContent: {website_data.get('aboutUsContent', 'NOT_FOUND')[:100] if website_data.get('aboutUsContent') else 'NOT_FOUND'}...")
        
        prompt = template['prompt'].format(
            company_name=website_data.get('companyName', ''),
            industry=website_data.get('industry', ''),
            business_type=website_data.get('businessType', ''),
            about_us_content=website_data.get('aboutUsContent', '')[:500]
        )
        logger.info(f"🔍 DEBUG: Generated prompt: {prompt[:200]}...")'''
    
    if old_prompt in content:
        content = content.replace(old_prompt, new_prompt)
        print("✅ Added comprehensive logging to prompt generation")
    else:
        print("⚠️  Could not find prompt generation to replace")
    
    # Add logging to Gemini API call
    old_api_call = '''        try:
            response = self.model.generate_content(prompt)
            message = response.text'''
    
    new_api_call = '''        try:
            logger.info(f"🔍 DEBUG: Calling Gemini API with prompt...")
            logger.info(f"🔍 DEBUG: Model type: {type(self.model)}")
            response = self.model.generate_content(prompt)
            logger.info(f"🔍 DEBUG: Gemini API response received")
            message = response.text
            logger.info(f"🔍 DEBUG: Response text type: {type(message)}")
            logger.info(f"🔍 DEBUG: Response text length: {len(message) if message else 0}")'''
    
    if old_api_call in content:
        content = content.replace(old_api_call, new_api_call)
        print("✅ Added comprehensive logging to Gemini API call")
    else:
        print("⚠️  Could not find Gemini API call to replace")
    
    # Write the updated content back
    with open('ai/message_generator.py', 'w') as f:
        f.write(content)
    
    print("\n🎯 Comprehensive logging added to message generator!")
    print("🔄 Please restart the backend services to apply the changes")
    return True

if __name__ == "__main__":
    add_message_generator_logging()
