#!/usr/bin/env python3

"""
PROGRESS TRACKING SYSTEM
Real-time progress tracking for optimized scraping
"""

import time
import threading
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
import json
import logging

logger = logging.getLogger(__name__)

class ProgressTracker:
    """Track progress of scraping operations in real-time"""
    
    def __init__(self, total_websites: int, file_upload_id: str):
        self.total_websites = total_websites
        self.file_upload_id = file_upload_id
        self.start_time = time.time()
        self.lock = threading.Lock()
        
        # Progress tracking
        self.completed_websites = 0
        self.failed_websites = 0
        self.pending_websites = total_websites
        self.current_batch = 0
        self.total_batches = 0
        
        # Performance metrics
        self.websites_per_second = 0.0
        self.estimated_completion = None
        self.average_time_per_website = 0.0
        
        # Resource usage
        self.cpu_usage = 0.0
        self.memory_usage = 0.0
        self.active_tasks = 0
        
        # Status updates
        self.status = "PENDING"
        self.last_update = datetime.now()
        self.error_messages = []
        
        # Progress history
        self.progress_history = []
        
    def update_progress(self, completed: int = 0, failed: int = 0, 
                       current_batch: int = 0, total_batches: int = 0,
                       cpu_usage: float = 0.0, memory_usage: float = 0.0,
                       active_tasks: int = 0, status: str = None):
        """Update progress information"""
        with self.lock:
            if completed > 0:
                self.completed_websites += completed
            if failed > 0:
                self.failed_websites += failed
                
            self.pending_websites = self.total_websites - self.completed_websites - self.failed_websites
            
            if current_batch > 0:
                self.current_batch = current_batch
            if total_batches > 0:
                self.total_batches = total_batches
                
            self.cpu_usage = cpu_usage
            self.memory_usage = memory_usage
            self.active_tasks = active_tasks
            
            if status:
                self.status = status
                
            # Calculate performance metrics
            elapsed_time = time.time() - self.start_time
            if elapsed_time > 0:
                self.websites_per_second = self.completed_websites / elapsed_time
                
                if self.completed_websites > 0:
                    self.average_time_per_website = elapsed_time / self.completed_websites
                    
                    # Estimate completion time
                    remaining_websites = self.pending_websites
                    if self.websites_per_second > 0:
                        estimated_seconds = remaining_websites / self.websites_per_second
                        self.estimated_completion = datetime.now() + timedelta(seconds=estimated_seconds)
            
            self.last_update = datetime.now()
            
            # Record progress history
            self.progress_history.append({
                "timestamp": self.last_update.isoformat(),
                "completed": self.completed_websites,
                "failed": self.failed_websites,
                "pending": self.pending_websites,
                "progress_percent": self.get_progress_percentage(),
                "websites_per_second": self.websites_per_second,
                "cpu_usage": self.cpu_usage,
                "memory_usage": self.memory_usage,
                "active_tasks": self.active_tasks,
                "status": self.status
            })
            
            # Keep only last 100 history entries
            if len(self.progress_history) > 100:
                self.progress_history = self.progress_history[-100:]
    
    def get_progress_percentage(self) -> float:
        """Get progress percentage"""
        if self.total_websites == 0:
            return 0.0
        return (self.completed_websites / self.total_websites) * 100
    
    def get_eta(self) -> Optional[str]:
        """Get estimated time to completion"""
        if self.estimated_completion:
            remaining = self.estimated_completion - datetime.now()
            if remaining.total_seconds() > 0:
                hours = int(remaining.total_seconds() // 3600)
                minutes = int((remaining.total_seconds() % 3600) // 60)
                if hours > 0:
                    return f"{hours}h {minutes}m"
                else:
                    return f"{minutes}m"
        return None
    
    def get_status_summary(self) -> Dict[str, Any]:
        """Get current status summary"""
        with self.lock:
            elapsed_time = time.time() - self.start_time
            
            return {
                "file_upload_id": self.file_upload_id,
                "status": self.status,
                "progress": {
                    "total_websites": self.total_websites,
                    "completed_websites": self.completed_websites,
                    "failed_websites": self.failed_websites,
                    "pending_websites": self.pending_websites,
                    "progress_percentage": self.get_progress_percentage(),
                    "current_batch": self.current_batch,
                    "total_batches": self.total_batches
                },
                "performance": {
                    "elapsed_time_seconds": elapsed_time,
                    "websites_per_second": self.websites_per_second,
                    "average_time_per_website": self.average_time_per_website,
                    "estimated_completion": self.estimated_completion.isoformat() if self.estimated_completion else None,
                    "eta": self.get_eta()
                },
                "resources": {
                    "cpu_usage_percent": self.cpu_usage,
                    "memory_usage_percent": self.memory_usage,
                    "active_tasks": self.active_tasks
                },
                "timestamps": {
                    "start_time": datetime.fromtimestamp(self.start_time).isoformat(),
                    "last_update": self.last_update.isoformat()
                },
                "errors": self.error_messages[-10:]  # Last 10 errors
            }
    
    def add_error(self, error_message: str):
        """Add error message"""
        with self.lock:
            timestamp = datetime.now().isoformat()
            self.error_messages.append({
                "timestamp": timestamp,
                "message": error_message
            })
            
            # Keep only last 50 errors
            if len(self.error_messages) > 50:
                self.error_messages = self.error_messages[-50:]
    
    def mark_completed(self):
        """Mark the entire operation as completed"""
        with self.lock:
            self.status = "COMPLETED"
            self.last_update = datetime.now()
            
            # Final progress update
            self.progress_history.append({
                "timestamp": self.last_update.isoformat(),
                "completed": self.completed_websites,
                "failed": self.failed_websites,
                "pending": self.pending_websites,
                "progress_percent": 100.0,
                "websites_per_second": self.websites_per_second,
                "cpu_usage": self.cpu_usage,
                "memory_usage": self.memory_usage,
                "active_tasks": 0,
                "status": "COMPLETED"
            })
    
    def mark_failed(self, error_message: str):
        """Mark the operation as failed"""
        with self.lock:
            self.status = "FAILED"
            self.last_update = datetime.now()
            self.add_error(error_message)
    
    def get_performance_metrics(self) -> Dict[str, Any]:
        """Get detailed performance metrics"""
        with self.lock:
            elapsed_time = time.time() - self.start_time
            
            # Calculate efficiency metrics
            total_processed = self.completed_websites + self.failed_websites
            success_rate = (self.completed_websites / total_processed * 100) if total_processed > 0 else 0
            
            # Calculate time distribution
            if self.progress_history:
                first_update = self.progress_history[0]["timestamp"]
                last_update = self.progress_history[-1]["timestamp"]
                
                # Parse timestamps and calculate duration
                try:
                    first_time = datetime.fromisoformat(first_update)
                    last_time = datetime.fromisoformat(last_update)
                    processing_duration = (last_time - first_time).total_seconds()
                except:
                    processing_duration = elapsed_time
            else:
                processing_duration = elapsed_time
            
            return {
                "efficiency": {
                    "success_rate_percent": success_rate,
                    "failure_rate_percent": 100 - success_rate,
                    "total_processed": total_processed
                },
                "timing": {
                    "total_elapsed_time": elapsed_time,
                    "processing_duration": processing_duration,
                    "setup_time": elapsed_time - processing_duration if elapsed_time > processing_duration else 0
                },
                "throughput": {
                    "websites_per_second": self.websites_per_second,
                    "websites_per_minute": self.websites_per_second * 60,
                    "websites_per_hour": self.websites_per_second * 3600
                },
                "resource_efficiency": {
                    "websites_per_cpu_percent": self.completed_websites / max(self.cpu_usage, 1),
                    "websites_per_memory_percent": self.completed_websites / max(self.memory_usage, 1)
                }
            }
    
    def export_progress_report(self) -> str:
        """Export progress report as JSON"""
        report = {
            "summary": self.get_status_summary(),
            "performance": self.get_performance_metrics(),
            "progress_history": self.progress_history,
            "error_log": self.error_messages
        }
        
        return json.dumps(report, indent=2, default=str)
    
    def print_progress(self):
        """Print current progress to console"""
        summary = self.get_status_summary()
        
        print(f"\n📊 PROGRESS UPDATE - {summary['timestamps']['last_update']}")
        print(f"📁 File Upload: {self.file_upload_id}")
        print(f"🔄 Status: {summary['status']}")
        print(f"📈 Progress: {summary['progress']['completed_websites']}/{summary['progress']['total_websites']} ({summary['progress']['progress_percentage']:.1f}%)")
        
        if summary['performance']['eta']:
            print(f"⏰ ETA: {summary['performance']['eta']}")
        
        print(f"⚡ Speed: {summary['performance']['websites_per_second']:.2f} websites/second")
        print(f"🖥️  CPU: {summary['resources']['cpu_usage_percent']:.1f}% | 💾 Memory: {summary['resources']['memory_usage_percent']:.1f}%")
        print(f"🚀 Active Tasks: {summary['resources']['active_tasks']}")
        
        if summary['errors']:
            print(f"❌ Recent Errors: {len(summary['errors'])}")
            for error in summary['errors'][-3:]:  # Show last 3 errors
                print(f"   - {error['timestamp']}: {error['message']}")

def main():
    """Test the progress tracker"""
    print("🧪 Testing Progress Tracker...")
    
    # Create tracker
    tracker = ProgressTracker(total_websites=25, file_upload_id="test_upload_123")
    
    # Simulate progress updates
    for i in range(1, 6):
        print(f"\n--- Update {i} ---")
        
        # Simulate processing
        completed = i * 5
        failed = i
        current_batch = i
        cpu_usage = 20 + (i * 10)
        memory_usage = 30 + (i * 5)
        active_tasks = min(10, 25 - completed)
        
        tracker.update_progress(
            completed=5,
            failed=1,
            current_batch=current_batch,
            total_batches=5,
            cpu_usage=cpu_usage,
            memory_usage=memory_usage,
            active_tasks=active_tasks,
            status="PROCESSING"
        )
        
        tracker.print_progress()
        time.sleep(1)
    
    # Mark as completed
    tracker.mark_completed()
    print("\n--- Final Status ---")
    tracker.print_progress()
    
    # Export report
    report = tracker.export_progress_report()
    print(f"\n📄 Progress Report Length: {len(report)} characters")

if __name__ == "__main__":
    main()
