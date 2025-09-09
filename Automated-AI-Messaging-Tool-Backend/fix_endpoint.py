#!/usr/bin/env python3

def add_endpoint():
    # Read the main.py file
    with open('main.py', 'r') as f:
        content = f.read()
    
    # Find the position after the start_message_generation function
    search_text = """    except Exception as e:
        logger.error(f"Error starting message generation: {e}")
        raise HTTPException(status_code=500, detail=str(e))"""
    
    # The new endpoint to add (properly formatted)
    new_endpoint = '''

@app.post("/api/workflow/trigger-ai-generation", response_model=TaskResponse)
async def trigger_ai_generation_for_file_upload(request: Dict[str, Any]):
    """Trigger AI message generation for all websites in a file upload"""
    try:
        file_upload_id = request.get("file_upload_id")
        message_type = request.get("message_type", "general")
        custom_prompt = request.get("custom_prompt", "")
        ai_model = request.get("ai_model", "gemini")
        
        if not file_upload_id:
            raise HTTPException(status_code=400, detail="File upload ID is required")
        
        # Get all websites for this file upload
        db_manager = DatabaseManager()
        websites = db_manager.get_websites_by_file_upload_id(file_upload_id)
        
        if not websites:
            raise HTTPException(status_code=404, detail=f"No websites found for file upload ID: {file_upload_id}")
        
        # Filter websites that have been successfully scraped
        scraped_websites = [w for w in websites if w.get("scrapingStatus") == "COMPLETED"]
        
        if not scraped_websites:
            raise HTTPException(status_code=400, detail="No successfully scraped websites found. Please wait for scraping to complete.")
        
        # Prepare website data for AI generation
        website_data = []
        for website in scraped_websites:
            website_data.append({
                "id": website.get("id"),
                "company_name": website.get("companyName", ""),
                "industry": website.get("industry", ""),
                "business_type": website.get("businessType", ""),
                "about_us_content": website.get("aboutUsContent", ""),
                "websiteUrl": website.get("websiteUrl", ""),
                "scraping_status": website.get("scrapingStatus"),
                "message_status": website.get("messageStatus"),
                "fileUploadId": website.get("fileUploadId"),
                "userId": website.get("userId")
            })
        
        # Start Celery task for AI message generation
        task = generate_messages_task.delay(website_data, message_type, file_upload_id, request.get("user_id", "default_user"))
        
        logger.info(f"Started AI message generation task {task.id} for {len(website_data)} websites from file upload {file_upload_id}")
        
        return TaskResponse(
            task_id=task.id,
            status="started",
            message=f"AI message generation started for {len(website_data)} websites from file upload {file_upload_id}"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error triggering AI generation for file upload: {e}")
        raise HTTPException(status_code=500, detail=str(e))

'''
    
    # Insert the new endpoint after the search text
    if search_text in content:
        new_content = content.replace(search_text, search_text + new_endpoint)
        
        # Write the updated content back
        with open('main.py', 'w') as f:
            f.write(new_content)
        
        print("✅ Endpoint added successfully!")
        return True
    else:
        print("❌ Could not find the insertion point")
        return False

if __name__ == "__main__":
    add_endpoint()
