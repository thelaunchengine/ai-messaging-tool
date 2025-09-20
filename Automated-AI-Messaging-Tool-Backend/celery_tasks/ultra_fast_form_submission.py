#!/usr/bin/env python3
"""
Ultra-Fast Parallel Form Submission System
Optimized for maximum speed and concurrency
"""

import asyncio
import aiohttp
import logging
import json
import time
from typing import Dict, List, Any, Optional
from concurrent.futures import ThreadPoolExecutor, as_completed
from celery import shared_task
from database.database_manager import DatabaseManager
import random

logger = logging.getLogger(__name__)

class UltraFastFormSubmitter:
    """
    Ultra-fast form submission with parallel processing
    """
    
    def __init__(self, max_workers: int = 20):
        self.max_workers = max_workers
        self.session = None
        self.db_manager = DatabaseManager()
    
    async def submit_forms_parallel(self, websites: List[Dict], file_upload_id: str) -> Dict[str, Any]:
        """
        Submit all forms in parallel for maximum speed
        """
        logger.info(f"🚀 Starting ULTRA-FAST parallel form submission for {len(websites)} websites")
        
        # Update file upload status
        self.db_manager.update_file_upload(file_upload_id, {
            'status': 'CONTACT_FORM_SUBMISSION_IN_PROGRESS'
        })
        
        # Filter websites with contact forms
        websites_with_forms = [w for w in websites if w.get('contactFormUrl')]
        logger.info(f"📊 {len(websites_with_forms)} websites have contact forms")
        
        if not websites_with_forms:
            logger.warning("No websites with contact forms found")
            return {
                'successful_submissions': 0,
                'failed_submissions': 0,
                'total_websites': len(websites)
            }
        
        # Process in parallel batches
        batch_size = 50  # Process 50 websites at once
        results = {
            'successful_submissions': 0,
            'failed_submissions': 0,
            'total_websites': len(websites_with_forms),
            'results': []
        }
        
        for i in range(0, len(websites_with_forms), batch_size):
            batch = websites_with_forms[i:i + batch_size]
            logger.info(f"🔥 Processing batch {i//batch_size + 1}: {len(batch)} websites")
            
            # Process batch in parallel
            batch_results = await self._process_batch_parallel(batch)
            
            # Update results
            results['successful_submissions'] += batch_results['successful']
            results['failed_submissions'] += batch_results['failed']
            results['results'].extend(batch_results['results'])
            
            # Update progress
            progress = min(100, int((i + len(batch)) / len(websites_with_forms) * 100))
            logger.info(f"📈 Progress: {progress}% - {results['successful_submissions']} successful, {results['failed_submissions']} failed")
        
        # Update final status
        if results['successful_submissions'] > 0:
            status = 'CONTACT_FORM_SUBMISSION_COMPLETED' if results['failed_submissions'] == 0 else 'CONTACT_FORM_SUBMISSION_PARTIAL'
            self.db_manager.update_file_upload(file_upload_id, {
                'status': status,
                'contactFormsProcessed': results['successful_submissions'],
                'failedSubmissions': results['failed_submissions']
            })
        else:
            self.db_manager.update_file_upload(file_upload_id, {
                'status': 'CONTACT_FORM_SUBMISSION_FAILED',
                'failedSubmissions': results['failed_submissions']
            })
        
        logger.info(f"🎯 ULTRA-FAST submission completed: {results['successful_submissions']} successful, {results['failed_submissions']} failed")
        return results
    
    async def _process_batch_parallel(self, websites: List[Dict]) -> Dict[str, Any]:
        """
        Process a batch of websites in parallel using asyncio
        """
        async with aiohttp.ClientSession(
            timeout=aiohttp.ClientTimeout(total=30),  # 30 second timeout per request
            connector=aiohttp.TCPConnector(limit=100, limit_per_host=20)  # High concurrency
        ) as session:
            
            # Create tasks for all websites in the batch
            tasks = []
            for website in websites:
                task = self._submit_single_form_async(session, website)
                tasks.append(task)
            
            # Execute all tasks in parallel
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Process results
            successful = 0
            failed = 0
            processed_results = []
            
            for i, result in enumerate(results):
                if isinstance(result, Exception):
                    logger.error(f"❌ Exception for {websites[i].get('websiteUrl')}: {result}")
                    failed += 1
                    processed_results.append({
                        'website_id': websites[i].get('id'),
                        'url': websites[i].get('websiteUrl'),
                        'success': False,
                        'error': str(result)
                    })
                elif result.get('success'):
                    successful += 1
                    processed_results.append(result)
                else:
                    failed += 1
                    processed_results.append(result)
            
            return {
                'successful': successful,
                'failed': failed,
                'results': processed_results
            }
    
    async def _submit_single_form_async(self, session: aiohttp.ClientSession, website: Dict) -> Dict[str, Any]:
        """
        Submit a single form asynchronously - ULTRA FAST version
        """
        try:
            website_url = website.get('websiteUrl', 'Unknown')
            contact_form_url = website.get('contactFormUrl')
            generated_message = website.get('generatedMessage', '')
            
            # Skip if no contact form URL
            if not contact_form_url:
                return {
                    'website_id': website.get('id'),
                    'url': website_url,
                    'success': False,
                    'error': 'No contact form URL'
                }
            
            # ULTRA-FAST form submission using HTTP requests (no Selenium overhead)
            submission_result = await self._submit_form_http_fast(session, contact_form_url, generated_message, website)
            
            # Update database asynchronously
            if submission_result.get('success'):
                self.db_manager.update_website_submission(
                    website_id=website.get('id'),
                    submission_status="SUBMITTED",
                    submission_time=submission_result.get('submission_time'),
                    response_content=submission_result.get('response_page', ''),
                    submitted_form_fields=json.dumps(submission_result.get('fields_submitted', {}))
                )
            else:
                self.db_manager.update_website_submission(
                    website_id=website.get('id'),
                    submission_status="FAILED",
                    submission_time=submission_result.get('submission_time'),
                    error_message=submission_result.get('error', 'Unknown error'),
                    submitted_form_fields=json.dumps(submission_result.get('fields_submitted', {}))
                )
            
            return {
                'website_id': website.get('id'),
                'url': website_url,
                'success': submission_result.get('success', False),
                'submission_time': submission_result.get('submission_time'),
                'error': submission_result.get('error'),
                'fields_submitted': submission_result.get('fields_submitted', {})
            }
            
        except Exception as e:
            logger.error(f"❌ Error submitting form for {website.get('websiteUrl')}: {e}")
            return {
                'website_id': website.get('id'),
                'url': website.get('websiteUrl'),
                'success': False,
                'error': str(e)
            }
    
    async def _submit_form_http_fast(self, session: aiohttp.ClientSession, form_url: str, message: str, website: Dict) -> Dict[str, Any]:
        """
        Ultra-fast HTTP form submission (no Selenium)
        """
        try:
            # Generate realistic form data
            form_data = {
                'name': f"{website.get('companyName', 'John')} {website.get('businessType', 'Smith')}",
                'email': f"contact@{website.get('companyName', 'company').lower().replace(' ', '')}.com",
                'phone': f"555-{random.randint(100, 999)}-{random.randint(1000, 9999)}",
                'message': message,
                'company': website.get('companyName', 'Company'),
                'subject': f"Inquiry about {website.get('industry', 'services')}",
                'website': website.get('websiteUrl', ''),
                'industry': website.get('industry', 'General')
            }
            
            # Try common form field names
            possible_fields = {
                'name': ['name', 'fullname', 'full_name', 'contact_name', 'firstname', 'lastname'],
                'email': ['email', 'email_address', 'e-mail', 'contact_email'],
                'phone': ['phone', 'telephone', 'phone_number', 'mobile', 'cell'],
                'message': ['message', 'comments', 'inquiry', 'description', 'details'],
                'company': ['company', 'company_name', 'business', 'organization'],
                'subject': ['subject', 'topic', 'inquiry_type', 'reason']
            }
            
            # Try multiple form submission strategies
            strategies = [
                self._try_post_form,
                self._try_get_form,
                self._try_ajax_form
            ]
            
            for strategy in strategies:
                try:
                    result = await strategy(session, form_url, form_data, possible_fields)
                    if result.get('success'):
                        return result
                except Exception as e:
                    logger.debug(f"Strategy {strategy.__name__} failed: {e}")
                    continue
            
            # If all strategies fail, return failure
            return {
                'success': False,
                'error': 'All form submission strategies failed',
                'submission_time': time.time()
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f"Form submission error: {e}",
                'submission_time': time.time()
            }
    
    async def _try_post_form(self, session: aiohttp.ClientSession, form_url: str, form_data: Dict, possible_fields: Dict) -> Dict[str, Any]:
        """Try POST form submission"""
        try:
            # Try common form endpoints
            endpoints = [form_url, f"{form_url}/contact", f"{form_url}/contact-us", f"{form_url}/form"]
            
            for endpoint in endpoints:
                try:
                    async with session.post(endpoint, data=form_data, allow_redirects=True) as response:
                        if response.status in [200, 201, 302]:
                            return {
                                'success': True,
                                'response_page': await response.text(),
                                'submission_time': time.time(),
                                'fields_submitted': form_data,
                                'method': 'POST'
                            }
                except Exception:
                    continue
            
            return {'success': False, 'error': 'POST submission failed'}
        except Exception as e:
            return {'success': False, 'error': f'POST error: {e}'}
    
    async def _try_get_form(self, session: aiohttp.ClientSession, form_url: str, form_data: Dict, possible_fields: Dict) -> Dict[str, Any]:
        """Try GET form submission"""
        try:
            # Convert form data to query parameters
            params = {k: v for k, v in form_data.items()}
            
            async with session.get(form_url, params=params, allow_redirects=True) as response:
                if response.status in [200, 201, 302]:
                    return {
                        'success': True,
                        'response_page': await response.text(),
                        'submission_time': time.time(),
                        'fields_submitted': form_data,
                        'method': 'GET'
                    }
            
            return {'success': False, 'error': 'GET submission failed'}
        except Exception as e:
            return {'success': False, 'error': f'GET error: {e}'}
    
    async def _try_ajax_form(self, session: aiohttp.ClientSession, form_url: str, form_data: Dict, possible_fields: Dict) -> Dict[str, Any]:
        """Try AJAX form submission"""
        try:
            headers = {
                'Content-Type': 'application/x-www-form-urlencoded',
                'X-Requested-With': 'XMLHttpRequest',
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            
            async with session.post(form_url, data=form_data, headers=headers, allow_redirects=True) as response:
                if response.status in [200, 201, 302]:
                    return {
                        'success': True,
                        'response_page': await response.text(),
                        'submission_time': time.time(),
                        'fields_submitted': form_data,
                        'method': 'AJAX'
                    }
            
            return {'success': False, 'error': 'AJAX submission failed'}
        except Exception as e:
            return {'success': False, 'error': f'AJAX error: {e}'}

@shared_task(bind=True, name="ultra_fast_form_submission.submit_forms_ultra_fast")
def submit_forms_ultra_fast_task(self, websites: List[Dict], file_upload_id: str, user_id: str = None):
    """
    Ultra-fast parallel form submission task
    """
    try:
        logger.info(f"🚀 Starting ULTRA-FAST form submission task for {len(websites)} websites")
        
        # Create submitter with high concurrency
        submitter = UltraFastFormSubmitter(max_workers=50)
        
        # Run async submission
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        try:
            results = loop.run_until_complete(
                submitter.submit_forms_parallel(websites, file_upload_id)
            )
            return results
        finally:
            loop.close()
            
    except Exception as e:
        logger.error(f"❌ Error in ultra-fast form submission task: {e}")
        raise
