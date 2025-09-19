"""
WebSocket server for real-time updates
"""
import asyncio
import json
import logging
from typing import Dict, Set
from fastapi import WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse
import psutil
import time
from datetime import datetime

logger = logging.getLogger(__name__)

class WebSocketManager:
    def __init__(self):
        self.active_connections: Dict[str, Set[WebSocket]] = {}
        self.system_metrics = {}
        
    async def connect(self, websocket: WebSocket, client_id: str):
        await websocket.accept()
        if client_id not in self.active_connections:
            self.active_connections[client_id] = set()
        self.active_connections[client_id].add(websocket)
        logger.info(f"Client {client_id} connected. Total connections: {len(self.active_connections)}")
        
    def disconnect(self, websocket: WebSocket, client_id: str):
        if client_id in self.active_connections:
            self.active_connections[client_id].discard(websocket)
            if not self.active_connections[client_id]:
                del self.active_connections[client_id]
        logger.info(f"Client {client_id} disconnected. Total connections: {len(self.active_connections)}")
        
    async def send_personal_message(self, message: str, client_id: str):
        if client_id in self.active_connections:
            for connection in self.active_connections[client_id]:
                try:
                    await connection.send_text(message)
                except Exception as e:
                    logger.error(f"Error sending message to {client_id}: {e}")
                    self.disconnect(connection, client_id)
                    
    async def broadcast(self, message: str):
        for client_id in list(self.active_connections.keys()):
            await self.send_personal_message(message, client_id)
            
    async def send_task_progress(self, task_id: str, progress_data: dict):
        """Send task progress updates to subscribed clients"""
        message = {
            "type": "task_progress",
            "task_id": task_id,
            "data": progress_data,
            "timestamp": datetime.now().isoformat()
        }
        
        # Send to clients subscribed to this specific task
        event_name = f"task_progress_{task_id}"
        if event_name in self.active_connections:
            for connection in self.active_connections[event_name]:
                try:
                    await connection.send_text(json.dumps(message))
                except Exception as e:
                    logger.error(f"Error sending task progress: {e}")
                    
    async def send_file_upload_progress(self, file_upload_id: str, progress_data: dict):
        """Send file upload progress updates"""
        message = {
            "type": "file_upload_progress",
            "file_upload_id": file_upload_id,
            "data": progress_data,
            "timestamp": datetime.now().isoformat()
        }
        
        event_name = f"file_upload_progress_{file_upload_id}"
        if event_name in self.active_connections:
            for connection in self.active_connections[event_name]:
                try:
                    await connection.send_text(json.dumps(message))
                except Exception as e:
                    logger.error(f"Error sending file upload progress: {e}")
                    
    async def send_scraping_job_update(self, job_id: str, job_data: dict):
        """Send scraping job updates"""
        message = {
            "type": "scraping_job_update",
            "job_id": job_id,
            "data": job_data,
            "timestamp": datetime.now().isoformat()
        }
        
        event_name = f"scraping_job_update_{job_id}"
        if event_name in self.active_connections:
            for connection in self.active_connections[event_name]:
                try:
                    await connection.send_text(json.dumps(message))
                except Exception as e:
                    logger.error(f"Error sending scraping job update: {e}")
                    
    async def send_message_generation_update(self, file_upload_id: str, generation_data: dict):
        """Send message generation updates"""
        message = {
            "type": "message_generation_update",
            "file_upload_id": file_upload_id,
            "data": generation_data,
            "timestamp": datetime.now().isoformat()
        }
        
        event_name = f"message_generation_update_{file_upload_id}"
        if event_name in self.active_connections:
            for connection in self.active_connections[event_name]:
                try:
                    await connection.send_text(json.dumps(message))
                except Exception as e:
                    logger.error(f"Error sending message generation update: {e}")
                    
    async def send_form_submission_update(self, file_upload_id: str, submission_data: dict):
        """Send form submission updates"""
        message = {
            "type": "form_submission_update",
            "file_upload_id": file_upload_id,
            "data": submission_data,
            "timestamp": datetime.now().isoformat()
        }
        
        event_name = f"form_submission_update_{file_upload_id}"
        if event_name in self.active_connections:
            for connection in self.active_connections[event_name]:
                try:
                    await connection.send_text(json.dumps(message))
                except Exception as e:
                    logger.error(f"Error sending form submission update: {e}")
                    
    def get_system_metrics(self) -> dict:
        """Get current system metrics"""
        try:
            cpu_percent = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('/')
            
            return {
                "cpu": cpu_percent,
                "memory": memory.percent,
                "disk": (disk.used / disk.total) * 100,
                "network": 0,  # Placeholder for network metrics
                "active_tasks": len(self.active_connections),
                "queue_size": 0,  # Placeholder for queue size
                "error_rate": 0,  # Placeholder for error rate
                "success_rate": 95,  # Placeholder for success rate
                "timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            logger.error(f"Error getting system metrics: {e}")
            return {
                "cpu": 0,
                "memory": 0,
                "disk": 0,
                "network": 0,
                "active_tasks": 0,
                "queue_size": 0,
                "error_rate": 0,
                "success_rate": 0,
                "timestamp": datetime.now().isoformat()
            }

# Create global WebSocket manager instance
websocket_manager = WebSocketManager()

async def websocket_endpoint(websocket: WebSocket, client_id: str = None):
    """WebSocket endpoint for real-time updates"""
    if not client_id:
        client_id = f"client_{int(time.time())}"
        
    await websocket_manager.connect(websocket, client_id)
    
    try:
        while True:
            # Receive message from client
            data = await websocket.receive_text()
            message = json.loads(data)
            
            # Handle different message types
            if message.get("type") == "subscribe_task":
                task_id = message.get("task_id")
                if task_id:
                    event_name = f"task_progress_{task_id}"
                    if event_name not in websocket_manager.active_connections:
                        websocket_manager.active_connections[event_name] = set()
                    websocket_manager.active_connections[event_name].add(websocket)
                    logger.info(f"Client {client_id} subscribed to task {task_id}")
                    
            elif message.get("type") == "subscribe_file_upload":
                file_upload_id = message.get("file_upload_id")
                if file_upload_id:
                    event_name = f"file_upload_progress_{file_upload_id}"
                    if event_name not in websocket_manager.active_connections:
                        websocket_manager.active_connections[event_name] = set()
                    websocket_manager.active_connections[event_name].add(websocket)
                    logger.info(f"Client {client_id} subscribed to file upload {file_upload_id}")
                    
            elif message.get("type") == "subscribe_scraping_job":
                job_id = message.get("job_id")
                if job_id:
                    event_name = f"scraping_job_update_{job_id}"
                    if event_name not in websocket_manager.active_connections:
                        websocket_manager.active_connections[event_name] = set()
                    websocket_manager.active_connections[event_name].add(websocket)
                    logger.info(f"Client {client_id} subscribed to scraping job {job_id}")
                    
            elif message.get("type") == "subscribe_message_generation":
                file_upload_id = message.get("file_upload_id")
                if file_upload_id:
                    event_name = f"message_generation_update_{file_upload_id}"
                    if event_name not in websocket_manager.active_connections:
                        websocket_manager.active_connections[event_name] = set()
                    websocket_manager.active_connections[event_name].add(websocket)
                    logger.info(f"Client {client_id} subscribed to message generation {file_upload_id}")
                    
            elif message.get("type") == "subscribe_form_submission":
                file_upload_id = message.get("file_upload_id")
                if file_upload_id:
                    event_name = f"form_submission_update_{file_upload_id}"
                    if event_name not in websocket_manager.active_connections:
                        websocket_manager.active_connections[event_name] = set()
                    websocket_manager.active_connections[event_name].add(websocket)
                    logger.info(f"Client {client_id} subscribed to form submission {file_upload_id}")
                    
            elif message.get("type") == "ping":
                # Respond to ping with pong
                await websocket.send_text(json.dumps({"type": "pong", "timestamp": datetime.now().isoformat()}))
                
    except WebSocketDisconnect:
        websocket_manager.disconnect(websocket, client_id)
    except Exception as e:
        logger.error(f"WebSocket error for client {client_id}: {e}")
        websocket_manager.disconnect(websocket, client_id)

async def system_metrics_broadcast():
    """Broadcast system metrics periodically"""
    while True:
        try:
            metrics = websocket_manager.get_system_metrics()
            await websocket_manager.broadcast(json.dumps({
                "type": "system_metrics",
                "data": metrics
            }))
            await asyncio.sleep(5)  # Update every 5 seconds
        except Exception as e:
            logger.error(f"Error broadcasting system metrics: {e}")
            await asyncio.sleep(5)

# Start system metrics broadcast in background
def start_system_metrics_broadcast():
    """Start the system metrics broadcast loop"""
    loop = asyncio.get_event_loop()
    loop.create_task(system_metrics_broadcast()) 