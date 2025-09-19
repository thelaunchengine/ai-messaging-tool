from fastapi import FastAPI, HTTPException, BackgroundTasks, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
import uvicorn
from dotenv import load_dotenv
import os
import asyncio
from datetime import datetime
import logging
import json
import threading
import time

# Temporarily disable these imports
# from scraping.scraper import WebsiteScraper
# from ai.message_generator import AIMessageGenerator
# from database.models import DatabaseManager

load_dotenv()

app = FastAPI(
    title="AI Messaging Tool Backend",
    description="Python backend for web scraping and AI message generation",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000", 
        "http://127.0.0.1:3000",
        "https://your-app.vercel.app",  # Replace with your actual Vercel domain
        "https://*.vercel.app"  # Allow all Vercel preview deployments
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize components (temporarily disabled)
# db_manager = DatabaseManager()
# scraper = WebsiteScraper()
# ai_generator = AIMessageGenerator()

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# In-memory task storage (replace with database in production)
task_status = {}

# Background task functions
async def process_websites_background(websites: List[dict], message_type: str, task_id: str):
    """Background task to process websites"""
    try:
        task_status[task_id] = {"status": "processing", "progress": 0}
        
        for i, website in enumerate(websites):
            # Simulate processing
            await asyncio.sleep(1)  # Simulate work
            
            # Update progress
            progress = int((i + 1) / len(websites) * 100)
            task_status[task_id] = {"status": "processing", "progress": progress}
        
        task_status[task_id] = {"status": "completed", "progress": 100}
        logger.info(f"Background task {task_id} completed")
        
    except Exception as e:
        task_status[task_id] = {"status": "failed", "error": str(e)}
        logger.error(f"Background task {task_id} failed: {e}")

async def process_chunk_background(chunk_id: str, chunk_number: int, start_row: int, end_row: int, file_path: str, file_type: str):
    """Background task to process file chunk"""
    try:
        task_status[chunk_id] = {"status": "processing", "progress": 0}
        
        # Simulate processing
        await asyncio.sleep(2)  # Simulate work
        
        task_status[chunk_id] = {"status": "completed", "progress": 100}
        logger.info(f"Chunk processing {chunk_id} completed")
        
    except Exception as e:
        task_status[chunk_id] = {"status": "failed", "error": str(e)}
        logger.error(f"Chunk processing {chunk_id} failed: {e}")

# Pydantic models (v1 compatibility)
class WebsiteData(BaseModel):
    website_url: str
    contact_form_url: Optional[str] = None

class ScrapingRequest(BaseModel):
    websites: List[dict]
    message_type: str = "general"

class FileProcessingRequest(BaseModel):
    fileUploadId: str
    filePath: str
    fileType: str
    totalChunks: int
    userId: str

class ChunkProcessingRequest(BaseModel):
    chunkId: str
    chunkNumber: int
    startRow: int
    endRow: int
    filePath: str
    fileType: str

class ScrapingResponse(BaseModel):
    job_id: str
    status: str
    message: str

class MessageGenerationRequest(BaseModel):
    website_url: str
    about_us_content: str
    industry: Optional[str] = None
    message_type: str = "general"

class MessageGenerationResponse(BaseModel):
    message: str
    confidence: float

@app.get("/")
async def root():
    return {"message": "AI Messaging Tool Backend API - Minimal Version"}

@app.get("/health")
async def health_check():
    return {"status": "healthy", "services": ["api", "basic_functionality"]}

@app.post("/api/scrape")
async def start_scraping(request: ScrapingRequest, background_tasks: BackgroundTasks):
    """
    Start scraping websites and generate AI messages
    """
    try:
        # Validate websites
        if not request.websites:
            raise HTTPException(status_code=400, detail="No websites provided")
        
        # Generate task ID
        task_id = f"scrape_{int(time.time())}"
        
        # Add background task
        background_tasks.add_task(
            process_websites_background, 
            request.websites, 
            request.message_type, 
            task_id
        )
        
        return {
            "message": "Scraping started in background",
            "task_id": task_id,
            "total_websites": len(request.websites),
            "status": "started"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/process-file")
async def process_large_file(request: FileProcessingRequest, background_tasks: BackgroundTasks):
    print("\n>>>> /api/process-file endpoint called <<<<\n")
    logger.info(f"Starting process_large_file for fileUploadId: {request.fileUploadId}")
    logger.debug(f"Request data: {request.dict()}")
    
    try:
        # Generate task ID
        task_id = f"file_{request.fileUploadId}"
        
        # Add background task for file processing
        background_tasks.add_task(
            process_websites_background, 
            [],  # Empty list for now, would be populated from file
            "general", 
            task_id
        )
        
        logger.info("process_large_file completed successfully")
        return {
            "message": "File processing started in background",
            "task_id": task_id,
            "file_upload_id": request.fileUploadId,
            "total_chunks": request.totalChunks,
            "status": "started"
        }
        
    except Exception as e:
        logger.error(f"Error in process_large_file: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/process-chunk")
async def process_chunk(request: ChunkProcessingRequest, background_tasks: BackgroundTasks):
    """
    Process a single chunk of the file
    """
    try:
        # Add background task
        background_tasks.add_task(
            process_chunk_background,
            request.chunkId,
            request.chunkNumber,
            request.startRow,
            request.endRow,
            request.filePath,
            request.fileType
        )
        
        return {
            "message": "Chunk processing started in background",
            "chunk_id": request.chunkId,
            "chunk_number": request.chunkNumber,
            "status": "started"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/task-status/{task_id}")
async def get_task_status(task_id: str):
    """
    Get status of a background task
    """
    try:
        if task_id in task_status:
            return {
                "task_id": task_id,
                **task_status[task_id]
            }
        else:
            raise HTTPException(status_code=404, detail="Task not found")
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/file-progress/{file_upload_id}")
async def get_file_progress(file_upload_id: str):
    """
    Get processing progress for a specific file upload
    """
    try:
        return {
            "message": "File progress endpoint available (database temporarily disabled)",
            "file_upload_id": file_upload_id,
            "status": "ready"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/user-files/{user_id}")
async def get_user_files(user_id: str):
    """
    Get all file uploads for a specific user
    """
    try:
        return {
            "message": "User files endpoint available (database temporarily disabled)",
            "user_id": user_id,
            "status": "ready"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/api/file-upload/{file_upload_id}")
async def cancel_file_processing(file_upload_id: str):
    """
    Cancel file processing (if still in progress)
    """
    try:
        return {
            "message": "File upload cancellation endpoint available (database temporarily disabled)",
            "file_upload_id": file_upload_id,
            "status": "ready"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/message/generate", response_model=MessageGenerationResponse)
async def generate_message(request: MessageGenerationRequest):
    """
    Generate AI message for a website
    """
    try:
        # For now, return a simple message
        message = f"Hello! I came across your website {request.website_url} and was impressed by your work. I'd love to discuss potential collaboration opportunities."
        
        return MessageGenerationResponse(
            message=message,
            confidence=0.8
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/websites/{file_upload_id}")
async def get_websites(file_upload_id: str):
    """
    Get websites for a file upload
    """
    try:
        return {
            "message": "Websites endpoint available (database temporarily disabled)",
            "file_upload_id": file_upload_id,
            "status": "ready"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/websites/{website_id}/update")
async def update_website(website_id: str, website_data: dict):
    """
    Update website information
    """
    try:
        return {
            "message": "Website update endpoint available (database temporarily disabled)",
            "website_id": website_id,
            "status": "ready"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/predefined-messages")
async def get_predefined_messages():
    """
    Get predefined messages
    """
    try:
        return {
            "message": "Predefined messages endpoint available (database temporarily disabled)",
            "status": "ready"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/predefined-messages")
async def create_predefined_message(message_data: dict):
    """
    Create a predefined message
    """
    try:
        return {
            "message": "Create predefined message endpoint available (database temporarily disabled)",
            "status": "ready"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    ) 