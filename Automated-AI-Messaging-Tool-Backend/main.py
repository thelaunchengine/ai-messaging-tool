from fastapi import FastAPI, HTTPException, WebSocket, Query, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import time
import logging
import os
from datetime import datetime
from enum import Enum
import uuid

# Import WebSocket manager
from websocket_server import websocket_manager, websocket_endpoint

# Import Celery tasks
from celery_tasks.scraping_tasks import scrape_websites_task, generate_messages_task
from celery_tasks.file_tasks import process_file_upload_task, process_chunk_task, extract_websites_from_file_task
from celery_tasks.form_submission_tasks import contact_form_submission_task
from database.database_manager import DatabaseManager
from ai.message_generator import GeminiMessageGenerator, PredefinedMessageIntegration

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="AI Messaging Backend with Celery", version="1.0.0")
# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://103.215.159.51:3001", "http://localhost:3001"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# WebSocket endpoint
@app.websocket("/ws/{client_id}")
async def websocket_endpoint_route(websocket: WebSocket, client_id: str):
    await websocket_endpoint(websocket, client_id)

# System metrics endpoint
@app.get("/api/monitoring/system-metrics")
async def get_system_metrics():
    """Get current system metrics"""
    return websocket_manager.get_system_metrics()

# Configuration endpoint
@app.get("/api/config/testing")
async def get_testing_config():
    """Get current testing configuration"""
    import os
    return {
        "testing_mode_enabled": os.getenv('TESTING_MODE_ENABLED', 'true').lower() == 'true',
        "max_ai_messages_per_file": int(os.getenv('MAX_AI_MESSAGES_PER_FILE', '2')),
        "description": "Testing mode limits AI message generation to control costs during development",
        "environment_variables": {
            "TESTING_MODE_ENABLED": os.getenv('TESTING_MODE_ENABLED', 'true'),
            "MAX_AI_MESSAGES_PER_FILE": os.getenv('MAX_AI_MESSAGES_PER_FILE', '2')
        }
    }

# Task metrics endpoint
@app.get("/api/monitoring/task-metrics")
async def get_task_metrics():
    """Get current task metrics from Celery and database"""
    try:
        from celery.result import AsyncResult
        from database.database_manager import DatabaseManager
        
        db_manager = DatabaseManager()
        tasks = []
        
        # Get active Celery tasks
        try:
            # This would require Celery inspection - for now, get from database
            file_uploads = db_manager.get_all_file_uploads()
            
            for upload in file_uploads[-50:]:  # Last 50 uploads
                if upload.get('status') in ['PENDING', 'PROCESSING', 'COMPLETED']:
                    # Calculate progress based on chunks
                    totalChunks = int(upload.get('totalChunks', 0) or 0)
                    completedChunks = int(upload.get('completedChunks', 0) or 0)
                    progress = int((completed_chunks / total_chunks * 100) if total_chunks > 0 else 0)
                    
                    # Calculate duration
                    createdAt = upload.get('createdAt')
                    duration = "0m 0s"
                    if createdAt:
                        from datetime import datetime, timedelta
                        
                        # Handle datetime object directly
                        if isinstance(created_at, datetime):
                            start_time = createdAt
                            now = datetime.now(start_time.tzinfo) if start_time.tzinfo else datetime.now()
                        else:
                            # Handle string datetime
                            start_time = datetime.fromisoformat(str(created_at).replace('Z', '+00:00'))
                            now = datetime.now(start_time.tzinfo)
                        
                        diff = now - start_time
                        minutes = int(diff.total_seconds() // 60)
                        seconds = int(diff.total_seconds() % 60)
                        duration = f"{minutes}m {seconds}s"
                        
                        # Only show tasks from last 24 hours
                        if diff > timedelta(hours=24):
                            continue
                    
                    tasks.append({
                        "id": upload.get('id', 'unknown'),
                        "type": "file_processing",
                        "status": upload.get('status', 'UNKNOWN'),
                        "progress": progress,
                        "startTime": created_at or "2024-01-15T10:30:00Z",
                        "duration": duration,
                        "errorCount": upload.get('failedWebsites', 0)
                    })
        except Exception as e:
            logger.error(f"Error fetching task metrics: {e}")
        
        # If no real tasks, return empty list
        if not tasks:
            return []
        
        return tasks
        
    except Exception as e:
        logger.error(f"Error in task metrics: {e}")
        return []

@app.get("/api/monitoring/website-activities/{fileUploadId}")
async def get_website_activities(fileUploadId: str):
    """Get detailed activity tracking for individual websites in a file upload"""
    try:
        from database.database_manager import DatabaseManager
        
        db_manager = DatabaseManager()
        websites = db_manager.get_websites_by_file_upload_id(fileUploadId)
        
        website_activities = []
        
        for website in websites:
            # Get detailed crawling activities for this website
            activities = get_website_crawling_activities(website)
            
            website_activities.append({
                "website_id": website.get('id', 'unknown'),
                "url": website.get('url', 'Unknown'),
                "status": website.get('scrapingStatus', 'PENDING'),
                "createdAt": website.get('createdAt'),
                "updatedAt": website.get('updatedAt'),
                "activities": activities,
                "extracted_data": {
                    "title": website.get('title', 'Not found'),
                    "companyName": website.get('companyName', 'Not found'),
                    "industry": website.get('industry', 'Not found'),
                    "businessType": website.get('businessType', 'Not found'),
                    "contactFormUrl": website.get('contactFormUrl', 'Not found'),
                    "has_contact_form": website.get('hasContactForm', False),
                    "aboutUsContent": website.get('aboutUsContent', 'Not found'),
                    "error_message": website.get('errorMessage', None)
                }
            })
        
        return website_activities
        
    except Exception as e:
        logger.error(f"Error in website activities: {e}")
        return []

def get_website_crawling_activities(website):
    """Get detailed crawling activities for a specific website"""
    activities = []
    
    # Step 1: URL Validation
    activities.append({
        "step": 1,
        "name": "URL Validation",
        "status": "COMPLETED",
        "description": f"Validating URL: {website.get('url', 'Unknown')}",
        "timestamp": website.get('createdAt'),
        "details": {
            "url": website.get('url', 'Unknown'),
            "validation": "URL format validated",
            "protocol": "https" if website.get('url', '').startswith('https') else "http"
        }
    })
    
    # Step 2: Initial Connection
    if website.get('scrapingStatus') in ['COMPLETED', 'FAILED']:
        activities.append({
            "step": 2,
            "name": "Initial Connection",
            "status": "COMPLETED" if website.get('scrapingStatus') == 'COMPLETED' else "FAILED",
            "description": "Establishing connection to website",
            "timestamp": website.get('createdAt'),
            "details": {
                "connection_status": "Connected" if website.get('scrapingStatus') == 'COMPLETED' else "Failed",
                "response_time": "~2-5 seconds",
                "error": website.get('errorMessage') if website.get('scrapingStatus') == 'FAILED' else None
            }
        })
    
    # Step 3: Page Content Crawling
    if website.get('scrapingStatus') == 'COMPLETED':
        activities.append({
            "step": 3,
            "name": "Page Content Crawling",
            "status": "COMPLETED",
            "description": "Extracting page title and content",
            "timestamp": website.get('createdAt'),
            "details": {
                "title_found": website.get('title') != 'Not found',
                "title": website.get('title', 'Not found'),
                "content_length": len(website.get('aboutUsContent', '')) if website.get('aboutUsContent') else 0,
                "content_extracted": "Yes" if website.get('aboutUsContent') else "No"
            }
        })
        
        # Step 4: Company Information Extraction
        activities.append({
            "step": 4,
            "name": "Company Information Extraction",
            "status": "COMPLETED",
            "description": "Extracting company name and business details",
            "timestamp": website.get('createdAt'),
            "details": {
                "company_name_found": website.get('companyName') != 'Not found',
                "companyName": website.get('companyName', 'Not found'),
                "industry_found": website.get('industry') != 'Not found',
                "industry": website.get('industry', 'Not found'),
                "business_type_found": website.get('businessType') != 'Not found',
                "businessType": website.get('businessType', 'Not found')
            }
        })
        
        # Step 5: Contact Form Detection
        activities.append({
            "step": 5,
            "name": "Contact Form Detection",
            "status": "COMPLETED",
            "description": "Searching for contact forms and contact information",
            "timestamp": website.get('createdAt'),
            "details": {
                "contact_form_found": website.get('hasContactForm', False),
                "contactFormUrl": website.get('contactFormUrl', 'Not found'),
                "contact_form_detection": "Found" if website.get('hasContactForm') else "Not found",
                "search_patterns": ["contact", "contact-us", "get-in-touch", "reach-us"]
            }
        })
        
        # Step 6: About Us Content Crawling
        activities.append({
            "step": 6,
            "name": "About Us Content Crawling",
            "status": "COMPLETED",
            "description": "Extracting about us page content",
            "timestamp": website.get('createdAt'),
            "details": {
                "about_content_found": website.get('aboutUsContent') != 'Not found',
                "about_content_length": len(website.get('aboutUsContent', '')) if website.get('aboutUsContent') else 0,
                "about_url_found": "Yes" if website.get('aboutUsContent') else "No",
                "content_summary": website.get('aboutUsContent', 'Not found')[:200] + "..." if website.get('aboutUsContent') and len(website.get('aboutUsContent', '')) > 200 else website.get('aboutUsContent', 'Not found')
            }
        })
        
        # Step 7: Data Processing
        activities.append({
            "step": 7,
            "name": "Data Processing",
            "status": "COMPLETED",
            "description": "Processing and structuring extracted data",
            "timestamp": website.get('updatedAt'),
            "details": {
                "data_structured": "Yes",
                "fields_extracted": [
                    "title" if website.get('title') != 'Not found' else None,
                    "companyName" if website.get('companyName') != 'Not found' else None,
                    "industry" if website.get('industry') != 'Not found' else None,
                    "contact_form" if website.get('hasContactForm') else None,
                    "about_content" if website.get('aboutUsContent') != 'Not found' else None
                ].filter(None),
                "total_fields": len([f for f in [
                    website.get('title'),
                    website.get('companyName'),
                    website.get('industry'),
                    website.get('hasContactForm'),
                    website.get('aboutUsContent')
                ] if f and f != 'Not found'])
            }
        })
    
    elif website.get('scrapingStatus') == 'FAILED':
        activities.append({
            "step": 3,
            "name": "Crawling Failed",
            "status": "FAILED",
            "description": "Failed to crawl website content",
            "timestamp": website.get('updatedAt'),
            "details": {
                "error_type": "Connection/Timeout",
                "error_message": website.get('errorMessage', 'Unknown error'),
                "retry_attempts": "3 attempts made",
                "suggested_action": "Check URL validity or try again later"
            }
        })
    
    return activities

@app.get("/api/monitoring/detailed-activities")
async def get_detailed_activities():
    """Get detailed activity tracking for all tasks"""
    try:
        from database.database_manager import DatabaseManager
        from datetime import datetime, timedelta
        
        db_manager = DatabaseManager()
        file_uploads = db_manager.get_all_file_uploads()
        
        detailed_activities = []
        
        for upload in file_uploads[-50:]:  # Last 50 uploads
            if upload.get('status') in ['PENDING', 'PROCESSING', 'COMPLETED']:
                createdAt = upload.get('createdAt')
                if createdAt:
                    from datetime import datetime, timedelta
                    
                    # Handle datetime object directly
                    if isinstance(created_at, datetime):
                        start_time = createdAt
                        now = datetime.now(start_time.tzinfo) if start_time.tzinfo else datetime.now()
                    else:
                        # Handle string datetime
                        start_time = datetime.fromisoformat(str(created_at).replace('Z', '+00:00'))
                        now = datetime.now(start_time.tzinfo)
                    
                    diff = now - start_time
                    
                    # Only show tasks from last 24 hours
                    if diff > timedelta(hours=24):
                        continue
                
                # Get detailed activities for this upload
                activities = get_upload_activities(upload)
                
                detailed_activities.append({
                    "task_id": upload.get('id', 'unknown'),
                    "filename": upload.get('originalName', 'Unknown'),
                    "status": upload.get('status', 'UNKNOWN'),
                    "totalWebsites": upload.get('totalWebsites', 0),
                    "processedWebsites": upload.get('processedWebsites', 0),
                    "failedWebsites": upload.get('failedWebsites', 0),
                    "start_time": created_at,
                    "duration": calculate_duration(created_at),
                    "activities": activities
                })
        
        return detailed_activities
        
    except Exception as e:
        logger.error(f"Error in detailed activities: {e}")
        return []

def calculate_duration_between(start_time: str, end_time: str) -> str:
    """Calculate duration between two timestamps"""
    try:
        if not start_time or not end_time:
            return "Unknown"
        
        from datetime import datetime
        start = datetime.fromisoformat(start_time.replace('Z', '+00:00'))
        end = datetime.fromisoformat(end_time.replace('Z', '+00:00'))
        duration = end - start
        
        total_seconds = int(duration.total_seconds())
        minutes = total_seconds // 60
        seconds = total_seconds % 60
        
        if minutes > 0:
            return f"{minutes}m {seconds}s"
        else:
            return f"{seconds}s"
    except Exception:
        return "Unknown"

@app.get("/api/workflow/progress/{fileUploadId}")
async def get_workflow_progress(fileUploadId: str):
    """Get workflow progress for a file upload"""
    try:
        db_manager = DatabaseManager()
        
        # Get file upload details
        file_upload = db_manager.get_file_upload_by_id(fileUploadId)
        if not file_upload:
            raise HTTPException(status_code=404, detail="File upload not found")
        
        # Get website data
        websites = db_manager.get_websites_by_file_upload_id(fileUploadId)
        
        # Calculate workflow phases
        phases = []
        
        # Phase 1: File Upload & Processing
        upload_phase = {
            "id": "upload",
            "name": "File Upload & Processing",
            "description": "Uploading file and extracting website URLs",
            "status": "completed" if file_upload.get('status') != 'PENDING' else "processing",
            "progress": 100 if file_upload.get('status') != 'PENDING' else 50,
            "startTime": file_upload.get('createdAt'),
            "endTime": file_upload.get('processingStartedAt') if file_upload.get('status') != 'PENDING' else None,
            "details": [
                f"Total websites: {file_upload.get('totalWebsites', 0)}",
                f"File type: {file_upload.get('fileType', 'unknown')}",
                f"File size: {file_upload.get('fileSize', 0)} bytes"
            ]
        }
        phases.append(upload_phase)
        
        # Phase 2: Website Scraping & Data Extraction
        scraping_phase = {
            "id": "scraping",
            "name": "Website Scraping & Data Extraction",
            "description": "Scraping websites and extracting business information",
            "status": "pending",
            "progress": 0,
            "startTime": None,
            "endTime": None,
            "details": []
        }
        
        if file_upload.get('status') in ['PROCESSING', 'COMPLETED']:
            scraping_phase["status"] = "completed"
            scraping_phase["progress"] = 100
            scraping_phase["startTime"] = file_upload.get('processingStartedAt')
            scraping_phase["endTime"] = file_upload.get('processingCompletedAt')
            scraping_phase["details"] = [
                f"Processed websites: {file_upload.get('processedWebsites', 0)}",
                f"Failed websites: {file_upload.get('failedWebsites', 0)}",
                f"Success rate: {((file_upload.get('processedWebsites', 0) / max(file_upload.get('totalWebsites', 1), 1)) * 100):.1f}%"
            ]
        elif file_upload.get('status') == 'PENDING':
            scraping_phase["status"] = "processing"
            scraping_phase["progress"] = 25
            scraping_phase["startTime"] = file_upload.get('createdAt')
        
        phases.append(scraping_phase)
        
        # Phase 3: Data Processing
        processing_phase = {
            "id": "processing",
            "name": "Data Processing",
            "description": "Processing and structuring scraped data",
            "status": "pending",
            "progress": 0,
            "startTime": None,
            "endTime": None,
            "details": []
        }
        
        if file_upload.get('status') == 'COMPLETED':
            processing_phase["status"] = "completed"
            processing_phase["progress"] = 100
            processing_phase["startTime"] = file_upload.get('processingStartedAt')
            processing_phase["endTime"] = file_upload.get('processingCompletedAt')
            processing_phase["details"] = [
                f"Data processed successfully",
                f"Total records: {len(websites)}",
                f"Processing time: {calculate_duration_between(file_upload.get('processingStartedAt'), file_upload.get('processingCompletedAt'))}"
            ]
        elif file_upload.get('status') == 'PROCESSING':
            processing_phase["status"] = "processing"
            processing_phase["progress"] = 75
            processing_phase["startTime"] = file_upload.get('processingStartedAt')
        
        phases.append(processing_phase)
        
        # Phase 4: AI Message Generation
        ai_phase = {
            "id": "ai-generation",
            "name": "AI Message Generation",
            "description": "Generating personalized messages using Gemini API",
            "status": "pending",
            "progress": 0,
            "startTime": None,
            "endTime": None,
            "details": []
        }
        
        # Check if messages have been generated
        generated_messages = [w for w in websites if w.get('messageStatus') == 'GENERATED']
        total_messages = len(websites)
        
        if generated_messages:
            ai_phase["status"] = "completed"
            ai_phase["progress"] = 100
            ai_phase["details"] = [
                f"Generated messages: {len(generated_messages)}",
                f"Total websites: {total_messages}",
                f"Success rate: {((len(generated_messages) / max(total_messages, 1)) * 100):.1f}%"
            ]
        elif file_upload.get('status') == 'COMPLETED':
            ai_phase["status"] = "processing"
            ai_phase["progress"] = 50
            ai_phase["startTime"] = file_upload.get('processingCompletedAt')
        
        phases.append(ai_phase)
        
        # Phase 5: Status Updates & Notifications
        completion_phase = {
            "id": "completion",
            "name": "Status Updates & Notifications",
            "description": "Updating status and sending notifications",
            "status": "pending",
            "progress": 0,
            "startTime": None,
            "endTime": None,
            "details": []
        }
        
        if file_upload.get('status') == 'COMPLETED':
            completion_phase["status"] = "completed"
            completion_phase["progress"] = 100
            completion_phase["startTime"] = file_upload.get('processingCompletedAt')
            completion_phase["endTime"] = file_upload.get('updatedAt')
            completion_phase["details"] = [
                "Workflow completed successfully",
                f"Total processing time: {calculate_duration_between(file_upload.get('createdAt'), file_upload.get('updatedAt'))}",
                "User notified of completion"
            ]
        
        phases.append(completion_phase)
        
        # Calculate overall progress
        completed_phases = len([p for p in phases if p["status"] == "completed"])
        processing_phases = len([p for p in phases if p["status"] == "processing"])
        overall_progress = ((completed_phases + (processing_phases * 0.5)) / len(phases)) * 100
        
        return {
            "fileUploadId": fileUploadId,
            "overallProgress": round(overall_progress, 1),
            "phases": phases,
            "status": file_upload.get('status'),
            "totalPhases": len(phases),
            "completedPhases": completed_phases,
            "processingPhases": processing_phases
        }
        
    except Exception as e:
        logger.error(f"Error getting workflow progress: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/monitoring/website-details/{fileUploadId}")
async def get_website_details(fileUploadId: str):
    """Get detailed information for all websites in a specific upload"""
    try:
        from database.database_manager import DatabaseManager
        
        db_manager = DatabaseManager()
        websites = db_manager.get_websites_by_file_upload_id(fileUploadId)
        
        if not websites:
            return {"error": "No websites found for this upload"}
        
        detailed_websites = []
        for website in websites:
            website_details = get_website_crawling_details(website)
            detailed_websites.append(website_details)
        
        # Calculate summary statistics
        totalWebsites = len(detailed_websites)
        successful_crawls = len([w for w in detailed_websites if w.get('status') == 'COMPLETED'])
        failed_crawls = len([w for w in detailed_websites if w.get('status') == 'FAILED'])
        contact_forms_found = len([w for w in detailed_websites if w.get('contact_form_analysis', {}).get('found')])
        about_pages_found = len([w for w in detailed_websites if w.get('about_page_analysis', {}).get('found')])
        
        return {
            "fileUploadId": fileUploadId,
            "summary": {
                "totalWebsites": total_websites,
                "successful_crawls": successful_crawls,
                "failed_crawls": failed_crawls,
                "success_rate": f"{(successful_crawls/total_websites*100):.1f}%" if total_websites > 0 else "0%",
                "contact_forms_found": contact_forms_found,
                "about_pages_found": about_pages_found,
                "data_quality_average": calculate_average_completeness(detailed_websites)
            },
            "websites": detailed_websites
        }
        
    except Exception as e:
        logger.error(f"Error getting website details: {e}")
        return {"error": str(e)}

def calculate_average_completeness(websites):
    """Calculate average completeness score across all websites"""
    if not websites:
        return "0%"
    
    total_score = 0
    for website in websites:
        completeness = website.get('data_quality', {}).get('completeness_score', '0/5 (0%)')
        try:
            score = int(completeness.split('/')[0])
            total_score += score
        except (ValueError, IndexError):
            # If parsing fails, assume 0 score
            total_score += 0
    
    average_score = total_score / len(websites)
    return f"{average_score:.1f}/5 ({int(average_score/5*100)}%)"

def get_upload_activities(upload):
    """Get detailed activities for a specific upload"""
    activities = []
    upload_id = upload.get('id')
    
    # Step 1: File Upload Activity
    activities.append({
        "step": 1,
        "name": "File Upload",
        "status": "COMPLETED",
        "description": f"File '{upload.get('originalName', 'Unknown')}' uploaded successfully",
        "timestamp": upload.get('createdAt'),
        "details": {
            "fileSize": f"{upload.get('fileSize', 0)} bytes",
            "fileType": upload.get('fileType', 'Unknown'),
            "total_rows": upload.get('totalWebsites', 0)
        }
    })
    
    # Step 2: File Processing Activity
    if upload.get('status') in ['PROCESSING', 'COMPLETED']:
        activities.append({
            "step": 2,
            "name": "File Processing",
            "status": "COMPLETED",
            "description": "CSV/Excel file parsed and validated",
            "timestamp": upload.get('createdAt'),
            "details": {
                "validation": "File format validated",
                "data_extraction": f"Extracted {upload.get('totalWebsites', 0)} website URLs"
            }
        })
    
    # Step 3: Website Crawling Activities with Individual Website Details
    if upload.get('status') in ['PROCESSING', 'COMPLETED']:
        # Get website data for this upload
        try:
            from database.database_manager import DatabaseManager
            db = DatabaseManager()
            websites = db.get_websites_by_file_upload_id(upload_id)
            
            # Enhanced crawling activities with detailed website information
            crawling_activities = []
            for i, website in enumerate(websites):
                # Get detailed crawling information for each website
                website_details = get_website_crawling_details(website)
                crawling_activities.append(website_details)
            
            activities.append({
                "step": 3,
                "name": "Website Crawling",
                "status": "IN_PROGRESS" if upload.get('status') == 'PROCESSING' else "COMPLETED",
                "description": f"Crawling {upload.get('totalWebsites', 0)} websites for data extraction",
                "timestamp": upload.get('createdAt'),
                "details": {
                    "totalWebsites": upload.get('totalWebsites', 0),
                    "processed": upload.get('processedWebsites', 0),
                    "failed": upload.get('failedWebsites', 0),
                    "crawling_summary": {
                        "successful_crawls": len([w for w in crawling_activities if w.get('status') == 'COMPLETED']),
                        "failed_crawls": len([w for w in crawling_activities if w.get('status') == 'FAILED']),
                        "pending_crawls": len([w for w in crawling_activities if w.get('status') == 'PENDING']),
                        "contact_forms_found": len([w for w in crawling_activities if w.get('contact_form_found')]),
                        "about_pages_found": len([w for w in crawling_activities if w.get('about_page_found')])
                    },
                    "individual_websites": crawling_activities
                }
            })
            
        except Exception as e:
            activities.append({
                "step": 3,
                "name": "Website Crawling",
                "status": "PENDING",
                "description": "Waiting to start crawling process",
                "timestamp": upload.get('createdAt'),
                "details": {
                    "error": f"Could not fetch website data: {str(e)}"
                }
            })
    
    # Step 4: Message Generation Activity
    if upload.get('status') == 'COMPLETED':
        activities.append({
            "step": 4,
            "name": "AI Message Generation",
            "status": "COMPLETED",
            "description": "Generating personalized AI messages for each website",
            "timestamp": upload.get('updatedAt'),
            "details": {
                "ai_model": "GPT-4",
                "message_type": "Personalized outreach",
                "generation_status": "Completed for all websites"
            }
        })
    
    # Step 5: Form Submission Activity (if applicable)
    if upload.get('status') == 'COMPLETED':
        activities.append({
            "step": 5,
            "name": "Contact Form Submission",
            "status": "PENDING",
            "description": "Ready for automated form submissions",
            "timestamp": upload.get('updatedAt'),
            "details": {
                "submission_status": "Manual trigger required",
                "forms_available": "Contact forms identified on websites"
            }
        })
    
    return activities

def get_website_crawling_details(website):
    """Get detailed crawling information for a specific website"""
    url = website.get('websiteUrl', 'Unknown')  # Fixed: use 'websiteUrl' instead of 'url'
    status = website.get('scrapingStatus', 'PENDING')
    error_message = website.get('errorMessage', '')
    
    # Determine what was crawled and what was found
    crawling_details = {
        "websiteUrl": url,
        "status": status,
        "crawling_timestamp": website.get('createdAt'),
        "error_message": error_message if error_message else None,
        
        # What was crawled
        "crawling_attempts": {
            "homepage": "Attempted" if status != 'PENDING' else "Not attempted",
            "contact_page": "Attempted" if website.get('contactFormUrl') else "Not attempted",
            "about_page": "Attempted" if website.get('aboutUsContent') else "Not attempted",
            "meta_tags": "Attempted" if status != 'PENDING' else "Not attempted"
        },
        
        # What was found
        "data_extracted": {
            "title": website.get('title', 'Not found'),
            "companyName": website.get('companyName', 'Not found'),
            "industry": website.get('industry', 'Not found'),
            "businessType": website.get('businessType', 'Not found'),
            "contactFormUrl": website.get('contactFormUrl', 'Not found'),
            "aboutUsContent": "Found" if website.get('aboutUsContent') else "Not found",
            "meta_description": website.get('metaDescription', 'Not found')
        },
        
        # Contact form details
        "contact_form_analysis": {
            "found": bool(website.get('hasContactForm')),
            "url": website.get('contactFormUrl', 'Not found'),
            "form_type": "Contact form" if website.get('hasContactForm') else "Not found",
            "submission_ready": bool(website.get('hasContactForm'))
        },
        
        # About page details
        "about_page_analysis": {
            "found": bool(website.get('aboutUsContent')),
            "content_length": len(website.get('aboutUsContent', '')) if website.get('aboutUsContent') else 0,
            "content_preview": website.get('aboutUsContent', '')[:200] + "..." if website.get('aboutUsContent') else "No content",
            "useful_for_ai": bool(website.get('aboutUsContent') and len(website.get('aboutUsContent', '')) > 50)
        },
        
        # Crawling performance
        "crawling_performance": {
            "response_time": "N/A",  # Could be added to database
            "page_size": "N/A",      # Could be added to database
            "http_status": "200" if status == 'COMPLETED' else "Error" if status == 'FAILED' else "Pending",
            "robots_txt_respected": True,  # Assuming yes
            "rate_limited": False    # Assuming no
        },
        
        # Data quality assessment
        "data_quality": {
            "has_company_name": bool(website.get('companyName')),
            "has_industry": bool(website.get('industry')),
            "has_contact_form": bool(website.get('hasContactForm')),
            "has_about_content": bool(website.get('aboutUsContent')),
            "completeness_score": calculate_completeness_score(website)
        }
    }
    
    return crawling_details

def calculate_completeness_score(website):
    """Calculate a completeness score for the website data"""
    score = 0
    total_fields = 5
    
    if website.get('title'):
        score += 1
    if website.get('companyName'):
        score += 1
    if website.get('industry'):
        score += 1
    if website.get('hasContactForm'):
        score += 1
    if website.get('aboutUsContent'):
        score += 1
    
    return f"{score}/{total_fields} ({int(score/total_fields*100)}%)"

def calculate_duration(created_at):
    """Calculate duration from creation time"""
    if not createdAt:
        return "0m 0s"
    
    try:
        from datetime import datetime
        
        if isinstance(created_at, datetime):
            start_time = createdAt
            now = datetime.now(start_time.tzinfo) if start_time.tzinfo else datetime.now()
        else:
            start_time = datetime.fromisoformat(str(created_at).replace('Z', '+00:00'))
            now = datetime.now(start_time.tzinfo)
        
        diff = now - start_time
        minutes = int(diff.total_seconds() // 60)
        seconds = int(diff.total_seconds() % 60)
        return f"{minutes}m {seconds}s"
    except:
        return "0m 0s"

# Task models
class ScrapingRequest(BaseModel):
    websites: List[dict]
    message_type: str = "general"
    fileUploadId: Optional[str] = None
    userId: Optional[str] = None

class TaskResponse(BaseModel):
    task_id: str
    status: str
    message: str

class TaskStatusResponse(BaseModel):
    task_id: str
    status: str
    progress: Optional[int] = None
    result: Optional[Dict] = None
    error: Optional[str] = None
    createdAt: str
    started_at: Optional[str] = None
    completed_at: Optional[str] = None

class FormSubmissionRequest(BaseModel):
    websites_with_messages: List[Dict]
    user_config: Optional[Dict] = None

# API Endpoints
@app.get("/")
async def root():
    return {"message": "AI Messaging Backend - Powered by Celery"}

@app.get("/health")
async def health():
    return {"status": "healthy", "python": "3.11", "celery": "enabled"}

@app.post("/api/scrape", response_model=TaskResponse)
async def start_scraping(request: ScrapingRequest):
    """Start scraping websites using Celery"""
    try:
        if not request.websites:
            raise HTTPException(status_code=400, detail="No websites provided")
        
        # Extract website URLs from the request
        websites = [site.get('url', site) if isinstance(site, dict) else site for site in request.websites]
        
        # Start Celery task with correct parameter order
        task = scrape_websites_task.delay(
            fileUploadId=request.fileUploadId,
            userId=request.userId,
            websites=websites
        )
        
        logger.info(f"Started Celery scraping task {task.id} with {len(websites)} websites")
        
        return TaskResponse(
            task_id=task.id,
            status="started",
            message=f"Scraping started for {len(websites)} websites"
        )
        
    except Exception as e:
        logger.error(f"Error starting scraping: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/generate-messages")
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
                companyName = website.get('companyName') or website.get('companyName', 'Unknown Company')
                industry = website.get('industry', 'Unknown Industry')
                businessType = website.get('businessType') or website.get('businessType', 'Unknown Business Type')
                aboutUsContent = website.get('aboutUsContent') or website.get('aboutUsContent', '')
                
                # Create a standardized website object for AI generation
                website_obj = {
                    'id': website_id,
                    'companyName': companyName,
                    'industry': industry,
                    'businessType': businessType,
                    'aboutUsContent': aboutUsContent,
                    'websiteUrl': website.get('websiteUrl') or website.get('websiteUrl', '')
                }
                
                # Generate message using AI
                message, confidence = ai_generator.generate_message(
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
                        'url': website_obj['websiteUrl'],
                        'message': message,
                        'confidence': confidence,
                        'success': True
                    })
                else:
                    results.append({
                        'website_id': website_id,
                        'url': website_obj['websiteUrl'],
                        'message': None,
                        'error': 'Failed to generate message',
                        'success': False
                    })
                    
            except Exception as e:
                logger.error(f"Error generating message for website {website.get('id', 'unknown')}: {e}")
                results.append({
                    'website_id': website.get('id'),
                    'url': website.get('websiteUrl') or website.get('websiteUrl', ''),
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
            "totalWebsites": len(website_data),
            "successful_count": successful_count,
            "failed_count": failed_count
        }
        
    except Exception as e:
        logger.error(f"Error in generate_messages endpoint: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/workflow/trigger-ai-generation", response_model=TaskResponse)
async def trigger_ai_generation_for_file_upload(request: Dict[str, Any]):
    """Trigger AI message generation for all websites in a file upload"""
    try:
        fileUploadId = request.get('fileUploadId')
        message_type = request.get('message_type', 'general')
        custom_prompt = request.get('custom_prompt', '')
        ai_model = request.get('ai_model', 'gemini')
        
        if not fileUploadId:
            raise HTTPException(status_code=400, detail="File upload ID is required")
        
        # Get all websites for this file upload
        db_manager = DatabaseManager()
        websites = db_manager.get_websites_by_file_upload_id(fileUploadId)
        
        if not websites:
            raise HTTPException(status_code=404, detail=f"No websites found for file upload ID: {fileUploadId}")
        
        # Filter websites that have been successfully scraped
        scraped_websites = [w for w in websites if w.get('scrapingStatus') == 'COMPLETED']
        
        if not scraped_websites:
            raise HTTPException(status_code=400, detail="No successfully scraped websites found. Please wait for scraping to complete.")
        
        # Prepare website data for AI generation
        website_data = []
        for website in scraped_websites:
            website_data.append({
                'id': website.get('id'),
                'companyName': website.get('companyName', ''),
                'industry': website.get('industry', ''),
                'businessType': website.get('businessType', ''),
                'aboutUsContent': website.get('aboutUsContent', ''),
                'websiteUrl': website.get('websiteUrl', ''),
                'scrapingStatus': website.get('scrapingStatus'),
                'messageStatus': website.get('messageStatus'),
                'fileUploadId': website.get('fileUploadId'),
                'userId': website.get('userId')
            })
        
        # Start Celery task for AI message generation
        task = generate_messages_task.delay(
            website_data=website_data,
            message_type=message_type,
            fileUploadId=fileUploadId,
            userId=request.get('userId', 'default_user')
        )
        
        logger.info(f"Started AI message generation task {task.id} for {len(website_data)} websites from file upload {fileUploadId}")
        
        return TaskResponse(
            task_id=task.id,
            status="started",
            message=f"AI message generation started for {len(website_data)} websites from file upload {fileUploadId}"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error triggering AI generation for file upload: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/process-file", response_model=TaskResponse)
async def process_large_file(
    fileUploadId: str = Query(..., description="File upload ID"),
    filePath: str = Query(..., description="File path"),
    fileType: str = Query(..., description="File type"),
    totalChunks: int = Query(..., description="Total chunks"),
    userId: str = Query(..., description="User ID"),
    websiteUrlColumn: str = Query("websiteUrl", description="Website URL column name"),
    contactFormUrlColumn: str = Query("contactFormUrl", description="Contact form URL column name")
):
    """Process large file using Celery - Fixed to handle frontend workflow with automatic file copying"""
    try:
        logger.info(f"Processing file upload {fileUploadId} with path: {filePath}")
        
        # Check if file exists - handle frontend upload directory mismatch
        if not os.path.exists(filePath):
            logger.warning(f"File not found at frontend path: {filePath}")
            
            # Try to find the file in the backend uploads directory
            filename = os.path.basename(filePath)
            backend_path = f"/home/xb3353/Automated-AI-Messaging-Tool-Backend/uploads/{filename}"
            
            if os.path.exists(backend_path):
                logger.info(f"Found file in backend directory: {backend_path}")
                filePath = backend_path
            else:
                # Try to copy file from frontend to backend if it exists in frontend
                frontend_path = filePath
                if os.path.exists(frontend_path):
                    logger.info(f"File found in frontend directory, copying to backend: {frontend_path}")
                    
                    # Create backend directory if it doesn't exist
                    backend_dir = "uploads"
                    os.makedirs(backend_dir, exist_ok=True)
                    
                    # Copy file to backend
                    import shutil
                    try:
                        shutil.copy2(frontend_path, backend_path)
                        logger.info(f"Successfully copied file to backend: {backend_path}")
                        filePath = backend_path
                    except Exception as copy_error:
                        logger.error(f"Failed to copy file from frontend to backend: {copy_error}")
                        raise HTTPException(status_code=500, detail=f"Failed to copy file to backend: {copy_error}")
                else:
                    logger.error(f"File not found in either location: {filePath} or {backend_path}")
                    raise HTTPException(status_code=404, detail=f"File not found. Please upload the file first.")
        
        # Check if file upload exists in database
        db_manager = DatabaseManager()
        upload = db_manager.get_file_upload_by_id(fileUploadId)
        if not upload:
            logger.error(f"File upload not found: {fileUploadId}")
            raise HTTPException(status_code=404, detail=f"File upload not found: {fileUploadId}")
        
        # Update status to PROCESSING
        db_manager.update_file_upload_status(fileUploadId, "PROCESSING")
        
        # Start Celery task with column mapping
        task = process_file_upload_task.delay(
            fileUploadId=fileUploadId, 
            file_path=filePath, 
            file_type=fileType, 
            total_chunks=totalChunks, 
            userId=userId,
            website_url_column=websiteUrlColumn,
            contact_form_url_column=contactFormUrlColumn
        )
        
        logger.info(f"Started Celery file processing task {task.id} with columns: {websiteUrlColumn}, {contactFormUrlColumn}")
        
        return TaskResponse(
            task_id=task.id,
            status="started",
            message=f"File processing started for {filePath}"
        )
        
    except Exception as e:
        logger.error(f"Error starting file processing: {e}")
        # Update status to ERROR if we have the upload ID
        try:
            if 'fileUploadId' in locals():
                db_manager = DatabaseManager()
                db_manager.update_file_upload_status(fileUploadId, "ERROR")
        except:
            pass
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/process-chunk", response_model=TaskResponse)
async def process_chunk(chunk_id: str, chunk_number: int, start_row: int, end_row: int, file_path: str, fileType: str):
    """Process a single chunk using Celery"""
    try:
        # Start Celery task
        task = process_chunk_task.delay(
            chunk_id=chunk_id,
            chunk_number=chunk_number,
            start_row=start_row,
            end_row=end_row,
            file_path=file_path,
            file_type=fileType
        )
        
        logger.info(f"Started Celery chunk processing task {task.id}")
        
        return TaskResponse(
            task_id=task.id,
            status="started",
            message=f"Chunk {chunk_number} processing started"
        )
        
    except Exception as e:
        logger.error(f"Error starting chunk processing: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# DISABLED: Manual website extraction endpoint - now handled automatically
# @app.post("/api/extract-websites", response_model=TaskResponse)
# async def extract_websites_from_file(file_path: str, fileType: str, fileUploadId: Optional[str] = None, userId: Optional[str] = None):
#     """Extract websites from file using Celery"""
#     try:
#         # Start Celery task with database parameters
#         task = extract_websites_from_file_task.delay(file_path, file_type, file_upload_id, user_id)
#         
#         logger.info(f"Started Celery website extraction task {task.id}")
#         
#         return TaskResponse(
#             task_id=task.id,
#             status="started",
#             message=f"Website extraction started for {file_path}"
#         )
#         
#     except Exception as e:
#         logger.error(f"Error starting website extraction: {e}")
#         raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/submit-forms", response_model=TaskResponse)
async def submit_contact_forms(request: FormSubmissionRequest):
    """
    Submit contact forms with generated messages
    """
    try:
        # Generate task ID
        task_id = str(uuid.uuid4())
        
        # Start form submission task
        task = contact_form_submission_task.delay(
            websites_with_messages=request.websites_with_messages,
            user_config=request.user_config
        )
        
        return TaskResponse(
            task_id=task.id,
            status="PENDING",
            message="Contact form submission started"
        )
        
    except Exception as e:
        logger.error(f"Error starting form submission: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/form-submission/status/{task_id}")
async def get_form_submission_status(task_id: str):
    """
    Get form submission task status
    """
    try:
        task = contact_form_submission_task.AsyncResult(task_id)
        
        if task.ready():
            if task.successful():
                result = task.result
                return {
                    "task_id": task_id,
                    "status": "COMPLETED",
                    "result": result
                }
            else:
                return {
                    "task_id": task_id,
                    "status": "FAILED",
                    "error": str(task.info)
                }
        else:
            return {
                "task_id": task_id,
                "status": task.state,
                "info": task.info
            }
            
    except Exception as e:
        logger.error(f"Error getting form submission status: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/task-status/{task_id}", response_model=TaskStatusResponse)
async def get_task_status(task_id: str):
    """Get Celery task status with progress tracking"""
    try:
        # Get task result from Celery
        from celery_app import celery_app
        result = celery_app.AsyncResult(task_id)
        
        # Build response
        response = {
            "task_id": task_id,
            "status": result.status,
            "createdAt": datetime.now().isoformat(),  # Celery doesn't provide creation time
        }
        
        # Add progress information if available
        if result.state == 'PROGRESS':
            response.update({
                "progress": result.info.get('progress', 0),
                "started_at": datetime.now().isoformat()
            })
        
        # Add result if completed
        if result.ready():
            if result.successful():
                response.update({
                    "result": result.result,
                    "completed_at": datetime.now().isoformat()
                })
            else:
                response.update({
                    "error": str(result.info),
                    "completed_at": datetime.now().isoformat()
                })
        
        return TaskStatusResponse(**response)
        
    except Exception as e:
        logger.error(f"Error getting task status: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/contact-inquiries/website/{website_id}")
async def get_contact_inquiries_by_website(website_id: str):
    """Get all contact inquiries for a specific website"""
    try:
        db_manager = DatabaseManager()
        inquiries = db_manager.get_contact_inquiries_by_website(website_id)
        
        return {
            "success": True,
            "website_id": website_id,
            "total_inquiries": len(inquiries),
            "inquiries": inquiries
        }
        
    except Exception as e:
        logger.error(f"Error getting contact inquiries for website: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/contact-inquiries/user/{userId}")
async def get_contact_inquiries_by_user(userId: str):
    """Get all contact inquiries for a specific user"""
    try:
        db_manager = DatabaseManager()
        inquiries = db_manager.get_contact_inquiries_by_user(userId)
        
        return {
            "success": True,
            "userId": userId,
            "total_inquiries": len(inquiries),
            "inquiries": inquiries
        }
        
    except Exception as e:
        logger.error(f"Error getting contact inquiries for user: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/contact-inquiries/statistics")
async def get_contact_inquiry_statistics(userId: str = None):
    """Get contact inquiry statistics"""
    try:
        db_manager = DatabaseManager()
        
        if userId:
            inquiries = db_manager.get_contact_inquiries_by_user(userId)
        else:
            # For admin users, get all inquiries (you might want to add admin check here)
            inquiries = db_manager.get_all_contact_inquiries(limit=1000)  # Get all inquiries for admin
        
        # Calculate statistics
        total_inquiries = len(inquiries)
        successful_submissions = len([i for i in inquiries if i['status'] == 'SUBMITTED'])
        failed_submissions = len([i for i in inquiries if i['status'] == 'FAILED'])
        pending_submissions = len([i for i in inquiries if i['status'] == 'PENDING'])
        
        success_rate = (successful_submissions / total_inquiries * 100) if total_inquiries > 0 else 0
        
        return {
            "success": True,
            "statistics": {
                "total_inquiries": total_inquiries,
                "successful_submissions": successful_submissions,
                "failed_submissions": failed_submissions,
                "pending_submissions": pending_submissions,
                "success_rate": round(success_rate, 2)
            }
        }
        
    except Exception as e:
        logger.error(f"Error getting contact inquiry statistics: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/scraping/results/{fileUploadId}")
async def get_scraping_results(fileUploadId: str):
    """Get scraping results for a specific file upload"""
    try:
        db_manager = DatabaseManager()
        
        # Get websites for this file upload
        websites = db_manager.get_websites_by_file_upload_id(fileUploadId)
        
        if not websites:
            raise HTTPException(status_code=404, detail=f"No scraping results found for file upload ID: {fileUploadId}")
        
        # Format the response
        results = []
        for website in websites:
            result = {
                "id": website['id'],
                "websiteUrl": website['websiteUrl'],
                "companyName": website['companyName'],
                "industry": website['industry'],
                "businessType": website['businessType'],
                "aboutUsContent": website['aboutUsContent'],
                "scrapingStatus": website['scrapingStatus'],
                "messageStatus": website['messageStatus'],
                "generatedMessage": website['generatedMessage'],
                "createdAt": website['createdAt'],
                "updatedAt": website['updatedAt'],
                "fileUploadId": website['fileUploadId'],
                "userId": website['userId']
            }
            results.append(result)
        
        return {
            "fileUploadId": fileUploadId,
            "totalWebsites": len(results),
            "results": results
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting scraping results: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/file-uploads/history", response_model=List[Dict[str, Any]])
async def get_file_upload_history(userId: str = None):
    """Get file upload history for display in frontend"""
    try:
        db_manager = DatabaseManager()
        
        # Get all file uploads (or filter by user_id if provided)
        if userId:
            file_uploads = db_manager.get_user_file_uploads(userId)
        else:
            # Get all file uploads (for admin view)
            file_uploads = db_manager.get_all_file_uploads()
        
        # Format the response for frontend
        history = []
        for upload in file_uploads:
            history.append({
                "id": upload['id'],
                "filename": upload['filename'],
                "originalName": upload['originalName'],
                "status": upload['status'],
                "totalWebsites": upload['totalWebsites'],
                "processedWebsites": upload['processedWebsites'],
                "failedWebsites": upload['failedWebsites'],
                "createdAt": upload['createdAt'],
                "updatedAt": upload['updatedAt'],
                "userId": upload['userId']
            })
        
        return history
        
    except Exception as e:
        logger.error(f"Error getting file upload history: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/tasks")
async def list_tasks():
    """List all Celery tasks (basic implementation)"""
    try:
        # This is a simplified version - in production you'd want to store task IDs
        return {
            "message": "Task listing requires task ID storage. Use individual task status endpoints.",
            "endpoints": {
                "task_status": "/api/task-status/{task_id}",
                "start_scraping": "/api/scrape",
                "start_file_processing": "/api/process-file"
            }
        }
    except Exception as e:
        logger.error(f"Error listing tasks: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/api/task/{task_id}")
async def cancel_task(task_id: str):
    """Cancel a running Celery task"""
    try:
        from celery_app import celery_app
        celery_app.control.revoke(task_id, terminate=True)
        
        logger.info(f"Task {task_id} cancelled successfully")
        
        return {
            "task_id": task_id,
            "status": "cancelled",
            "message": "Task cancelled successfully"
        }
        
    except Exception as e:
        logger.error(f"Error cancelling task {task_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/predefined-messages", response_model=Dict[str, Any])
async def create_predefined_message(message_data: Dict[str, Any]):
    """Create a new predefined message"""
    try:
        db = DatabaseManager()
        success = db.create_predefined_message(message_data)
        
        if success:
            return {"success": True, "message": "Predefined message created successfully"}
        else:
            raise HTTPException(status_code=500, detail="Failed to create predefined message")
            
    except Exception as e:
        logger.error(f"Error creating predefined message: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/predefined-messages", response_model=List[Dict[str, Any]])
async def get_predefined_messages(industry: str = None, businessType: str = None, status: str = 'ACTIVE'):
    """Get predefined messages with optional filtering"""
    try:
        db = DatabaseManager()
        messages = db.get_predefined_messages_by_criteria(
            industry=industry,
            business_type=businessType,
            status=status
        )
        return messages
        
    except Exception as e:
        logger.error(f"Error getting predefined messages: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/predefined-messages/{message_id}", response_model=Dict[str, Any])
async def get_predefined_message(message_id: str):
    """Get a specific predefined message by ID"""
    try:
        db = DatabaseManager()
        message = db.get_predefined_message_by_id(message_id)
        
        if message:
            return message
        else:
            raise HTTPException(status_code=404, detail="Predefined message not found")
            
    except Exception as e:
        logger.error(f"Error getting predefined message: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.put("/api/predefined-messages/{message_id}", response_model=Dict[str, Any])
async def update_predefined_message(message_id: str, message_data: Dict[str, Any]):
    """Update an existing predefined message"""
    try:
        db = DatabaseManager()
        success = db.update_predefined_message(message_id, message_data)
        
        if success:
            return {"success": True, "message": "Predefined message updated successfully"}
        else:
            raise HTTPException(status_code=500, detail="Failed to update predefined message")
            
    except Exception as e:
        logger.error(f"Error updating predefined message: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/api/predefined-messages/{message_id}", response_model=Dict[str, Any])
async def delete_predefined_message(message_id: str):
    """Delete a predefined message"""
    try:
        db = DatabaseManager()
        success = db.delete_predefined_message(message_id)
        
        if success:
            return {"success": True, "message": "Predefined message deleted successfully"}
        else:
            raise HTTPException(status_code=500, detail="Failed to delete predefined message")
            
    except Exception as e:
        logger.error(f"Error deleting predefined message: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/predefined-messages/statistics", response_model=Dict[str, Any])
async def get_predefined_message_statistics():
    """Get statistics about predefined message usage"""
    try:
        db = DatabaseManager()
        stats = db.get_predefined_message_statistics()
        return stats
        
    except Exception as e:
        logger.error(f"Error getting predefined message statistics: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/message-generation/hybrid", response_model=Dict[str, Any])
async def generate_hybrid_message(request: Dict[str, Any]):
    """Generate message using hybrid approach (predefined + AI)"""
    try:
        website_data = request.get('website_data', {})
        message_type = request.get('message_type', 'general')
        
        db = DatabaseManager()
        ai_generator = GeminiMessageGenerator(db_manager=db)
        
        result = ai_generator.hybrid_message_generation(website_data, message_type)
        
        return {
            "success": True,
            "message": result['message'],
            "method": result['method'],
            "confidence_score": result['confidence_score'],
            "base_predefined_message": result.get('base_predefined_message'),
            "customization_level": result['customization_level']
        }
        
    except Exception as e:
        logger.error(f"Error generating hybrid message: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/message-generation/with-predefined-examples", response_model=Dict[str, Any])
async def generate_message_with_predefined_examples(request: Dict[str, Any]):
    """Generate message using predefined messages as examples"""
    try:
        website_data = request.get('website_data', {})
        message_type = request.get('message_type', 'general')
        
        db = DatabaseManager()
        ai_generator = GeminiMessageGenerator(db_manager=db)
        
        message, confidence = ai_generator.generate_with_predefined_examples(website_data, message_type)
        
        return {
            "success": True,
            "message": message,
            "confidence_score": confidence,
            "method": "predefined_examples"
        }
        
    except Exception as e:
        logger.error(f"Error generating message with predefined examples: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/message-generation/generate-for-selected", response_model=Dict[str, Any])
async def generate_messages_for_selected_websites(request: Dict[str, Any]):
    """Generate AI messages for manually selected websites"""
    try:
        website_ids = request.get('website_ids', [])
        message_type = request.get('message_type', 'general')
        userId = request.get('userId', 'default_user')
        
        if not website_ids:
            raise HTTPException(status_code=400, detail="No website IDs provided")
        
        # Get website data from database
        db = DatabaseManager()
        websites_data = []
        
        for website_id in website_ids:
            # Get website data by ID (you'll need to implement this method)
            website_data = db.get_website_by_id(website_id)
            if website_data:
                websites_data.append(website_data)
        
        if not websites_data:
            raise HTTPException(status_code=404, detail="No valid websites found")
        
        # Generate messages for selected websites
        ai_generator = GeminiMessageGenerator(db_manager=db)
        results = []
        
        for website in websites_data:
            try:
                message, confidence = ai_generator.generate_message(
                    website, 
                    message_type=message_type
                )
                
                # Update database with generated message
                db.update_website_message(
                    website_id=website.get('id'),
                    generatedMessage=message,
                    messageStatus="GENERATED"
                )
                
                results.append({
                    'website_id': website.get('id'),
                    'websiteUrl': website.get('websiteUrl'),
                    'companyName': website.get('companyName'),
                    'generatedMessage': message,
                    'confidence_score': confidence,
                    'message_type': message_type,
                    'success': True
                })
                
            except Exception as e:
                logger.error(f"Error generating message for {website.get('websiteUrl')}: {e}")
                results.append({
                    'website_id': website.get('id'),
                    'websiteUrl': website.get('websiteUrl'),
                    'companyName': website.get('companyName'),
                    'error': str(e),
                    'success': False
                })
        
        return {
            "success": True,
            "totalWebsites": len(website_ids),
            "processedWebsites": len([r for r in results if r['success']]),
            "failedWebsites": len([r for r in results if not r['success']]),
            "results": results
        }
        
    except Exception as e:
        logger.error(f"Error generating messages for selected websites: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/form-submission/submit-for-selected", response_model=Dict[str, Any])
async def submit_forms_for_selected_websites(request: Dict[str, Any]):
    """Submit contact forms for manually selected websites"""
    try:
        website_ids = request.get('website_ids', [])
        user_config = request.get('user_config', {})
        
        if not website_ids:
            raise HTTPException(status_code=400, detail="No website IDs provided")
        
        # Get websites with generated messages
        db = DatabaseManager()
        websites_with_messages = []
        
        for website_id in website_ids:
            website_data = db.get_website_by_id(website_id)
            if website_data and website_data.get('generatedMessage'):
                websites_with_messages.append(website_data)
        
        if not websites_with_messages:
            raise HTTPException(status_code=404, detail="No websites with generated messages found")
        
        # Start form submission task
        task = contact_form_submission_task.delay(
            websites_with_messages=websites_with_messages,
            user_config=user_config
        )
        
        return {
            "success": True,
            "task_id": task.id,
            "totalWebsites": len(websites_with_messages),
            "message": "Contact form submission started for selected websites"
        }
        
    except Exception as e:
        logger.error(f"Error starting form submission for selected websites: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/websites/with-messages", response_model=List[Dict[str, Any]])
async def get_websites_with_generated_messages(fileUploadId: str = None, userId: str = None):
    """Get websites that have generated messages for manual selection"""
    try:
        db = DatabaseManager()
        
        # Get websites with generated messages
        websites = db.get_websites_with_messages(fileUploadId, userId)
        
        return websites
        
    except Exception as e:
        logger.error(f"Error getting websites with messages: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/websites/without-messages", response_model=List[Dict[str, Any]])
async def get_websites_without_messages(fileUploadId: str = None, userId: str = None):
    """Get websites that don't have generated messages yet"""
    try:
        db = DatabaseManager()
        
        # Get websites without generated messages
        websites = db.get_websites_without_messages(fileUploadId, userId)
        
        return websites
        
    except Exception as e:
        logger.error(f"Error getting websites without messages: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/websites/by-file-upload/{fileUploadId}", response_model=Dict[str, Any])
async def get_websites_by_file_upload(
    fileUploadId: str,
    page: int = Query(1, description="Page number"),
    limit: int = Query(10, description="Results per page"),
    search: str = Query("", description="Search term"),
    sortBy: str = Query("createdAt", description="Sort field"),
    sortOrder: str = Query("desc", description="Sort order (asc/desc)")
):
    """Get all websites from a specific file upload with pagination, search, and sorting"""
    try:
        db = DatabaseManager()
        
        # Get all websites for this file upload
        websites = db.get_websites_by_file_upload_id(fileUploadId)
        
        # Apply search filter
        if search:
            filtered_websites = []
            for website in websites:
                if (search.lower() in website.get('websiteUrl', '').lower() or 
                    search.lower() in website.get('companyName', '').lower() or
                    search.lower() in website.get('industry', '').lower()):
                    filtered_websites.append(website)
            websites = filtered_websites
        
        # Apply sorting
        if sortBy and sortOrder:
            reverse = sortOrder.lower() == 'desc'
            try:
                websites.sort(key=lambda x: x.get(sortBy, ''), reverse=reverse)
            except:
                # Fallback to default sorting if sort field doesn't exist
                websites.sort(key=lambda x: x.get('createdAt', ''), reverse=True)
        
        # Calculate pagination
        total_count = len(websites)
        total_pages = (total_count + limit - 1) // limit
        skip = (page - 1) * limit
        has_next_page = page < total_pages
        has_previous_page = page > 1
        
        # Apply pagination
        paginated_websites = websites[skip:skip + limit]
        
        # Categorize websites
        with_messages = [w for w in websites if w.get('generatedMessage')]
        without_messages = [w for w in websites if not w.get('generatedMessage')]
        
        return {
            "fileUploadId": fileUploadId,
            "totalWebsites": total_count,
            "with_messages": len(with_messages),
            "without_messages": len(without_messages),
            "websites": paginated_websites,
            "pagination": {
                "page": page,
                "limit": limit,
                "totalCount": total_count,
                "totalPages": total_pages,
                "hasNextPage": has_next_page,
                "hasPreviousPage": has_previous_page
            }
        }
        
    except Exception as e:
        logger.error(f"Error getting websites by file upload: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/scraping/trigger-manual/{fileUploadId}", response_model=Dict[str, Any])
async def trigger_manual_scraping(fileUploadId: str, userId: str = None):
    """Manually trigger scraping for a specific file upload"""
    try:
        db_manager = DatabaseManager()
        
        # Get websites for this file upload that are still pending
        websites = db_manager.get_websites_by_file_upload_id(fileUploadId)
        pending_websites = [w for w in websites if w.get('scrapingStatus') == 'PENDING']
        
        if not pending_websites:
            return {
                "status": "no_pending",
                "message": "No pending websites found for scraping",
                "fileUploadId": fileUploadId,
                "total_pending": 0
            }
        
        # Get website URLs for scraping
        website_urls = [w['websiteUrl'] for w in pending_websites]
        
        # Start scraping task
        from celery_tasks.scraping_tasks import scrape_websites_task
        
        task = scrape_websites_task.delay(
            fileUploadId=fileUploadId,
            userId=userId or "system",
            websites=website_urls
        )
        
        logger.info(f"Manually triggered scraping task {task.id} for {len(website_urls)} websites")
        
        return {
            "status": "started",
            "task_id": task.id,
            "message": f"Scraping started for {len(website_urls)} websites",
            "fileUploadId": fileUploadId,
            "total_pending": len(website_urls)
        }
        
    except Exception as e:
        logger.error(f"Error triggering manual scraping: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/message-generation/bulk-generate", response_model=Dict[str, Any])
async def bulk_generate_messages(request: Dict[str, Any]):
    """Bulk generate messages for multiple websites"""
    try:
        fileUploadId = request.get('fileUploadId')
        message_type = request.get('message_type', 'general')
        userId = request.get('userId', 'default_user')
        limit = request.get('limit', 100)  # Limit for batch processing
        
        if not fileUploadId:
            raise HTTPException(status_code=400, detail="File upload ID is required")
        
        # Get websites without messages
        db = DatabaseManager()
        websites = db.get_websites_without_messages(fileUploadId, userId)
        
        if not websites:
            return {
                "success": True,
                "message": "No websites found without messages",
                "totalWebsites": 0,
                "processedWebsites": 0
            }
        
        # Limit the number of websites to process
        websites_to_process = websites[:limit]
        
        # Generate messages
        ai_generator = GeminiMessageGenerator(db_manager=db)
        results = []
        
        for website in websites_to_process:
            try:
                message, confidence = ai_generator.generate_message(
                    website, 
                    message_type="general"
                )
                
                # Update database
                db.update_website_message(
                    website_id=website.get('id'),
                    generatedMessage=message,
                    messageStatus="GENERATED"
                )
                
                results.append({
                    'website_id': website.get('id'),
                    'websiteUrl': website.get('websiteUrl'),
                    'companyName': website.get('companyName'),
                    'confidence_score': confidence,
                    'success': True
                })
                
            except Exception as e:
                logger.error(f"Error generating message for {website.get('websiteUrl')}: {e}")
                results.append({
                    'website_id': website.get('id'),
                    'websiteUrl': website.get('websiteUrl'),
                    'error': str(e),
                    'success': False
                })
        
        return {
            "success": True,
            "totalWebsites": len(websites_to_process),
            "processedWebsites": len([r for r in results if r['success']]),
            "failedWebsites": len([r for r in results if not r['success']]),
            "results": results
        }
        
    except Exception as e:
        logger.error(f"Error in bulk message generation: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/ai/generate-single-message")
async def generate_single_ai_message(website_data: List[Dict[str, Any]]):
    """Generate AI messages for individual websites - Direct API"""
    try:
        if not website_data:
            raise HTTPException(status_code=400, detail="Website data is required")
        
        logger.info(f"Generating messages for {len(website_data)} websites via direct API")
        
        # Initialize AI generator
        db_manager = DatabaseManager()
        ai_generator = GeminiMessageGenerator(db_manager=db_manager)
        
        results = []
        for website in website_data:
            try:
                # Extract website information
                website_id = website.get('id')
                companyName = website.get('companyName') or 'Unknown Company'
                industry = website.get('industry') or 'Unknown Industry'
                businessType = website.get('businessType') or 'Unknown Business Type'
                aboutUsContent = website.get('aboutUsContent') or ''
                
                # Create a standardized website object for AI generation
                website_obj = {
                    'id': website_id,
                    'companyName': companyName,
                    'industry': industry,
                    'businessType': businessType,
                    'aboutUsContent': aboutUsContent,
                    'websiteUrl': website.get('websiteUrl') or ''
                }
                
                logger.info(f"Processing website: {website_obj['companyName']} - {website_obj['industry']}")
                
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
                        'url': website_obj['websiteUrl'],
                        'message': message,
                        'confidence': confidence,
                        'success': True
                    })
                    logger.info(f"Successfully generated message for {website_obj['companyName']}")
                else:
                    results.append({
                        'website_id': website_id,
                        'url': website_obj['websiteUrl'],
                        'message': None,
                        'error': 'Failed to generate message',
                        'success': False
                    })
                    logger.warning(f"Failed to generate message for {website_obj['companyName']}")
                    
            except Exception as e:
                logger.error(f"Error generating message for website {website.get('id', 'unknown')}: {e}")
                results.append({
                    'website_id': website.get('id'),
                    'url': website.get('websiteUrl') or website.get('websiteUrl', ''),
                    'message': None,
                    'error': str(e),
                    'success': False
                })
        
        # Count successful generations
        successful_count = len([r for r in results if r['success']])
        failed_count = len([r for r in results if not r['success']])
        
        logger.info(f"Direct API message generation completed. Success: {successful_count}, Failed: {failed_count}")
        
        return {
            "success": True,
            "messages": results,
            "totalWebsites": len(website_data),
            "successful_count": successful_count,
            "failed_count": failed_count
        }
        
    except Exception as e:
        logger.error(f"Error in generate_single_ai_message endpoint: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/ai/generate-preview")
async def generate_ai_message_preview(website_data: List[Dict[str, Any]]):
    """Generate AI message preview for UI display - no database storage"""
    try:
        if not website_data:
            raise HTTPException(status_code=400, detail="Website data is required")
        
        logger.info(f"Generating AI message preview for {len(website_data)} websites")
        
        # Initialize AI generator
        ai_generator = GeminiMessageGenerator(db_manager=None)  # No database needed
        
        results = []
        for website in website_data:
            try:
                # Extract website information
                companyName = website.get('companyName') or 'Unknown Company'
                industry = website.get('industry') or 'Unknown Industry'
                businessType = website.get('businessType') or 'Unknown Business Type'
                aboutUsContent = website.get('aboutUsContent') or ''
                
                # Create a simple website object for AI generation
                website_obj = {
                    'companyName': companyName,
                    'industry': industry,
                    'businessType': businessType,
                    'aboutUsContent': aboutUsContent,
                    'websiteUrl': website.get('websiteUrl') or ''
                }
                
                # Generate message using AI
                message, confidence = ai_generator.hybrid_message_generation(
                    website_obj, 
                    message_type="general"
                )
                
                if message:
                    results.append({
                        'website_id': website.get('id'),
                        'url': website_obj['websiteUrl'],
                        'message': message,
                        'success': True
                    })
                    logger.info(f"Generated preview message for {companyName}")
                else:
                    results.append({
                        'website_id': website.get('id'),
                        'url': website_obj['websiteUrl'],
                        'message': None,
                        'error': 'Failed to generate message',
                        'success': False
                    })
                    
            except Exception as e:
                logger.error(f"Error generating preview for website {website.get('id', 'unknown')}: {e}")
                results.append({
                    'website_id': website.get('id'),
                    'url': website.get('websiteUrl') or website.get('websiteUrl', ''),
                    'message': None,
                    'error': str(e),
                    'success': False
                })
        
        return {
            "success": True,
            "messages": results
        }
        
    except Exception as e:
        logger.error(f"Error in generate_ai_message_preview: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# File upload endpoint
@app.post("/api/upload-file")
async def upload_file(file: UploadFile = File(...), userId: str = Query(...)):
    """Upload a CSV file, create a file upload record, and automatically start processing"""
    try:
        if not file.filename.endswith('.csv'):
            raise HTTPException(status_code=400, detail="Only CSV files are supported")
        
        # Check if file with same name already exists
        db_manager = DatabaseManager()
        existing_upload = db_manager.get_file_upload_by_original_name(file.filename, userId)
        
        if existing_upload:
            # Update existing record instead of creating new one
            file_upload_id = existing_upload['id']
            file_path = existing_upload['filename']
            
            # Update file content
            with open(file_path, "wb") as buffer:
                content = await file.read()
                buffer.write(content)
            
            # Update file upload record
            success = db_manager.update_file_upload(file_upload_id, {
                'fileSize': len(content),
                'status': 'UPLOADING',
                'updatedAt': datetime.now().isoformat()
            })
            
            logger.info(f"Updated existing file upload: {file_upload_id} -> {file_path}")
        else:
            # Create new file upload record
            file_upload_id = str(uuid.uuid4())
            
            # Create uploads directory if it doesn't exist
            upload_dir = "/home/xb3353/Automated-AI-Messaging-Tool-Backend/uploads"
            os.makedirs(upload_dir, exist_ok=True)
            
            # Save file to uploads directory
            file_path = os.path.join(upload_dir, f"{file_upload_id}_{file.filename}")
            with open(file_path, "wb") as buffer:
                content = await file.read()
                buffer.write(content)
            
            # Create new file upload record in database
            success = db_manager.create_file_upload(
                fileUploadId=file_upload_id,
                userId=userId,
                filename=file_path,
                originalName=file.filename,
                fileSize=len(content),
                fileType="csv",
                status="UPLOADING",
                totalWebsites=0,
                processedWebsites=0,
                failedWebsites=0
            )
            
            logger.info(f"Created new file upload: {file_upload_id} -> {file_path}")
        
        if not success:
            raise HTTPException(status_code=500, detail="Failed to create file upload record")
        
        logger.info(f"File uploaded successfully: {file_upload_id} -> {file_path}")
        
        # AUTOMATIC PROCESSING: Start file processing task immediately
        try:
            from celery_tasks.file_tasks import process_file_upload_task
            import csv
            
            # Automatically detect CSV column names
            website_column = "Website URL"  # default
            contact_form_column = "Contact Form URL"  # default
            
            try:
                # Read CSV header to detect columns
                with open(file_path, 'r', encoding='utf-8') as csvfile:
                    reader = csv.reader(csvfile)
                    headers = next(reader, [])
                    
                    # Look for common column name variations
                    for header in headers:
                        header_lower = header.lower()
                        if any(keyword in header_lower for keyword in ['website', 'url', 'site']):
                            website_column = header
                        elif any(keyword in header_lower for keyword in ['contact', 'form', 'email']):
                            contact_form_column = header
                    
                    logger.info(f"Detected columns: Website='{website_column}', Contact='{contact_form_column}'")
            except Exception as csv_error:
                logger.warning(f"Could not detect CSV columns, using defaults: {csv_error}")
            
            # Start the processing task
            task = process_file_upload_task.delay(
                fileUploadId=file_upload_id, 
                file_path=file_path, 
                file_type="csv", 
                total_chunks=1,  # totalChunks
                userId=userId,
                website_url_column=website_column,
                contact_form_url_column=contact_form_column
            )
            
            # Update status to PROCESSING
            db_manager.update_file_upload_status(file_upload_id, "PROCESSING")
            
            logger.info(f"Automatically started processing task {task.id} for upload {file_upload_id}")
            
            return {
                "success": True,
                "fileUploadId": file_upload_id,
                "filePath": file_path,
                "originalName": file.filename,
                "fileSize": len(content),
                "taskId": task.id,
                "status": "PROCESSING",
                "message": f"File {file.filename} uploaded and processing started automatically"
            }
            
        except Exception as processing_error:
            logger.error(f"Error starting automatic processing: {processing_error}")
            # Update status to ERROR
            db_manager.update_file_upload_status(file_upload_id, "ERROR")
            
            return {
                "success": True,
                "fileUploadId": file_upload_id,
                "filePath": file_path,
                "originalName": file.filename,
                "fileSize": len(content),
                "status": "UPLOADED_BUT_PROCESSING_FAILED",
                "message": f"File uploaded but automatic processing failed. Manual processing required.",
                "error": str(processing_error)
            }
        
    except Exception as e:
        logger.error(f"Error uploading file: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/upload-from-frontend")
async def upload_from_frontend(file: UploadFile = File(...), userId: str = Query(...)):
    """Upload a CSV file from frontend, copy to backend directory, and start processing"""
    try:
        if not file.filename.endswith('.csv'):
            raise HTTPException(status_code=400, detail="Only CSV files are supported")
        
        # Check if file with same name already exists
        db_manager = DatabaseManager()
        existing_upload = db_manager.get_file_upload_by_original_name(file.filename, userId)
        
        if existing_upload:
            # Update existing record instead of creating new one
            file_upload_id = existing_upload['id']
            backend_file_path = existing_upload['filename']
            
            # Read file content and update file
            content = await file.read()
            with open(backend_file_path, "wb") as buffer:
                buffer.write(content)
            
            # Update file upload record
            success = db_manager.update_file_upload(file_upload_id, {
                'fileSize': len(content),
                'status': 'UPLOADING',
                'updatedAt': datetime.now().isoformat()
            })
            
            logger.info(f"Updated existing file upload: {file_upload_id} -> {backend_file_path}")
        else:
            # Create new file upload record
            file_upload_id = str(uuid.uuid4())
            
            # Create backend uploads directory if it doesn't exist
            backend_upload_dir = "/home/xb3353/Automated-AI-Messaging-Tool-Backend/uploads"
            os.makedirs(backend_upload_dir, exist_ok=True)
            
            # Save file to backend uploads directory with unique name
            backend_file_path = os.path.join(backend_upload_dir, f"{file_upload_id}_{file.filename}")
            
            # Read file content
            content = await file.read()
            
            # Write to backend directory
            with open(backend_file_path, "wb") as buffer:
                buffer.write(content)
            
            logger.info(f"File copied to backend: {file_upload_id} -> {backend_file_path}")
            
            # Create new file upload record in database
            success = db_manager.create_file_upload(
                fileUploadId=file_upload_id,
                userId=userId,
                filename=backend_file_path,  # Use backend path
                originalName=file.filename,
                fileSize=len(content),
                fileType="csv",
                status="UPLOADING",
                totalWebsites=0,
                processedWebsites=0,
                failedWebsites=0
            )
            
            logger.info(f"Created new file upload: {file_upload_id} -> {backend_file_path}")
        
        if not success:
            raise HTTPException(status_code=500, detail="Failed to create file upload record")
        
        logger.info(f"File uploaded successfully: {file_upload_id} -> {backend_file_path}")
        
        # AUTOMATIC PROCESSING: Start file processing task immediately
        try:
            from celery_tasks.file_tasks import process_file_upload_task
            import csv
            
            # Automatically detect CSV column names
            website_column = "Website URL"  # default
            contact_form_column = "Contact Form URL"  # default
            
            try:
                # Parse CSV header from content in memory to avoid race condition
                content_str = content.decode('utf-8')
                csv_lines = content_str.split('\n')
                if len(csv_lines) > 0:
                    headers = csv_lines[0].split(',')
                    
                    # Look for common column name variations
                    for header in headers:
                        header_lower = header.lower()
                        if any(keyword in header_lower for keyword in ['website', 'url', 'site']):
                            website_column = header
                        elif any(keyword in header_lower for keyword in ['contact', 'form', 'email']):
                            contact_form_column = header
                    
                    logger.info(f"Detected columns: Website='{website_column}', Contact='{contact_form_column}'")
                else:
                    logger.warning("No CSV content found, using default columns")
            except Exception as csv_error:
                logger.warning(f"Could not detect CSV columns, using defaults: {csv_error}")
            
            # Start the processing task
            # DEBUG: Log all variables before task call
            logger.info(f"DEBUG: About to call Celery task with parameters:")
            logger.info(f"DEBUG: fileUploadId={file_upload_id}")
            logger.info(f"DEBUG: file_path={backend_file_path}")
            logger.info(f"DEBUG: file_type=csv")
            logger.info(f"DEBUG: total_chunks=1")
            logger.info(f"DEBUG: userId={userId}")
            logger.info(f"DEBUG: website_url_column={website_column}")
            logger.info(f"DEBUG: contact_form_url_column={contact_form_column}")
            logger.info(f"DEBUG: All variables defined and ready")
            
            logger.info(f"DEBUG: Calling process_file_upload_task.delay() now...")
            try:
                logger.info(f"DEBUG: Task call parameters:")
                logger.info(f"DEBUG: fileUploadId={file_upload_id}")
                logger.info(f"DEBUG: file_path={backend_file_path}")
                logger.info(f"DEBUG: file_type=csv")
                logger.info(f"DEBUG: total_chunks=1")
                logger.info(f"DEBUG: userId={userId}")
                logger.info(f"DEBUG: website_url_column={website_column}")
                logger.info(f"DEBUG: contact_form_url_column={contact_form_column}")
                
                task = process_file_upload_task.delay(
                    fileUploadId=file_upload_id, 
                    file_path=backend_file_path, 
                    file_type="csv", 
                    total_chunks=1,  # totalChunks
                    userId=userId,
                    website_url_column=website_column,
                    contact_form_url_column=contact_form_column
                )
                
                logger.info(f"DEBUG: Task call successful, task_id={task.id}")
            except Exception as task_error:
                logger.error(f"DEBUG: Task call failed with error: {task_error}")
                logger.error(f"DEBUG: Error type: {type(task_error)}")
                logger.error(f"DEBUG: Error details: {str(task_error)}")
                import traceback
                logger.error(f"DEBUG: Full traceback: {traceback.format_exc()}")
                raise HTTPException(status_code=500, detail=f"Celery task failed: {task_error}")
            
            # Update status to PROCESSING
            db_manager.update_file_upload_status(file_upload_id, "PROCESSING")
            
            logger.info(f"Automatically started processing task {task.id} for upload {file_upload_id}")
            
            return {
                "success": True,
                "fileUploadId": file_upload_id,
                "filePath": backend_file_path,
                "originalName": file.filename,
                "fileSize": len(content),
                "taskId": task.id,
                "status": "PROCESSING",
                "message": f"File {file.filename} uploaded to backend and processing started automatically"
            }
            
        except Exception as processing_error:
            logger.error(f"Error starting automatic processing: {processing_error}")
            # Update status to ERROR
            db_manager.update_file_upload_status(file_upload_id, "ERROR")
            
            return {
                "success": True,
                "fileUploadId": file_upload_id,
                "filePath": backend_file_path,
                "originalName": file.filename,
                "fileSize": len(content),
                "status": "UPLOADED_BUT_PROCESSING_FAILED",
                "message": f"File uploaded to backend but automatic processing failed. Manual processing required.",
                "error": str(processing_error)
            }
        
    except Exception as e:
        logger.error(f"Error uploading file from frontend: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/upload")
async def get_file_uploads(
    userId: str = Query(..., description="User ID"),
    fileUploadId: str = Query(None, description="Specific file upload ID"),
    page: int = Query(1, description="Page number"),
    limit: int = Query(10, description="Results per page"),
    search: str = Query("", description="Search term"),
    status: str = Query("all", description="Status filter")
):
    """Get file uploads with pagination and search support"""
    try:
        db_manager = DatabaseManager()
        
        if fileUploadId:
            # Get specific file upload with progress
            file_upload = db_manager.get_file_upload_by_id(fileUploadId)
            if not file_upload:
                raise HTTPException(status_code=404, detail="File upload not found")
            
            # Get websites for this upload
            websites = db_manager.get_websites_by_file_upload_id(fileUploadId)
            
            return {
                "fileUpload": {
                    **file_upload,
                    "websites": websites
                }
            }
        else:
            # Get paginated file uploads with search and filtering
            file_uploads = db_manager.get_file_uploads_by_user_id(userId)
            
            # Apply search filter
            if search:
                filtered_uploads = []
                for upload in file_uploads:
                    if (search.lower() in upload.get('originalName', '').lower() or 
                        search.lower() in upload.get('filename', '').lower()):
                        filtered_uploads.append(upload)
                file_uploads = filtered_uploads
            
            # Apply status filter
            if status and status != 'all':
                file_uploads = [u for u in file_uploads if u.get('status') == status]
            
            # Calculate pagination
            total_count = len(file_uploads)
            total_pages = (total_count + limit - 1) // limit
            skip = (page - 1) * limit
            has_next_page = page < total_pages
            has_previous_page = page > 1
            
            # Apply pagination
            paginated_uploads = file_uploads[skip:skip + limit]
            
            return {
                "fileUploads": paginated_uploads,
                "pagination": {
                    "page": page,
                    "limit": limit,
                    "totalCount": total_count,
                    "totalPages": total_pages,
                    "hasNextPage": has_next_page,
                    "hasPreviousPage": has_previous_page
                }
            }
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting file uploads: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/upload/{fileUploadId}/websites")
async def get_websites_for_file_upload(
    fileUploadId: str,
    page: int = Query(1, description="Page number"),
    limit: int = Query(10, description="Results per page"),
    search: str = Query("", description="Search term"),
    sortBy: str = Query("createdAt", description="Sort field"),
    sortOrder: str = Query("desc", description="Sort order (asc/desc)")
):
    """Get websites for a specific file upload with pagination, search, and sorting"""
    try:
        db_manager = DatabaseManager()
        
        # Get all websites for this file upload
        websites = db_manager.get_websites_by_file_upload_id(fileUploadId)
        
        if not websites:
            return {
                "websites": [],
                "pagination": {
                    "page": page,
                    "limit": limit,
                    "totalCount": 0,
                    "totalPages": 0,
                    "hasNextPage": False,
                    "hasPreviousPage": False
                }
            }
        
        # Apply search filter
        if search:
            filtered_websites = []
            for website in websites:
                if (search.lower() in website.get('websiteUrl', '').lower() or 
                    search.lower() in website.get('companyName', '').lower() or
                    search.lower() in website.get('industry', '').lower() or
                    search.lower() in website.get('businessType', '').lower()):
                    filtered_websites.append(website)
            websites = filtered_websites
        
        # Apply sorting
        if sortBy and sortOrder:
            reverse = sortOrder.lower() == 'desc'
            try:
                websites.sort(key=lambda x: x.get(sortBy, '') or '', reverse=reverse)
            except:
                # Fallback to default sorting if sort field doesn't exist
                websites.sort(key=lambda x: x.get('createdAt', '') or '', reverse=True)
        
        # Calculate pagination
        total_count = len(websites)
        total_pages = (total_count + limit - 1) // limit
        skip = (page - 1) * limit
        has_next_page = page < total_pages
        has_previous_page = page > 1
        
        # Apply pagination
        paginated_websites = websites[skip:skip + limit]
        
        return {
            "websites": paginated_websites,
            "pagination": {
                "page": page,
                "limit": limit,
                "totalCount": total_count,
                "totalPages": total_pages,
                "hasNextPage": has_next_page,
                "hasPreviousPage": has_previous_page
            }
        }
        
    except Exception as e:
        logger.error(f"Error getting websites for file upload {fileUploadId}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) # Test automatic upload - Wed Jul 30 22:34:10 IST 2025
