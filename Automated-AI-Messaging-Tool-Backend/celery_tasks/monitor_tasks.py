#!/usr/bin/env python3
"""
Monitor and Auto-Retry Stuck Processes
Automatically detects and restarts stuck form submission processes
"""

import logging
import time
from datetime import datetime, timedelta
from typing import List, Dict, Any
from celery import shared_task
from database.database_manager import DatabaseManager
# Lazy import to avoid circular dependency
# from celery_tasks.form_submission_tasks import submit_contact_forms_task

logger = logging.getLogger(__name__)

@shared_task(bind=True, name="monitor_tasks.check_stuck_processes")
def check_stuck_processes_task(self):
    """
    Check for stuck processes and restart them automatically
    Runs every 5 minutes via Celery Beat
    """
    try:
        logger.info("🔍 Checking for stuck processes...")
        
        db_manager = DatabaseManager()
        
        # Find processes that have been stuck for more than 10 minutes
        stuck_threshold = datetime.utcnow() - timedelta(minutes=10)
        
        # Get stuck file uploads
        stuck_uploads = db_manager.get_stuck_uploads(stuck_threshold)
        
        if not stuck_uploads:
            logger.info("✅ No stuck processes found")
            return {'status': 'success', 'stuck_count': 0}
        
        logger.warning(f"⚠️ Found {len(stuck_uploads)} stuck processes")
        
        restarted_count = 0
        for upload in stuck_uploads:
            try:
                # Get websites for this upload that need form submission
                websites = db_manager.get_websites_for_form_submission(upload['id'])
                
                if not websites:
                    logger.info(f"No websites need form submission for upload {upload['id']}")
                    continue
                
                # Restart form submission
                logger.info(f"🔄 Restarting form submission for upload {upload['id']} with {len(websites)} websites")
                
                # Update status to show restart
                db_manager.update_file_upload(upload['id'], {
                    'status': 'CONTACT_FORM_SUBMISSION_RESTARTING',
                    'updatedAt': datetime.utcnow()
                })
                
                # Submit new form submission task (lazy import to avoid circular dependency)
                from celery_tasks.form_submission_tasks import submit_contact_forms_task
                submit_contact_forms_task.delay(
                    websites_with_messages=websites,
                    fileUploadId=upload['id'],
                    userId=upload['userId']
                )
                
                restarted_count += 1
                logger.info(f"✅ Restarted form submission for upload {upload['id']}")
                
            except Exception as e:
                logger.error(f"❌ Failed to restart upload {upload['id']}: {e}")
        
        logger.info(f"🎯 Restarted {restarted_count} stuck processes")
        return {
            'status': 'success', 
            'stuck_count': len(stuck_uploads),
            'restarted_count': restarted_count
        }
        
    except Exception as e:
        logger.error(f"❌ Error in stuck process monitor: {e}")
        return {'status': 'error', 'error': str(e)}

@shared_task(bind=True, name="monitor_tasks.cleanup_old_failed_uploads")
def cleanup_old_failed_uploads_task(self):
    """
    Clean up old failed uploads to prevent database bloat
    Runs daily
    """
    try:
        logger.info("🧹 Starting cleanup of old failed uploads...")
        
        db_manager = DatabaseManager()
        
        # Find uploads that failed more than 7 days ago
        cleanup_threshold = datetime.utcnow() - timedelta(days=7)
        
        # Get old failed uploads
        old_failed_uploads = db_manager.get_old_failed_uploads(cleanup_threshold)
        
        if not old_failed_uploads:
            logger.info("✅ No old failed uploads to clean up")
            return {'status': 'success', 'cleaned_count': 0}
        
        cleaned_count = 0
        for upload in old_failed_uploads:
            try:
                # Delete associated websites first
                db_manager.delete_websites_for_upload(upload['id'])
                
                # Delete the upload
                db_manager.delete_file_upload(upload['id'])
                
                cleaned_count += 1
                logger.info(f"🗑️ Cleaned up old failed upload {upload['id']}")
                
            except Exception as e:
                logger.error(f"❌ Failed to clean up upload {upload['id']}: {e}")
        
        logger.info(f"🎯 Cleaned up {cleaned_count} old failed uploads")
        return {
            'status': 'success', 
            'cleaned_count': cleaned_count
        }
        
    except Exception as e:
        logger.error(f"❌ Error in cleanup task: {e}")
        return {'status': 'error', 'error': str(e)}
