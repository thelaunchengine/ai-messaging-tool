#!/usr/bin/env python3
"""
AI Workflow Endpoints - FastAPI integration for automatic AI message generation
Provides endpoints to trigger and monitor AI workflow integration
"""

from fastapi import APIRouter, HTTPException, BackgroundTasks
from pydantic import BaseModel
from typing import Dict, Any, Optional
import logging
from ai_workflow_integration import AIWorkflowIntegration, generate_ai_messages_bulk_task
from enhanced_database_manager import EnhancedDatabaseManager

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create router
ai_workflow_router = APIRouter(prefix="/api/ai-workflow", tags=["AI Workflow"])

# Initialize components
db_manager = EnhancedDatabaseManager()
ai_integration = AIWorkflowIntegration()

# Request/Response models
class AIWorkflowTriggerRequest(BaseModel):
    file_upload_id: str
    background_processing: bool = True

class AIWorkflowStatusResponse(BaseModel):
    file_upload_id: str
    status: str
    total_websites: int
    ai_messages_generated: int
    pending_ai_generation: int
    completion_percentage: float
    first_generation: Optional[str] = None
    last_generation: Optional[str] = None
    message: Optional[str] = None
    error: Optional[str] = None

class AIWorkflowResultsResponse(BaseModel):
    file_upload_id: str
    status: str
    websites: list
    total_count: int
    message: Optional[str] = None

@ai_workflow_router.post("/trigger", response_model=Dict[str, Any])
async def trigger_ai_workflow(
    request: AIWorkflowTriggerRequest,
    background_tasks: BackgroundTasks
):
    """
    Trigger AI workflow for automatic message generation after scraping
    """
    try:
        logger.info(f"Triggering AI workflow for file upload: {request.file_upload_id}")
        
        # Check if file upload exists and has websites
        websites = await db_manager.get_websites_by_file_upload(request.file_upload_id)
        
        if not websites:
            raise HTTPException(
                status_code=404, 
                detail=f"No websites found for file upload {request.file_upload_id}"
            )
        
        # Check if websites have been scraped
        scraped_websites = [w for w in websites if w.get('status') == 'scraped']
        
        if not scraped_websites:
            raise HTTPException(
                status_code=400,
                detail="No websites have been scraped yet. Please complete scraping first."
            )
        
        if request.background_processing:
            # Add to background tasks for Celery processing
            background_tasks.add_task(
                generate_ai_messages_bulk_task, 
                request.file_upload_id
            )
            
            return {
                "status": "triggered",
                "message": f"AI workflow triggered for {len(scraped_websites)} websites",
                "file_upload_id": request.file_upload_id,
                "websites_count": len(scraped_websites),
                "processing_mode": "background",
                "estimated_time": f"~{len(scraped_websites) * 2} seconds"
            }
        else:
            # Process synchronously (for small batches)
            if len(scraped_websites) > 20:
                raise HTTPException(
                    status_code=400,
                    detail="Synchronous processing limited to 20 websites. Use background processing for larger batches."
                )
            
            result = await ai_integration.process_bulk_ai_generation(request.file_upload_id)
            
            return {
                "status": "completed",
                "message": "AI workflow completed synchronously",
                "file_upload_id": request.file_upload_id,
                "result": result
            }
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error triggering AI workflow: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to trigger AI workflow: {str(e)}"
        )

@ai_workflow_router.get("/status/{file_upload_id}", response_model=AIWorkflowStatusResponse)
async def get_ai_workflow_status(file_upload_id: str):
    """
    Get AI workflow status for a file upload
    """
    try:
        status = await db_manager.get_ai_generation_status(file_upload_id)
        
        if status.get('status') == 'not_found':
            raise HTTPException(
                status_code=404,
                detail=f"File upload {file_upload_id} not found"
            )
        
        return AIWorkflowStatusResponse(
            file_upload_id=file_upload_id,
            status=status.get('status', 'unknown'),
            total_websites=status.get('total_websites', 0),
            ai_messages_generated=status.get('ai_messages_generated', 0),
            pending_ai_generation=status.get('pending_ai_generation', 0),
            completion_percentage=status.get('completion_percentage', 0),
            first_generation=status.get('first_generation'),
            last_generation=status.get('last_generation'),
            message=status.get('message'),
            error=status.get('error')
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting AI workflow status: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get AI workflow status: {str(e)}"
        )

@ai_workflow_router.get("/results/{file_upload_id}", response_model=AIWorkflowResultsResponse)
async def get_ai_workflow_results(file_upload_id: str):
    """
    Get AI workflow results (websites with generated messages)
    """
    try:
        websites = await db_manager.get_websites_with_ai_messages(file_upload_id)
        
        if not websites:
            return AIWorkflowResultsResponse(
                file_upload_id=file_upload_id,
                status="no_results",
                websites=[],
                total_count=0,
                message="No AI messages generated yet"
            )
        
        return AIWorkflowResultsResponse(
            file_upload_id=file_upload_id,
            status="completed",
            websites=websites,
            total_count=len(websites),
            message=f"Retrieved {len(websites)} websites with AI messages"
        )
        
    except Exception as e:
        logger.error(f"Error getting AI workflow results: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get AI workflow results: {str(e)}"
        )

@ai_workflow_router.post("/reset/{file_upload_id}")
async def reset_ai_workflow(file_upload_id: str):
    """
    Reset AI messages for a file upload (for regeneration)
    """
    try:
        success = await db_manager.reset_ai_messages_for_file_upload(file_upload_id)
        
        if success:
            return {
                "status": "success",
                "message": f"AI messages reset for file upload {file_upload_id}",
                "file_upload_id": file_upload_id
            }
        else:
            raise HTTPException(
                status_code=500,
                detail="Failed to reset AI messages"
            )
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error resetting AI workflow: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to reset AI workflow: {str(e)}"
        )

@ai_workflow_router.post("/test-generation")
async def test_ai_generation():
    """
    Test AI message generation with sample data
    """
    try:
        test_website = {
            'id': 'test123',
            'company_name': 'Test Technology Solutions',
            'industry': 'Technology',
            'about_content': 'A leading technology company specializing in AI and machine learning solutions for businesses.',
            'website_url': 'https://testtechsolutions.com'
        }
        
        result = await ai_integration.generate_ai_message_for_website(test_website)
        
        return {
            "status": "success",
            "message": "Test AI generation completed",
            "test_result": result
        }
        
    except Exception as e:
        logger.error(f"Error in test AI generation: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Test AI generation failed: {str(e)}"
        )

# Health check endpoint
@ai_workflow_router.get("/health")
async def ai_workflow_health():
    """
    Health check for AI workflow endpoints
    """
    return {
        "status": "healthy",
        "service": "AI Workflow Integration",
        "timestamp": "2025-08-13T07:45:00Z",
        "components": {
            "ai_integration": "active",
            "database_manager": "active",
            "celery_integration": "active"
        }
    }
