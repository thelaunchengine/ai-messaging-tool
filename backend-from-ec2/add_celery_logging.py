#!/usr/bin/env python3

def add_celery_logging():
    # Read the scraping_tasks.py file
    with open('celery_tasks/scraping_tasks.py', 'r') as f:
        content = f.read()
    
    # Add comprehensive logging to generate_messages_task
    old_task_start = '''    def generate_messages_task(self, website_data: List[Dict], message_type: str = "general", file_upload_id: str = None, user_id: str = None):

    """
    Generate AI messages for scraped websites
    """
    try:
        logger.info(f"Starting message generation for {len(website_data)} websites")'''
    
    new_task_start = '''    def generate_messages_task(self, website_data: List[Dict], message_type: str = "general", file_upload_id: str = None, user_id: str = None):

    """
    Generate AI messages for scraped websites
    """
    try:
        logger.info(f"Starting message generation for {len(website_data)} websites")
        logger.info(f"🔍 DEBUG: website_data type: {type(website_data)}")
        logger.info(f"🔍 DEBUG: website_data length: {len(website_data) if website_data else 'None'}")
        if website_data and len(website_data) > 0:
            logger.info(f"🔍 DEBUG: First website data sample: {website_data[0]}")
            logger.info(f"🔍 DEBUG: First website keys: {list(website_data[0].keys()) if website_data[0] else 'None'}")'''
    
    if old_task_start in content:
        content = content.replace(old_task_start, new_task_start)
        print("✅ Added comprehensive logging to task start")
    else:
        print("⚠️  Could not find task start to replace")
    
    # Add logging before AI generation
    old_ai_call = '''            try:
                # Generate message based on website data
                message, confidence = generate_ai_message(website, message_type)'''
    
    new_ai_call = '''            try:
                # Generate message based on website data
                logger.info(f"🔍 DEBUG: About to call generate_ai_message for website: {website.get('websiteUrl', 'Unknown URL')}")
                logger.info(f"🔍 DEBUG: Website data being passed: {website}")
                logger.info(f"🔍 DEBUG: Message type: {message_type}")
                message, confidence = generate_ai_message(website, message_type)
                logger.info(f"🔍 DEBUG: generate_ai_message returned - message: {type(message)}, confidence: {confidence}")
                if message:
                    logger.info(f"🔍 DEBUG: Message content preview: {message[:100]}...")
                else:
                    logger.info(f"🔍 DEBUG: Message is None or empty")'''
    
    if old_ai_call in content:
        content = content.replace(old_ai_call, new_ai_call)
        print("✅ Added comprehensive logging to AI generation call")
    else:
        print("⚠️  Could not find AI generation call to replace")
    
    # Add logging to the generate_ai_message function
    old_function_start = '''def generate_ai_message(website_data: Dict, message_type: str = "general") -> Tuple[str, float]:
    """
    Generate AI message using enhanced Gemini with predefined message integration
    """
    try:
        # Initialize database manager and AI generator
        db_manager = DatabaseManager()
        ai_generator = GeminiMessageGenerator(db_manager=db_manager)'''
    
    new_function_start = '''def generate_ai_message(website_data: Dict, message_type: str = "general") -> Tuple[str, float]:
    """
    Generate AI message using enhanced Gemini with predefined message integration
    """
    try:
        logger.info(f"🔍 DEBUG: generate_ai_message called with website_data type: {type(website_data)}")
        logger.info(f"🔍 DEBUG: website_data keys: {list(website_data.keys()) if website_data else 'None'}")
        logger.info(f"🔍 DEBUG: message_type: {message_type}")
        
        # Initialize database manager and AI generator
        logger.info(f"🔍 DEBUG: Initializing DatabaseManager...")
        db_manager = DatabaseManager()
        logger.info(f"🔍 DEBUG: DatabaseManager initialized successfully")
        
        logger.info(f"🔍 DEBUG: Initializing GeminiMessageGenerator...")
        ai_generator = GeminiMessageGenerator(db_manager=db_manager)
        logger.info(f"🔍 DEBUG: GeminiMessageGenerator initialized successfully")'''
    
    if old_function_start in content:
        content = content.replace(old_function_start, new_function_start)
        print("✅ Added comprehensive logging to generate_ai_message function")
    else:
        print("⚠️  Could not find generate_ai_message function start to replace")
    
    # Add logging before hybrid message generation
    old_hybrid_call = '''        # Generate message with hybrid approach
        result = ai_generator.hybrid_message_generation(website_data, message_type)'''
    
    new_hybrid_call = '''        # Generate message with hybrid approach
        logger.info(f"🔍 DEBUG: About to call hybrid_message_generation...")
        logger.info(f"🔍 DEBUG: ai_generator type: {type(ai_generator)}")
        logger.info(f"🔍 DEBUG: ai_generator.predefined_integration: {ai_generator.predefined_integration}")
        
        result = ai_generator.hybrid_message_generation(website_data, message_type)
        logger.info(f"🔍 DEBUG: hybrid_message_generation returned: {result}")
        logger.info(f"🔍 DEBUG: Result type: {type(result)}")
        if isinstance(result, dict):
            logger.info(f"🔍 DEBUG: Result keys: {list(result.keys()) if result else 'None'}")'''
    
    if old_hybrid_call in content:
        content = content.replace(old_hybrid_call, new_hybrid_call)
        print("✅ Added comprehensive logging to hybrid message generation call")
    else:
        print("⚠️  Could not find hybrid message generation call to replace")
    
    # Add logging to the return statement
    old_return = '''        return result['message'], result['confidence_score']'''
    
    new_return = '''        logger.info(f"🔍 DEBUG: Extracting message and confidence from result...")
        if 'message' in result:
            logger.info(f"🔍 DEBUG: Message found in result: {type(result['message'])}")
            logger.info(f"🔍 DEBUG: Message content: {result['message'][:100] if result['message'] else 'None'}...")
        else:
            logger.info(f"🔍 DEBUG: No 'message' key in result!")
            
        if 'confidence_score' in result:
            logger.info(f"🔍 DEBUG: Confidence score found: {result['confidence_score']}")
        else:
            logger.info(f"🔍 DEBUG: No 'confidence_score' key in result!")
            
        return result['message'], result['confidence_score']'''
    
    if old_return in content:
        content = content.replace(old_return, new_return)
        print("✅ Added comprehensive logging to return statement")
    else:
        print("⚠️  Could not find return statement to replace")
    
    # Write the updated content back
    with open('celery_tasks/scraping_tasks.py', 'w') as f:
        f.write(content)
    
    print("\n🎯 Comprehensive logging added to Celery tasks!")
    print("🔄 Please restart the backend services to apply the changes")
    return True

if __name__ == "__main__":
    add_celery_logging()
