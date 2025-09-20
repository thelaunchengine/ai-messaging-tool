"""
Celery configuration for AI Messaging Backend
"""
from celery import Celery
from celery.schedules import crontab
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Create Celery instance
celery_app = Celery(
    'ai_messaging_tool',
    broker=os.getenv('REDIS_URL', 'redis://localhost:6379/0'),
    backend=os.getenv('REDIS_URL', 'redis://localhost:6379/0'),
    include=['celery_tasks.scraping_tasks', 'celery_tasks.file_tasks', 'celery_tasks.form_submission_tasks', 'celery_tasks.captcha_handler', 'celery_tasks.monitor_tasks']
)

# Celery configuration
celery_app.conf.update(
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='UTC',
    enable_utc=True,
    task_track_started=True,
    task_time_limit=30 * 60,  # 30 minutes
    task_soft_time_limit=25 * 60,  # 25 minutes
    worker_prefetch_multiplier=1,  # Process one task at a time
    task_acks_late=True,  # Acknowledge task only after completion
    result_expires=3600,  # Results expire after 1 hour
    worker_max_tasks_per_child=1000,  # Restart worker after 1000 tasks
    task_routes={
        'celery_tasks.scraping_tasks.*': {'queue': 'scraping'},
        'celery_tasks.file_tasks.*': {'queue': 'file_processing'},
        'celery_tasks.ai_tasks.*': {'queue': 'ai_processing'},
        'celery_tasks.form_submission_tasks.*': {'queue': 'form_submission'},
        'celery_tasks.ultra_fast_form_submission.*': {'queue': 'form_submission'},
        'monitor_tasks.*': {'queue': 'monitoring'},
    },
    beat_schedule={
        # Check for stuck processes every 5 minutes
        'check-stuck-processes': {
            'task': 'monitor_tasks.check_stuck_processes',
            'schedule': 300.0,  # 5 minutes
        },
        
        # Clean up old failed uploads daily at 2 AM
        'cleanup-old-failed-uploads': {
            'task': 'monitor_tasks.cleanup_old_failed_uploads',
            'schedule': crontab(hour=2, minute=0),  # Daily at 2 AM
        },
    },
    task_default_queue='default',
    task_default_exchange='default',
    task_default_routing_key='default',
)

# Optional: Configure task result backend for better monitoring
celery_app.conf.result_backend = os.getenv('REDIS_URL', 'redis://localhost:6379/0')

# Import tasks to ensure they are registered
import celery_tasks.scraping_tasks
import celery_tasks.file_tasks
import celery_tasks.form_submission_tasks
import celery_tasks.ultra_fast_form_submission
import celery_tasks.monitor_tasks

if __name__ == '__main__':
    celery_app.start() 