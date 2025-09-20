#!/usr/bin/env python3
"""
Celery Beat Schedule Configuration
Automatically runs monitoring and cleanup tasks
"""

from celery.schedules import crontab

# Celery Beat schedule configuration
beat_schedule = {
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
}

# Timezone for scheduled tasks
timezone = 'UTC'
