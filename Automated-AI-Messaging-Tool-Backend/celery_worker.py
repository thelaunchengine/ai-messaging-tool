#!/usr/bin/env python3
"""
Celery Worker for AI Messaging Backend
Run this script to start Celery workers for processing background tasks
"""

import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from celery_app import celery_app

if __name__ == '__main__':
    # Get worker number from environment variable or default to 1
    worker_num = os.getenv('WORKER_NUM', '1')
    
    # Start the Celery worker
    celery_app.worker_main([
        'worker',
        '--loglevel=info',
        '--concurrency=8',  # Number of worker processes
        '--queues=default,scraping,file_processing,ai_processing',  # All queues
        f'--hostname=worker{worker_num}@%h',  # Unique worker hostname
        '--max-tasks-per-child=1000',  # Restart worker after 1000 tasks
    ]) 