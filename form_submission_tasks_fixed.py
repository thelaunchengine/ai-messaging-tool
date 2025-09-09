#!/usr/bin/env python3
"""
Contact Form Submission Tasks using Selenium
"""
from celery import current_task
from celery_app import celery_app
import time
import logging
from datetime import datetime
from typing import List, Dict, Any, Optional
from database.database_manager import DatabaseManager
import os
import random
import tempfile
import shutil

logger = logging.getLogger(__name__)

class ContactFormSubmitter:
    """Contact form submission using Selenium automation"""
    
    def __init__(self):
        self.chrome_options = self._setup_chrome_options()
        self.user_config = self._get_user_config()
    
    def _setup_chrome_options(self):
        """Setup Chrome options for automation"""
        from selenium.webdriver.chrome.options import Options
        
        options = Options()
        options.add_argument('--headless')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--disable-blink-features=AutomationControlled')
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option('useAutomationExtension', False)
        options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36')
        
        # Add options to prevent user data directory conflicts
        options.add_argument('--remote-debugging-port=0')
        options.add_argument('--disable-background-timer-throttling')
        options.add_argument('--disable-backgrounding-occluded-windows')
        options.add_argument('--disable-renderer-backgrounding')
        
        return options
    
    def _get_user_config(self):
        """Get user configuration for form submission"""
        return {
            'sender_name': os.getenv('SENDER_NAME', 'John Doe'),
            'sender_email': os.getenv('SENDER_EMAIL', 'john.doe@example.com'),
            'sender_phone': os.getenv('SENDER_PHONE', '+1-555-123-4567'),
            'message_subject': os.getenv('MESSAGE_SUBJECT', 'Business Inquiry'),
            'company_name': os.getenv('COMPANY_NAME', 'Your Company')
        }
    
    def detect_contact_form_fields(self, form_url: str) -> Dict[str, Any]:
        """
        Detect and map contact form fields using Selenium
        """
        driver = None
        temp_dir = None
        try:
            # Create unique user data directory to prevent conflicts
            temp_dir = tempfile.mkdtemp(prefix='chrome_selenium_detect_')
            self.chrome_options.add_argument(f'--user-data-dir={temp_dir}')
            
            from selenium import webdriver
            from webdriver_manager.chrome import ChromeDriverManager
            from selenium.webdriver.chrome.service import Service
            from selenium.webdriver.common.by import By
            from selenium.webdriver.support.ui import WebDriverWait
            from selenium.webdriver.support import expected_conditions as EC
            
            driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=self.chrome_options)
            driver.get(form_url)
            
            # Wait for page to load
            time.sleep(3)
            
            # Find form elements
            form = driver.find_element(By.TAG_NAME, "form")
            
            # Map form fields
            field_mapping = {
                'name': self._detect_name_field(driver),
                'email': self._detect_email_field(driver),
                'phone': self._detect_phone_field(driver),
                'subject': self._detect_subject_field(driver),
                'message': self._detect_message_field(driver),
                'company': self._detect_company_field(driver)
            }
            
            result = {
                'form_element': form,
                'field_mapping': field_mapping,
                'form_action': form.get_attribute('action'),
                'form_method': form.get_attribute('method'),
                'form_url': form_url
            }
            
            return result
            
        except Exception as e:
            logger.error(f"Error detecting form fields: {e}")
            return None
        finally:
            if driver:
                driver.quit()
            # Clean up temporary directory
            if temp_dir and os.path.exists(temp_dir):
                try:
                    shutil.rmtree(temp_dir)
                    logger.info(f"Cleaned up temporary Chrome directory: {temp_dir}")
                except Exception as cleanup_error:
                    logger.warning(f"Could not clean up temporary directory {temp_dir}: {cleanup_error}")
    
    def _detect_name_field(self, driver) -> Optional[str]:
        """Detect name input field"""
        from selenium.webdriver.common.by import By
        
        name_selectors = [
            "input[name*='name' i]",
            "input[id*='name' i]",
            "input[placeholder*='name' i]",
            "input[type='text'][name*='first' i]",
            "input[type='text'][name*='last' i]"
        ]
        
        for selector in name_selectors:
            try:
                element = driver.find_element(By.CSS_SELECTOR, selector)
                if element.is_displayed():
                    return selector
            except:
                continue
        
        return None
    
    def _detect_email_field(self, driver) -> Optional[str]:
        """Detect email input field"""
        from selenium.webdriver.common.by import By
        
        email_selectors = [
            "input[type='email']",
            "input[name*='email' i]",
            "input[id*='email' i]",
            "input[placeholder*='email' i]"
        ]
        
        for selector in email_selectors:
            try:
                element = driver.find_element(By.CSS_SELECTOR, selector)
                if element.is_displayed():
                    return selector
            except:
                continue
        
        return None
    
    def _detect_phone_field(self, driver) -> Optional[str]:
        """Detect phone input field"""
        from selenium.webdriver.common.by import By
        
        phone_selectors = [
            "input[type='tel']",
            "input[name*='phone' i]",
            "input[id*='phone' i]",
            "input[placeholder*='phone' i]"
        ]
        
        for selector in phone_selectors:
            try:
                element = driver.find_element(By.CSS_SELECTOR, selector)
                if element.is_displayed():
                    return selector
            except:
                continue
        
        return None
    
    def _detect_subject_field(self, driver) -> Optional[str]:
        """Detect subject input field"""
        from selenium.webdriver.common.by import By
        
        subject_selectors = [
            "input[name*='subject' i]",
            "input[id*='subject' i]",
            "input[placeholder*='subject' i]",
            "input[type='text'][name*='topic' i]"
        ]
        
        for selector in subject_selectors:
            try:
                element = driver.find_element(By.CSS_SELECTOR, selector)
                if element.is_displayed():
                    return selector
            except:
                continue
        
        return None
    
    def _detect_message_field(self, driver) -> Optional[str]:
        """Detect message input field"""
        from selenium.webdriver.common.by import By
        
        message_selectors = [
            "textarea[name*='message' i]",
            "textarea[id*='message' i]",
            "textarea[placeholder*='message' i]",
            "textarea[name*='comment' i]",
            "textarea[name*='inquiry' i]"
        ]
        
        for selector in message_selectors:
            try:
                element = driver.find_element(By.CSS_SELECTOR, selector)
                if element.is_displayed():
                    return selector
            except:
                continue
        
        return None
    
    def _detect_company_field(self, driver) -> Optional[str]:
        """Detect company input field"""
        from selenium.webdriver.common.by import By
        
        company_selectors = [
            "input[name*='company' i]",
            "input[id*='company' i]",
            "input[placeholder*='company' i]",
            "input[name*='organization' i]"
        ]
        
        for selector in company_selectors:
            try:
                element = driver.find_element(By.CSS_SELECTOR, selector)
                if element.is_displayed():
                    return selector
            except:
                continue
        
        return None
    
    def submit_contact_form(self, form_data: Dict, generated_message: str) -> Dict[str, Any]:
        """
        Submit contact form with generated message
        """
        driver = None
        temp_dir = None
        try:
            # Create unique user data directory to prevent conflicts
            temp_dir = tempfile.mkdtemp(prefix='chrome_selenium_submit_')
            self.chrome_options.add_argument(f'--user-data-dir={temp_dir}')
            
            from selenium import webdriver
            from webdriver_manager.chrome import ChromeDriverManager
            from selenium.webdriver.chrome.service import Service
            from selenium.webdriver.common.by import By
            from selenium.webdriver.support.ui import WebDriverWait
            from selenium.webdriver.support import expected_conditions as EC
            
            driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=self.chrome_options)
            
            # Navigate to form URL
            driver.get(form_data['form_url'])
            time.sleep(2)
            
            # Fill form fields
            field_mapping = form_data['field_mapping']
            
            # Fill name field
            if field_mapping.get('name'):
                try:
                    name_field = driver.find_element(By.CSS_SELECTOR, field_mapping['name'])
                    name_field.clear()
                    name_field.send_keys(self.user_config['sender_name'])
                    logger.info(f"Filled name field: {self.user_config['sender_name']}")
                except Exception as e:
                    logger.warning(f"Could not fill name field: {e}")
            
            # Fill email field
            if field_mapping.get('email'):
                try:
                    email_field = driver.find_element(By.CSS_SELECTOR, field_mapping['email'])
                    email_field.clear()
                    email_field.send_keys(self.user_config['sender_email'])
                    logger.info(f"Filled email field: {self.user_config['sender_email']}")
                except Exception as e:
                    logger.warning(f"Could not fill email field: {e}")
            
            # Fill phone field
            if field_mapping.get('phone'):
                try:
                    phone_field = driver.find_element(By.CSS_SELECTOR, field_mapping['phone'])
                    phone_field.clear()
                    phone_field.send_keys(self.user_config['sender_phone'])
                    logger.info(f"Filled phone field: {self.user_config['sender_phone']}")
                except Exception as e:
                    logger.warning(f"Could not fill phone field: {e}")
            
            # Fill subject field
            if field_mapping.get('subject'):
                try:
                    subject_field = driver.find_element(By.CSS_SELECTOR, field_mapping['subject'])
                    subject_field.clear()
                    subject_field.send_keys(self.user_config['message_subject'])
                    logger.info(f"Filled subject field: {self.user_config['message_subject']}")
                except Exception as e:
                    logger.warning(f"Could not fill subject field: {e}")
            
            # Fill message field
            if field_mapping.get('message'):
                try:
                    message_field = driver.find_element(By.CSS_SELECTOR, field_mapping['message'])
                    message_field.clear()
                    message_field.send_keys(generated_message)
                    logger.info(f"Filled message field with generated message")
                except Exception as e:
                    logger.warning(f"Could not fill message field: {e}")
            
            # Submit form
            try:
                submit_button = driver.find_element(By.CSS_SELECTOR, "input[type='submit'], button[type='submit']")
                submit_button.click()
                logger.info("Form submitted successfully")
            except Exception as e:
                logger.warning(f"Could not find submit button: {e}")
            
            # Wait for submission
            time.sleep(3)
            
            # Check for success indicators
            success_indicators = [
                "thank you",
                "success",
                "submitted",
                "received",
                "sent"
            ]
            
            page_text = driver.page_source.lower()
            submission_successful = any(indicator in page_text for indicator in success_indicators)
            
            result = {
                'success': submission_successful,
                'submission_time': datetime.now(),
                'response_page': driver.page_source[:1000],  # First 1000 chars
                'form_url': form_data['form_url']
            }
            
            return result
            
        except Exception as e:
            logger.error(f"Error submitting form: {e}")
            return {
                'success': False,
                'error': str(e),
                'submission_time': datetime.now(),
                'form_url': form_data.get('form_url', '')
            }
        finally:
            if driver:
                driver.quit()
            # Clean up temporary directory
            if temp_dir and os.path.exists(temp_dir):
                try:
                    shutil.rmtree(temp_dir)
                    logger.info(f"Cleaned up temporary Chrome directory: {temp_dir}")
                except Exception as cleanup_error:
                    logger.warning(f"Could not clean up temporary directory {temp_dir}: {cleanup_error}")

@celery_app.task(bind=True)
def submit_contact_forms_task(self, websites_with_messages: List[Dict], user_config: Dict = None):
    """
    Submit contact forms with generated messages
    """
    logger.info(f"🚀 Contact form submission task started with {len(websites_with_messages)} websites")
    logger.info(f"Task ID: {self.request.id}")
    logger.info(f"Websites: {[w.get('websiteUrl', 'Unknown') for w in websites_with_messages]}")
    
    try:
        submitter = ContactFormSubmitter()
        submission_results = []
        
        total_websites = len(websites_with_messages)
        successful_submissions = 0
        failed_submissions = 0
        
        for i, website in enumerate(websites_with_messages):
            try:
                # Skip if no contact form URL
                if not website.get('contactFormUrl'):
                    logger.info(f"Skipping {website.get('websiteUrl', 'Unknown')} - no contact form URL")
                    continue
                
                logger.info(f"Processing {website.get('websiteUrl', 'Unknown')} - contact form: {website.get('contactFormUrl')}")
                
                # 1. Detect form structure
                form_data = submitter.detect_contact_form_fields(website['contactFormUrl'])
                
                if not form_data:
                    logger.warning(f"Could not detect form structure for {website['websiteUrl']}")
                    failed_submissions += 1
                    continue
                
                # 2. Submit form
                submission_result = submitter.submit_contact_form(
                    form_data=form_data,
                    generated_message=website['generatedMessage']
                )
                
                # 3. Update database
                db_manager = DatabaseManager()
                success = db_manager.update_website_submission(
                    website_id=website.get('id'),
                    submission_status="SUBMITTED" if submission_result['success'] else "FAILED",
                    submission_time=submission_result['submission_time'],
                    response_content=submission_result.get('response_page', ''),
                    error_message=submission_result.get('error', '')
                )
                
                submission_results.append({
                    'website_id': website.get('id'),
                    'url': website.get('websiteUrl'),
                    'contact_form_url': website.get('contactFormUrl'),
                    'success': submission_result['success'],
                    'submission_time': submission_result['submission_time'],
                    'error': submission_result.get('error')
                })
                
                if submission_result['success']:
                    successful_submissions += 1
                else:
                    failed_submissions += 1
                
            except Exception as e:
                logger.error(f"Error processing website {website.get('websiteUrl', 'Unknown')}: {e}")
                failed_submissions += 1
                continue
        
        logger.info(f"Form submission completed. Successful: {successful_submissions}, Failed: {failed_submissions}")
        logger.info(f"✅ Contact form submission task completed successfully")
        logger.info(f"📊 Final Results - Total: {total_websites}, Success: {successful_submissions}, Failed: {failed_submissions}")
        
        return {
            'status': 'success',
            'total_websites': total_websites,
            'successful_submissions': successful_submissions,
            'failed_submissions': failed_submissions,
            'results': submission_results
        }
        
    except Exception as e:
        logger.error(f"Error in contact form submission task: {e}", exc_info=True)
        return {
            'status': 'error',
            'error': str(e)
        }
