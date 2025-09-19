#!/usr/bin/env python3
"""
Robust Celery Worker Monitor
Automatically restarts crashed workers and provides health monitoring
"""
import time
import subprocess
import psutil
import logging
import os
import signal
from datetime import datetime
import requests
import json

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('/home/xb3353/Automated-AI-Messaging-Tool-Backend/logs/celery_monitor_new.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class CeleryMonitor:
    def __init__(self):
        self.celery_app_path = '/home/xb3353/Automated-AI-Messaging-Tool-Backend'
        self.venv_path = os.path.join(self.celery_app_path, 'venv/bin/activate')
        self.worker_processes = []
        self.max_restart_attempts = 5
        self.restart_cooldown = 30  # seconds
        self.last_restart_time = {}
        
    def get_celery_workers(self):
        """Get list of running Celery worker processes"""
        workers = []
        for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
            try:
                if proc.info['name'] == 'python3' and proc.info['cmdline']:
                    cmdline = ' '.join(proc.info['cmdline'])
                    if 'celery' in cmdline and 'worker' in cmdline:
                        workers.append({
                            'pid': proc.info['pid'],
                            'cmdline': cmdline,
                            'process': proc
                        })
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
        return workers
    
    def is_worker_healthy(self, worker):
        """Check if a worker is healthy by testing its responsiveness"""
        try:
            # Test worker responsiveness
            result = subprocess.run([
                'ssh', '-i', '/Users/apple/.ssh/backend_upload_key', 
                'xb3353@103.215.159.51',
                f'cd {self.celery_app_path} && source venv/bin/activate && celery -A celery_app inspect active'
            ], capture_output=True, text=True, timeout=10)
            
            return result.returncode == 0 and 'worker' in result.stdout
        except Exception as e:
            logger.error(f"Error checking worker health: {e}")
            return False
    
    def restart_worker(self, worker_name, worker_num):
        """Restart a specific Celery worker"""
        try:
            current_time = time.time()
            worker_key = f"{worker_name}_{worker_num}"
            
            # Check restart cooldown
            if worker_key in self.last_restart_time:
                if current_time - self.last_restart_time[worker_key] < self.restart_cooldown:
                    logger.warning(f"Worker {worker_key} restarted too recently, skipping")
                    return False
            
            logger.info(f"Restarting {worker_key}...")
            
            # Kill existing worker process
            subprocess.run([
                'ssh', '-i', '/Users/apple/.ssh/backend_upload_key', 
                'xb3353@103.215.159.51',
                f'pkill -f "celery.*{worker_name}"'
            ], timeout=10)
            
            time.sleep(2)  # Wait for process to terminate
            
            # Start new worker
            start_cmd = [
                'ssh', '-i', '/Users/apple/.ssh/backend_upload_key', 
                'xb3353@103.215.159.51',
                f'cd {self.celery_app_path} && source venv/bin/activate && nohup celery -A celery_app worker --loglevel=info --concurrency=2 --queues=default,scraping,file_processing,ai_processing --hostname={worker_name}@%h --max-tasks-per-child=1000 > /home/xb3353/Automated-AI-Messaging-Tool-Backend/logs/celery_{worker_name}.log 2>&1 &'
            ]
            
            result = subprocess.run(start_cmd, capture_output=True, text=True, timeout=30)
            
            if result.returncode == 0:
                logger.info(f"Successfully restarted {worker_key}")
                self.last_restart_time[worker_key] = current_time
                return True
            else:
                logger.error(f"Failed to restart {worker_key}: {result.stderr}")
                return False
                
        except Exception as e:
            logger.error(f"Error restarting {worker_key}: {e}")
            return False
    
    def check_fastapi_health(self):
        """Check if FastAPI backend is healthy"""
        try:
            response = requests.get('http://103.215.159.51:8000/health', timeout=5)
            return response.status_code == 200
        except Exception as e:
            logger.error(f"FastAPI health check failed: {e}")
            return False
    
    def check_redis_connection(self):
        """Check if Redis is accessible"""
        try:
            result = subprocess.run([
                'ssh', '-i', '/Users/apple/.ssh/backend_upload_key', 
                'xb3353@103.215.159.51',
                'redis-cli ping'
            ], capture_output=True, text=True, timeout=5)
            return result.returncode == 0 and 'PONG' in result.stdout
        except Exception as e:
            logger.error(f"Redis health check failed: {e}")
            return False
    
    def check_database_connection(self):
        """Check if database is accessible"""
        try:
            result = subprocess.run([
                'ssh', '-i', '/Users/apple/.ssh/backend_upload_key', 
                'xb3353@103.215.159.51',
                f'cd {self.celery_app_path} && source venv/bin/activate && python3 -c "import psycopg2; conn = psycopg2.connect(\'postgresql://postgres:cDtrtoOqpdkAzMcLSd%401847@localhost:5432/aimsgdb\'); conn.close(); print(\'DB OK\')"'
            ], capture_output=True, text=True, timeout=10)
            return result.returncode == 0 and 'DB OK' in result.stdout
        except Exception as e:
            logger.error(f"Database health check failed: {e}")
            return False
    
    def monitor_loop(self):
        """Main monitoring loop"""
        logger.info("Starting Celery Monitor...")
        
        while True:
            try:
                # Check system health
                fastapi_healthy = self.check_fastapi_health()
                redis_healthy = self.check_redis_connection()
                db_healthy = self.check_database_connection()
                
                logger.info(f"Health Check - FastAPI: {fastapi_healthy}, Redis: {redis_healthy}, DB: {db_healthy}")
                
                # Get current workers
                workers = self.get_celery_workers()
                logger.info(f"Found {len(workers)} Celery workers")
                
                # Check if we have enough workers
                expected_workers = 2  # We expect 2 workers
                if len(workers) < expected_workers:
                    logger.warning(f"Only {len(workers)} workers running, expected {expected_workers}")
                    
                    # Restart missing workers
                    for i in range(expected_workers - len(workers)):
                        worker_name = f"worker{i+1}"
                        self.restart_worker(worker_name, i+1)
                
                # Check each worker's health
                for worker in workers:
                    if not self.is_worker_healthy(worker):
                        logger.warning(f"Unhealthy worker detected: {worker['pid']}")
                        # Extract worker name from cmdline
                        cmdline = worker['cmdline']
                        if 'worker1' in cmdline:
                            self.restart_worker('worker1', 1)
                        elif 'worker2' in cmdline:
                            self.restart_worker('worker2', 2)
                
                # Log system status
                status = {
                    'timestamp': datetime.now().isoformat(),
                    'fastapi_healthy': fastapi_healthy,
                    'redis_healthy': redis_healthy,
                    'db_healthy': db_healthy,
                    'worker_count': len(workers),
                    'expected_workers': expected_workers
                }
                
                logger.info(f"System Status: {json.dumps(status, indent=2)}")
                
                # Wait before next check
                time.sleep(30)  # Check every 30 seconds
                
            except KeyboardInterrupt:
                logger.info("Monitor stopped by user")
                break
            except Exception as e:
                logger.error(f"Monitor error: {e}")
                time.sleep(60)  # Wait longer on error

if __name__ == "__main__":
    monitor = CeleryMonitor()
    monitor.monitor_loop() 