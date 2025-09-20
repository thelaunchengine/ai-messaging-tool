"""
Ultra-optimized Celery configuration for AI Messaging Backend
"""
from celery import Celery
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Create Celery instance with optimized settings
celery_app = Celery(
    'ai_messaging_tool',
    broker=os.getenv('REDIS_URL', 'redis://localhost:6379/0'),
    backend=os.getenv('REDIS_URL', 'redis://localhost:6379/0'),
    include=['celery_tasks.scraping_tasks', 'celery_tasks.file_tasks', 'celery_tasks.form_submission_tasks', 'celery_tasks.captcha_handler']
)

# Ultra-optimized Celery configuration
celery_app.conf.update(
    # Serialization
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    
    # Timezone
    timezone='UTC',
    enable_utc=True,
    
    # Task execution
    task_track_started=True,
    task_time_limit=20 * 60,  # 20 minutes (reduced from 30)
    task_soft_time_limit=18 * 60,  # 18 minutes (reduced from 25)
    task_acks_late=True,
    task_reject_on_worker_lost=True,
    
    # Worker optimization
    worker_prefetch_multiplier=1,  # Process one task at a time for better memory management
    worker_max_tasks_per_child=200,  # Restart workers more frequently
    worker_max_memory_per_child=1024 * 1024 * 1024,  # 1GB memory limit per worker
    
    # Result backend optimization
    result_expires=1800,  # Results expire after 30 minutes (reduced from 1 hour)
    result_backend_max_retries=3,
    result_backend_retry_delay=1,
    
    # Broker optimization
    broker_pool_limit=20,  # Increased connection pool
    broker_connection_retry_on_startup=True,
    broker_connection_retry=True,
    broker_connection_max_retries=10,
    
    # Task routing with priority queues
    task_routes={
        'celery_tasks.scraping_tasks.*': {'queue': 'scraping', 'priority': 5},
        'celery_tasks.file_tasks.*': {'queue': 'file_processing', 'priority': 4},
        'celery_tasks.form_submission_tasks.*': {'queue': 'priority', 'priority': 8},
        'celery_tasks.ai_tasks.*': {'queue': 'ai_processing', 'priority': 6},
    },
    
    # Queue configuration
    task_default_queue='default',
    task_default_exchange='default',
    task_default_routing_key='default',
    task_default_priority=5,
    
    # Performance optimizations
    worker_disable_rate_limits=True,
    task_ignore_result=False,
    task_store_eager_result=True,
    
    # Memory optimization
    worker_memory_limit=1024 * 1024 * 1024,  # 1GB per worker
    worker_autoscaler='celery.worker.autoscale:Autoscaler',
    
    # Logging optimization
    worker_log_format='[%(asctime)s: %(levelname)s/%(processName)s] %(message)s',
    worker_task_log_format='[%(asctime)s: %(levelname)s/%(processName)s][%(task_name)s(%(task_id)s)] %(message)s',
    
    # Task compression
    task_compression='gzip',
    result_compression='gzip',
    
    # Connection optimization
    broker_heartbeat=30,  # Reduced heartbeat interval
    broker_connection_timeout=10,
    broker_connection_retry_delay=0.1,
    
    # Task execution optimization
    task_always_eager=False,
    task_eager_propagates=True,
    task_send_sent_event=True,
    
    # Worker pool optimization
    worker_pool='prefork',
    worker_pool_restarts=True,
    worker_pool_putlocks=True,
)

# Set result backend
celery_app.conf.result_backend = os.getenv('REDIS_URL', 'redis://localhost:6379/0')

# Import tasks to ensure they are registered
import celery_tasks.scraping_tasks
import celery_tasks.file_tasks
import celery_tasks.form_submission_tasks

if __name__ == '__main__':
    celery_app.start()
