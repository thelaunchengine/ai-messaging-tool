#!/usr/bin/env python3
"""
Contact Form Submission Celery Tasks
Handles automated contact form submission with AI-generated messages
"""

import logging
import time
from typing import Dict, List, Any, Optional
from celery import current_task
from celery_app import celery_app
from datetime import datetime

# Import our custom modules
from .form_submitter import ContactFormSubmitter
from database.database_manager import DatabaseManager

logger = logging.getLogger(__name__)

@celery_app.task(bind=True)
def submit_contact_forms_task(self, website_data: List[Dict], message_type: str = "general", fileUploadId: str = None, userId: str = None):
    """
    IMMEDIATE contact form submission task - no waiting for other websites!
    
    Args:
        website_data: List of website data dictionaries
        message_type: Type of message (general, partnership, inquiry, custom)
        fileUploadId: File upload ID for tracking
        userId: User ID for tracking
    """
    try:
        logger.info(f"🚀 Starting contact form submission task for {len(website_data)} websites")
        logger.info(f"📝 Message type: {message_type}")
        logger.info(f"📁 File upload ID: {fileUploadId}")
        logger.info(f"👤 User ID: {userId}")
        
        # Initialize form submitter
        form_submitter = ContactFormSubmitter()
        
        # Initialize database manager
        db_manager = DatabaseManager()
        
        # Track results
        results = []
        total_websites = len(website_data)
        successful_submissions = 0
        failed_submissions = 0
        
        for i, website in enumerate(website_data):
            try:
                website_id = website.get('id')
                company_name = website.get('companyName', 'Unknown Company')
                website_url = website.get('websiteUrl', '')
                
                logger.info(f"📝 Processing website {i+1}/{total_websites}: {company_name}")
                
                # Check if website has contact form
                if not website.get('has_contact_form'):
                    logger.info(f"⚠️ No contact form found for {company_name}, skipping")
                    results.append({
                        'website_id': website_id,
                        'company_name': company_name,
                        'success': False,
                        'error': 'No contact form detected',
                        'submission_method': 'none'
                    })
                    failed_submissions += 1
                    continue
                
                # Check if AI message exists
                ai_message = website.get('generatedMessage')
                if not ai_message:
                    logger.warning(f"⚠️ No AI message generated for {company_name}, skipping")
                    results.append({
                        'website_id': website_id,
                        'company_name': company_name,
                        'success': False,
                        'error': 'No AI message generated',
                        'submission_method': 'none'
                    })
                    failed_submissions += 1
                    continue
                
                # Submit contact form
                logger.info(f"📝 Submitting contact form for {company_name}")
                submission_result = form_submitter.submit_contact_form(
                    website_data=website,
                    ai_message=ai_message,
                    message_type=message_type
                )
                
                # Update submission result with website info
                submission_result['website_id'] = website_id
                submission_result['company_name'] = company_name
                submission_result['ai_message'] = ai_message[:100] + '...' if len(ai_message) > 100 else ai_message
                submission_result['submitted_at'] = datetime.now().isoformat()
                
                # Track success/failure
                if submission_result['success']:
                    successful_submissions += 1
                    logger.info(f"✅ Contact form submitted successfully for {company_name}")
                else:
                    failed_submissions += 1
                    logger.error(f"❌ Contact form submission failed for {company_name}: {submission_result.get('error', 'Unknown error')}")
                
                # Add to results
                results.append(submission_result)
                
                # Update progress
                progress = int((i + 1) / total_websites * 100)
                self.update_state(
                    state='PROGRESS',
                    meta={
                        'current': i + 1,
                        'total': total_websites,
                        'progress': progress,
                        'successful_submissions': successful_submissions,
                        'failed_submissions': failed_submissions,
                        'current_website': company_name
                    }
                )
                
                # Add small delay between submissions to avoid overwhelming servers
                time.sleep(2)
                
            except Exception as e:
                logger.error(f"❌ Error processing website {website.get('companyName', 'Unknown')}: {e}")
                results.append({
                    'website_id': website.get('id'),
                    'company_name': website.get('companyName', 'Unknown'),
                    'success': False,
                    'error': str(e),
                    'submission_method': 'error'
                })
                failed_submissions += 1
                continue
        
        # Update database with submission results
        self._update_database_submissions(db_manager, results, fileUploadId, userId)
        
        # Final status update
        final_result = {
            'status': 'completed',
            'total_websites': total_websites,
            'successful_submissions': successful_submissions,
            'failed_submissions': failed_submissions,
            'success_rate': (successful_submissions / total_websites * 100) if total_websites > 0 else 0,
            'results': results,
            'completed_at': datetime.now().isoformat()
        }
        
        logger.info(f"✅ Contact form submission task completed!")
        logger.info(f"📊 Results: {successful_submissions}/{total_websites} successful submissions")
        logger.info(f"📈 Success rate: {final_result['success_rate']:.1f}%")
        
        return final_result
        
    except Exception as e:
        logger.error(f"❌ Fatal error in contact form submission task: {e}")
        
        # Update task state to failed
        self.update_state(
            state='FAILURE',
            meta={
                'error': str(e),
                'failed_at': datetime.now().isoformat()
            }
        )
        
        # Re-raise to mark task as failed
        raise
    
    def _update_database_submissions(self, db_manager: DatabaseManager, results: List[Dict], fileUploadId: str, userId: str):
        """Update database with submission results"""
        try:
            for result in results:
                website_id = result.get('website_id')
                if not website_id:
                    continue
                
                # Update website submission status
                submission_status = 'SUBMITTED' if result['success'] else 'FAILED'
                
                db_manager.update_website_submission_status(
                    website_id=website_id,
                    status=submission_status,
                    submitted_at=datetime.now() if result['success'] else None,
                    error_message=result.get('error') if not result['success'] else None,
                    response_received=False,  # Will be updated when response is received
                    submission_method=result.get('submission_method', 'unknown')
                )
                
                # Create form submission record
                db_manager.create_form_submission(
                    website_id=website_id,
                    file_upload_id=fileUploadId,
                    user_id=userId,
                    submission_status=submission_status,
                    submitted_message=result.get('ai_message', ''),
                    message_type=result.get('message_type', 'general'),
                    contact_form_url=result.get('contact_form_url', ''),
                    form_fields_used=result.get('form_fields_used', {}),
                    submission_method=result.get('submission_method', 'unknown'),
                    submitted_at=datetime.now() if result['success'] else None,
                    response_received=False,
                    error_message=result.get('error') if not result['success'] else None,
                    retry_count=0,
                    max_retries=3
                )
                
                logger.info(f"✅ Updated database for website {result.get('company_name', 'Unknown')}")
                
        except Exception as e:
            logger.error(f"❌ Error updating database with submission results: {e}")

@celery_app.task(bind=True)
def retry_failed_submissions_task(self, submission_ids: List[str], message_type: str = "general"):
    """
    Retry failed contact form submissions
    
    Args:
        submission_ids: List of submission IDs to retry
        message_type: Type of message to use for retry
    """
    try:
        logger.info(f"🔄 Starting retry task for {len(submission_ids)} failed submissions")
        
        # Initialize form submitter
        form_submitter = ContactFormSubmitter()
        
        # Initialize database manager
        db_manager = DatabaseManager()
        
        retry_results = []
        
        for submission_id in submission_ids:
            try:
                # Get submission details from database
                submission = db_manager.get_form_submission_by_id(submission_id)
                if not submission:
                    logger.warning(f"⚠️ Submission {submission_id} not found, skipping")
                    continue
                
                # Get website data
                website = db_manager.get_website_by_id(submission['website_id'])
                if not website:
                    logger.warning(f"⚠️ Website for submission {submission_id} not found, skipping")
                    continue
                
                # Check retry limit
                if submission['retry_count'] >= submission['max_retries']:
                    logger.warning(f"⚠️ Submission {submission_id} has reached max retries, skipping")
                    continue
                
                # Retry submission
                logger.info(f"🔄 Retrying submission for {website.get('companyName', 'Unknown')}")
                
                submission_result = form_submitter.submit_contact_form(
                    website_data=website,
                    ai_message=submission['submitted_message'],
                    message_type=message_type
                )
                
                # Update retry count
                db_manager.update_submission_retry_count(submission_id, submission['retry_count'] + 1)
                
                # Update submission status if successful
                if submission_result['success']:
                    db_manager.update_form_submission_status(
                        submission_id=submission_id,
                        status='SUBMITTED',
                        submitted_at=datetime.now(),
                        submission_method=submission_result.get('submission_method', 'retry')
                    )
                    
                    # Update website status
                    db_manager.update_website_submission_status(
                        website_id=website['id'],
                        status='SUBMITTED',
                        submitted_at=datetime.now(),
                        submission_method=submission_result.get('submission_method', 'retry')
                    )
                    
                    logger.info(f"✅ Retry successful for {website.get('companyName', 'Unknown')}")
                else:
                    logger.error(f"❌ Retry failed for {website.get('companyName', 'Unknown')}: {submission_result.get('error', 'Unknown error')}")
                
                retry_results.append({
                    'submission_id': submission_id,
                    'website_name': website.get('companyName', 'Unknown'),
                    'success': submission_result['success'],
                    'error': submission_result.get('error'),
                    'retry_count': submission['retry_count'] + 1
                })
                
                # Add delay between retries
                time.sleep(3)
                
            except Exception as e:
                logger.error(f"❌ Error retrying submission {submission_id}: {e}")
                retry_results.append({
                    'submission_id': submission_id,
                    'success': False,
                    'error': str(e)
                })
        
        logger.info(f"✅ Retry task completed for {len(submission_ids)} submissions")
        return {
            'status': 'completed',
            'total_retries': len(submission_ids),
            'results': retry_results
        }
        
    except Exception as e:
        logger.error(f"❌ Fatal error in retry task: {e}")
        raise

@celery_app.task(bind=True)
def monitor_submission_responses_task(self, submission_ids: List[str]):
    """
    Monitor for responses to submitted contact forms
    
    Args:
        submission_ids: List of submission IDs to monitor
    """
    try:
        logger.info(f"👀 Starting response monitoring for {len(submission_ids)} submissions")
        
        # This task would typically:
        # 1. Check email accounts for responses
        # 2. Monitor website contact forms for replies
        # 3. Update database with response information
        
        # For now, just log that monitoring is active
        logger.info(f"👀 Response monitoring active for {len(submission_ids)} submissions")
        
        return {
            'status': 'monitoring',
            'submissions_monitored': len(submission_ids),
            'message': 'Response monitoring is active'
        }
        
    except Exception as e:
        logger.error(f"❌ Error in response monitoring task: {e}")
        raise
