# MONITORING ENDPOINTS
# These endpoints provide real-time monitoring and progress tracking

from fastapi import APIRouter, HTTPException
from typing import Dict, Any
import psutil
import time

router = APIRouter()

@router.get("/api/monitoring/system-resources")
async def get_system_resources() -> Dict[str, Any]:
    """Get current system resource usage"""
    try:
        cpu_percent = psutil.cpu_percent(interval=1)
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage('/')
        
        return {
            "timestamp": time.time(),
            "cpu": {
                "usage_percent": cpu_percent,
                "count": psutil.cpu_count(),
                "frequency": psutil.cpu_freq()._asdict() if psutil.cpu_freq() else None
            },
            "memory": {
                "total_gb": memory.total / (1024**3),
                "available_gb": memory.available / (1024**3),
                "used_gb": memory.used / (1024**3),
                "usage_percent": memory.percent
            },
            "disk": {
                "total_gb": disk.total / (1024**3),
                "used_gb": disk.used / (1024**3),
                "free_gb": disk.free / (1024**3),
                "usage_percent": (disk.used / disk.total) * 100
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting system resources: {str(e)}")

@router.get("/api/monitoring/scraping-progress/{file_upload_id}")
async def get_scraping_progress(file_upload_id: str) -> Dict[str, Any]:
    """Get scraping progress for a specific file upload"""
    try:
        # This would integrate with the ProgressTracker
        # For now, return a placeholder
        return {
            "file_upload_id": file_upload_id,
            "status": "PROCESSING",
            "progress": {
                "total_websites": 0,
                "completed_websites": 0,
                "failed_websites": 0,
                "progress_percentage": 0.0
            },
            "performance": {
                "websites_per_second": 0.0,
                "eta": None
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting progress: {str(e)}")

@router.get("/api/monitoring/celery-workers")
async def get_celery_workers_status() -> Dict[str, Any]:
    """Get status of all Celery workers"""
    try:
        # This would integrate with Celery monitoring
        # For now, return a placeholder
        return {
            "timestamp": time.time(),
            "workers": [
                {
                    "name": "celery-worker-1",
                    "status": "online",
                    "concurrency": 8,
                    "active_tasks": 0,
                    "processed_tasks": 0
                },
                {
                    "name": "celery-worker-2",
                    "status": "online",
                    "concurrency": 8,
                    "active_tasks": 0,
                    "processed_tasks": 0
                },
                {
                    "name": "celery-worker-3",
                    "status": "online",
                    "concurrency": 8,
                    "active_tasks": 0,
                    "processed_tasks": 0
                },
                {
                    "name": "celery-worker-4",
                    "status": "online",
                    "concurrency": 8,
                    "active_tasks": 0,
                    "processed_tasks": 0
                }
            ],
            "total_workers": 4,
            "total_concurrency": 32,
            "total_active_tasks": 0
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting worker status: {str(e)}")

@router.get("/api/monitoring/performance-metrics")
async def get_performance_metrics() -> Dict[str, Any]:
    """Get overall performance metrics"""
    try:
        return {
            "timestamp": time.time(),
            "scraping": {
                "websites_per_second": 0.0,
                "average_time_per_website": 0.0,
                "success_rate_percent": 0.0
            },
            "ai_generation": {
                "messages_per_second": 0.0,
                "average_time_per_message": 0.0,
                "success_rate_percent": 0.0
            },
            "database": {
                "queries_per_second": 0.0,
                "average_query_time": 0.0,
                "active_connections": 0
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting performance metrics: {str(e)}")
