#!/usr/bin/env python3

def fix_ai_endpoint():
    """Fix the existing generate-messages endpoint to use real AI generation"""
    
    # Read the current main.py file
    with open('main.py', 'r') as f:
        content = f.read()
    
    # Find the old generate-messages endpoint
    old_endpoint = '''@app.post("/api/generate-messages")
async def generate_messages(website_data: List[Dict[str, Any]]):
    """Generate AI messages for individual websites"""
    try:
        if not website_data:
            raise HTTPException(status_code=400, detail="Website data is required")
        
        logger.info(f"Generating messages for {len(website_data)} websites")
        
        # Initialize AI generator
        db_manager = DatabaseManager()
        ai_generator = GeminiMessageGenerator(db_manager=db_manager)
        
        results = []
        for website in website_data:
            try:
                # Extract website information
                website_id = website.get('id')
                company_name = website.get('companyName') or website.get('company_name', 'Unknown Company')
                industry = website.get('industry', 'Unknown Industry')
                business_type = website.get('businessType') or website.get('business_type', 'Unknown Business Type')
                about_us_content = website.get('aboutUsContent') or website.get('about_us_content', '')
                
                # Create a standardized website object for AI generation
                website_obj = {
                    'id': website_id,
                    'company_name': company_name,
                    'industry': industry,
                    'business_type': business_type,
                    'about_us_content': about_us_content,
                    'website_url': website.get('websiteUrl') or website.get('website_url', '')
                }
                
                # Generate message using AI
                message, confidence = ai_generator.hybrid_message_generation(
                    website_obj, 
                    message_type="general"
                )
                
                if message:
                    # Update database if website_id is provided
                    if website_id:
                        try:
                            db_manager.update_website_message(
                                website_id=website_id,
                                generatedMessage=message,
                                messageStatus="GENERATED"
                            )
                            logger.info(f"Updated website {website_id} with generated message")
                        except Exception as db_error:
                            logger.warning(f"Could not update database for website {website_id}: {db_error}")
                    
                    results.append({
                        'website_id': website_id,
                        'url': website_obj['website_url'],
                        'message': message,
                        'confidence': confidence,
                        'success': True
                    })
                else:
                    results.append({
                        'website_id': website_id,
                        'url': website_obj['website_url'],
                        'message': None,
                        'error': 'Failed to generate message',
                        'success': False
                    })
                    
            except Exception as e:
                logger.error(f"Error generating message for website {website.get('id', 'unknown')}: {e}")
                results.append({
                    'website_id': website.get('id'),
                    'url': website.get('websiteUrl') or website.get('website_url', ''),
                    'message': None,
                    'error': str(e),
                    'success': False
                })
        
        # Count successful generations
        successful_count = len([r for r in results if r['success']])
        failed_count = len([r for r in results if not r['success']])
        
        logger.info(f"Message generation completed. Success: {successful_count}, Failed: {failed_count}")
        
        return {
            "success": True,
            "messages": results,
            "total_websites": len(website_data),
            "successful_count": successful_count,
            "failed_count": failed_count
        }
        
    except Exception as e:
        logger.error(f"Error in generate_messages endpoint: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))'''
    
    # New endpoint that uses real AI generation
    new_endpoint = '''@app.post("/api/generate-messages")
async def generate_messages(website_data: List[Dict[str, Any]]):
    """Generate real AI messages using Gemini API"""
    try:
        if not website_data:
            raise HTTPException(status_code=400, detail="Website data is required")
        
        logger.info(f"Generating real AI messages for {len(website_data)} websites using Gemini")
        
        # Initialize AI generator
        db_manager = DatabaseManager()
        ai_generator = GeminiMessageGenerator(db_manager=db_manager)
        
        results = []
        for website in website_data:
            try:
                # Extract website information
                company_name = website.get('companyName') or website.get('company_name', 'Unknown Company')
                industry = website.get('industry', 'Unknown Industry')
                business_type = website.get('businessType') or website.get('business_type', 'Unknown Business Type')
                about_us_content = website.get('aboutUsContent') or website.get('about_us_content', '')
                
                logger.info(f"Processing website: {company_name} - {industry} - {business_type}")
                
                # Create a standardized website object for AI generation
                website_obj = {
                    'company_name': company_name,
                    'industry': industry,
                    'business_type': business_type,
                    'about_us_content': about_us_content,
                    'website_url': website.get('websiteUrl') or website.get('website_url', '')
                }
                
                # Generate message using real AI
                result = ai_generator.hybrid_message_generation(
                    website_obj, 
                    message_type="general"
                )
                
                # Extract message and confidence from result
                message = result.get('message', '')
                confidence = result.get('confidence_score', 0.0)
                
                if message and message.strip():
                    results.append({
                        'website_id': website.get('id'),
                        'url': website_obj['website_url'],
                        'message': message,
                        'confidence': confidence,
                        'success': True,
                        'is_ai_generated': True
                    })
                    logger.info(f"Successfully generated AI message for {company_name}")
                else:
                    results.append({
                        'website_id': website.get('id'),
                        'url': website_obj['website_url'],
                        'message': None,
                        'error': 'AI generation returned empty message',
                        'success': False,
                        'is_ai_generated': False
                    })
                    logger.warning(f"AI generation returned empty message for {company_name}")
                    
            except Exception as e:
                logger.error(f"Error generating AI message for website {website.get('id', 'unknown')}: {e}")
                results.append({
                    'website_id': website.get('id'),
                    'url': website.get('websiteUrl') or website.get('website_url', ''),
                    'message': None,
                    'error': str(e),
                    'success': False,
                    'is_ai_generated': False
                })
        
        # Count successful generations
        successful_count = len([r for r in results if r['success']])
        failed_count = len([r for r in results if not r['success']])
        
        logger.info(f"Real AI message generation completed. Success: {successful_count}, Failed: {failed_count}")
        
        return {
            "success": True,
            "messages": results,
            "total_websites": len(website_data),
            "successful_count": successful_count,
            "failed_count": failed_count,
            "ai_model": "gemini-1.5-flash"
        }
        
    except Exception as e:
        logger.error(f"Error in generate_messages endpoint: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))'''
    
    # Replace the old endpoint with the new one
    if old_endpoint in content:
        content = content.replace(old_endpoint, new_endpoint)
        print("✅ Successfully replaced the old AI endpoint with real AI generation")
        
        # Write the updated content back
        with open('main.py', 'w') as f:
            f.write(content)
        
        print("✅ Updated main.py with real AI generation")
    else:
        print("❌ Could not find the old endpoint to replace")
        print("The file might have been modified or the endpoint structure is different")

if __name__ == "__main__":
    fix_ai_endpoint()
