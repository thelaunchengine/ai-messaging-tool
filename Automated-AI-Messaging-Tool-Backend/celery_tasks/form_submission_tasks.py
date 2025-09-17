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

# Import AI-powered form detection
from hybrid_form_detector import HybridFormDetector, DetectionResult
from ai_form_analyzer import AIFormAnalyzer
from celery_tasks.simple_form_submission import SimpleFormSubmitter
from ai_services.intelligent_form_submitter import IntelligentFormSubmitter

logger = logging.getLogger(__name__)

class ContactFormSubmitter:
    """Contact form submission using Selenium automation"""
    
    def __init__(self):
        self.user_config = self._get_user_config()
        self.hybrid_detector = HybridFormDetector()
        self.ai_analyzer = AIFormAnalyzer()
        self.simple_submitter = SimpleFormSubmitter()
        self.intelligent_submitter = IntelligentFormSubmitter()
    
    def _setup_firefox_options(self):
        """Setup Firefox options for automation"""
        from selenium import webdriver
        from selenium.webdriver.firefox.options import Options
        from selenium.webdriver.firefox.service import Service
        import tempfile
        import os
        import uuid
        import time

        options = Options()
        options.add_argument('--headless')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        
        # Create a unique profile directory for this instance
        unique_id = str(uuid.uuid4())[:8]
        timestamp = str(int(time.time() * 1000))
        profile_dir = tempfile.mkdtemp(prefix=f'firefox_selenium_{unique_id}_{timestamp}_')
        
        # Set profile directory
        options.add_argument(f'--profile={profile_dir}')
        
        # Additional Firefox-specific options
        options.add_argument('--disable-gpu')
        options.add_argument('--disable-extensions')
        options.add_argument('--disable-plugins')
        options.add_argument('--disable-images')
        # Enable JavaScript for dynamic forms
        # options.add_argument('--disable-javascript')  # Commented out to allow JS
        options.add_argument('--disable-web-security')
        options.add_argument('--allow-running-insecure-content')
        
        # Memory and process isolation
        options.add_argument('--disable-background-networking')
        options.add_argument('--disable-default-apps')
        options.add_argument('--disable-sync')
        
        # Marionette port fixes
        options.set_preference("marionette.enabled", True)
        options.set_preference("marionette.port", 0)  # Let Firefox choose port
        options.set_preference("marionette.logging", "fatal")
        options.set_preference("browser.cache.disk.enable", False)
        options.set_preference("browser.cache.memory.enable", False)
        options.set_preference("browser.cache.offline.enable", False)
        options.set_preference("network.http.use-cache", False)
        
        # Set user agent
        options.set_preference("general.useragent.override", "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:91.0) Gecko/20100101 Firefox/91.0")
        
        # Additional Firefox preferences
        options.set_preference("dom.webdriver.enabled", False)
        options.set_preference("useAutomationExtension", False)
        
        # Enable JavaScript
        options.set_preference("javascript.enabled", True)
        
        return options, profile_dir

    def _setup_chrome_options(self):
        """Setup Chrome options for automation (fallback)"""
        from selenium import webdriver
        from selenium.webdriver.chrome.options import Options
        import tempfile
        import uuid
        import time
        
        options = Options()
        options.add_argument('--headless')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--disable-blink-features=AutomationControlled')
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option('useAutomationExtension', False)
        options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36')
        
        # Create unique profile directory to avoid conflicts between workers
        unique_id = str(uuid.uuid4())[:8]
        timestamp = str(int(time.time() * 1000))
        profile_dir = tempfile.mkdtemp(prefix=f'chrome_selenium_{unique_id}_{timestamp}_')
        options.add_argument(f'--user-data-dir={profile_dir}')
        
        # Additional stability options
        options.add_argument('--disable-extensions')
        options.add_argument('--disable-plugins')
        options.add_argument('--disable-images')
        # Enable JavaScript for dynamic forms
        # options.add_argument('--disable-javascript')  # Commented out to allow JS
        options.add_argument('--disable-web-security')
        options.add_argument('--allow-running-insecure-content')
        options.add_argument('--disable-features=VizDisplayCompositor')
        
        # Additional options to prevent conflicts
        options.add_argument('--disable-background-timer-throttling')
        options.add_argument('--disable-backgrounding-occluded-windows')
        options.add_argument('--disable-renderer-backgrounding')
        options.add_argument('--disable-features=TranslateUI')
        options.add_argument('--disable-ipc-flooding-protection')
        
        # Memory and process isolation
        options.add_argument('--disable-gpu')
        options.add_argument('--disable-software-rasterizer')
        options.add_argument('--disable-background-networking')
        options.add_argument('--disable-default-apps')
        options.add_argument('--disable-sync')
        
        # Additional isolation options
        options.add_argument('--disable-hang-monitor')
        options.add_argument('--disable-prompt-on-repost')
        options.add_argument('--disable-domain-reliability')
        options.add_argument('--disable-component-extensions-with-background-pages')
        
        # Process isolation
        options.add_argument('--single-process')
        options.add_argument('--disable-background-timer-throttling')
        options.add_argument('--disable-backgrounding-occluded-windows')
        options.add_argument('--disable-renderer-backgrounding')
        
        return options, profile_dir
    
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
        Detect and map contact form fields using hybrid AI + traditional approach
        """
        driver = None
        profile_dir = None
        try:
            # Try Firefox first (more stable)
            try:
                logger.info(f"🔥 Attempting Firefox for form detection: {form_url}")
                firefox_options, profile_dir = self._setup_firefox_options()
            
            from selenium import webdriver
                from selenium.webdriver.firefox.service import Service
            from selenium.webdriver.common.by import By
            from selenium.webdriver.support.ui import WebDriverWait
            from selenium.webdriver.support import expected_conditions as EC
            
                # Create Firefox driver with improved service configuration
                service = Service(
                    executable_path='/usr/local/bin/geckodriver',
                    log_path='/tmp/geckodriver.log'
                )
                driver = webdriver.Firefox(service=service, options=firefox_options)
                
                # Set timeouts for better stability
                driver.set_page_load_timeout(30)
                driver.implicitly_wait(10)

                # Set timeouts
                driver.set_page_load_timeout(30)
                driver.implicitly_wait(10)

                driver.get(form_url)

                # Wait for page to load with better error handling
                try:
                    WebDriverWait(driver, 10).until(
                        lambda d: d.execute_script("return document.readyState") == "complete"
                    )
                except Exception as timeout_error:
                    logger.warning(f"Page load timeout for {form_url}, continuing anyway: {timeout_error}")

                # Additional wait for dynamic content
                time.sleep(2)

                # Use hybrid detection system
                logger.info(f"🔍 Starting hybrid form detection for {form_url}")
                detection_result = self.hybrid_detector.detect_contact_form(form_url, driver)

                if not detection_result.success:
                    logger.error(f"❌ Hybrid form detection failed for {form_url}: {detection_result.error_message}")
                    return None
            
                logger.info(f"✅ Form detection successful using {detection_result.method_used} method")
                logger.info(f"📊 Detection confidence: {detection_result.confidence_score:.2f}")
                logger.info(f"⏱️ Detection time: {detection_result.detection_time:.2f}s")

                # Convert detection result to expected format
                result = {
                    'form_element': detection_result.form_data.get('form_element'),
                    'field_mapping': detection_result.field_mappings,
                    'form_action': detection_result.form_data.get('form_action', ''),
                    'form_method': detection_result.form_data.get('form_method', 'POST'),
                    'form_url': form_url,
                    'detection_method': detection_result.method_used,
                    'confidence_score': detection_result.confidence_score,
                    'submission_strategy': detection_result.submission_strategy
                }

                driver.quit()
                return result

            except Exception as firefox_error:
                logger.warning(f"Firefox failed, trying Chrome fallback: {firefox_error}")
                if driver:
                    driver.quit()
                    driver = None

                # Fallback to Chrome
                logger.info(f"🌐 Attempting Chrome fallback for form detection: {form_url}")
                chrome_options, chrome_profile_dir = self._setup_chrome_options()

                from selenium import webdriver
                from selenium.webdriver.common.by import By
                from selenium.webdriver.support.ui import WebDriverWait
                from selenium.webdriver.support import expected_conditions as EC

                driver = webdriver.Chrome(options=chrome_options)

                # Set timeouts
                driver.set_page_load_timeout(30)
                driver.implicitly_wait(10)

                driver.get(form_url)

                # Wait for page to load with better error handling
                try:
                    WebDriverWait(driver, 10).until(
                        lambda d: d.execute_script("return document.readyState") == "complete"
                    )
                except Exception as timeout_error:
                    logger.warning(f"Page load timeout for {form_url}, continuing anyway: {timeout_error}")

                # Additional wait for dynamic content
                time.sleep(2)

                # Use hybrid detection system
                logger.info(f"🔍 Starting hybrid form detection for {form_url}")
                detection_result = self.hybrid_detector.detect_contact_form(form_url, driver)

                if not detection_result.success:
                    logger.error(f"❌ Hybrid form detection failed for {form_url}: {detection_result.error_message}")
                    return None

                logger.info(f"✅ Form detection successful using {detection_result.method_used} method")
                logger.info(f"📊 Detection confidence: {detection_result.confidence_score:.2f}")
                logger.info(f"⏱️ Detection time: {detection_result.detection_time:.2f}s")

                # Convert detection result to expected format
            result = {
                    'form_element': detection_result.form_data.get('form_element'),
                    'field_mapping': detection_result.field_mappings,
                    'form_action': detection_result.form_data.get('form_action', ''),
                    'form_method': detection_result.form_data.get('form_method', 'POST'),
                    'form_url': form_url,
                    'detection_method': detection_result.method_used,
                    'confidence_score': detection_result.confidence_score,
                    'submission_strategy': detection_result.submission_strategy
            }
            
            driver.quit()
            return result
            
        except Exception as e:
            logger.error(f"Error detecting form fields with Selenium: {e}")
            if driver:
                driver.quit()
            
            # Fallback to simple form detection
            logger.info(f"🔄 Falling back to simple form detection for {form_url}")
            try:
                result = self.simple_submitter.detect_contact_form_fields(form_url)
                if result:
                    logger.info(f"✅ Simple form detection successful for {form_url}")
                    return result
                else:
                    logger.error(f"❌ Simple form detection also failed for {form_url}")
                    return None
            except Exception as simple_error:
                logger.error(f"❌ Simple form detection failed: {simple_error}")
            return None
        finally:
            # Clean up Firefox profile directory
            if profile_dir and os.path.exists(profile_dir):
                try:
                    import shutil
                    shutil.rmtree(profile_dir)
                    logger.info(f"Cleaned up Firefox profile directory: {profile_dir}")
                except Exception as cleanup_error:
                    logger.warning(f"Could not clean up Firefox profile directory {profile_dir}: {cleanup_error}")
            
            # Clean up Chrome profile directory if it exists
            if 'chrome_profile_dir' in locals() and chrome_profile_dir and os.path.exists(chrome_profile_dir):
                try:
                    import shutil
                    shutil.rmtree(chrome_profile_dir)
                    logger.info(f"Cleaned up Chrome profile directory: {chrome_profile_dir}")
                except Exception as cleanup_error:
                    logger.warning(f"Could not clean up Chrome profile directory {chrome_profile_dir}: {cleanup_error}")
    
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
                    logger.debug(f"✅ Found name field using selector: {selector}")
                    return selector
            except Exception as e:
                logger.debug(f"❌ Selector '{selector}' failed: {e}")
                continue
        
        logger.debug(f"⚠️ No name field detected with any selector")
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
            "input[placeholder*='subject' i]"
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
        """Detect message/comment textarea field"""
        from selenium.webdriver.common.by import By
        
        message_selectors = [
            "textarea[name*='message' i]",
            "textarea[name*='comment' i]",
            "textarea[id*='message' i]",
            "textarea[placeholder*='message' i]",
            "textarea[placeholder*='comment' i]"
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
            "input[placeholder*='company' i]"
        ]
        
        for selector in company_selectors:
            try:
                element = driver.find_element(By.CSS_SELECTOR, selector)
                if element.is_displayed():
                    return selector
            except:
                continue
        
        return None
    
    def submit_contact_form_intelligent(self, website_data: Dict, generated_message: str) -> Dict[str, Any]:
        """
        Submit contact form using AI-powered intelligent approach
        This is the primary method that adapts to different platforms
        """
        try:
            logger.info(f"🤖 Using AI-powered intelligent form submission for {website_data.get('websiteUrl', 'Unknown')}")
            
            # Use the intelligent form submitter
            result = self.intelligent_submitter.submit_contact_form(website_data, generated_message)
            
            # Convert SubmissionResult to expected format
            return {
                'success': result.success,
                'error': result.error_message,
                'submission_time': result.submission_time,
                'response_page': result.response_content,
                'submission_method': result.method_used,
                'platform_detected': result.platform_detected,
                'fields_submitted': result.fields_submitted,
                'confidence_score': result.confidence_score,
                'form_url': website_data.get('contactFormUrl', '')
            }
            
        except Exception as e:
            logger.error(f"❌ AI-powered submission failed: {e}")
            return {
                'success': False,
                'error': f"AI-powered submission error: {str(e)}",
                'submission_time': time.strftime('%Y-%m-%d %H:%M:%S'),
                'response_page': None,
                'submission_method': 'ai_error',
                'platform_detected': None,
                'fields_submitted': {},
                'confidence_score': 0.0,
                'form_url': website_data.get('contactFormUrl', '')
            }
    
    def submit_contact_form(self, form_data: Dict, generated_message: str) -> Dict[str, Any]:
        """
        Submit contact form with generated message
        """
        driver = None
        profile_dir = None
        try:
            # Try Firefox first (more stable)
            try:
                logger.info(f"🔥 Attempting Firefox for form submission: {form_data['form_url']}")
                firefox_options, profile_dir = self._setup_firefox_options()
            
            from selenium import webdriver
                from selenium.webdriver.firefox.service import Service
            from selenium.webdriver.common.by import By
            from selenium.webdriver.support.ui import WebDriverWait
            from selenium.webdriver.support import expected_conditions as EC
            
                # Create Firefox driver with improved service configuration
                service = Service(
                    executable_path='/usr/local/bin/geckodriver',
                    log_path='/tmp/geckodriver.log'
                )
                driver = webdriver.Firefox(service=service, options=firefox_options)
                
                # Set timeouts for better stability
                driver.set_page_load_timeout(30)
                driver.implicitly_wait(10)
            except Exception as firefox_error:
                logger.warning(f"Firefox failed, trying Chrome fallback: {firefox_error}")
                if driver:
                    driver.quit()
                    driver = None

                # Fallback to Chrome
                logger.info(f"🌐 Attempting Chrome fallback for form submission: {form_data['form_url']}")
                chrome_options, chrome_profile_dir = self._setup_chrome_options()
                
                from selenium import webdriver
                from selenium.webdriver.common.by import By
                from selenium.webdriver.support.ui import WebDriverWait
                from selenium.webdriver.support import expected_conditions as EC
                
                driver = webdriver.Chrome(options=chrome_options)
            
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
            
            # Handle CAPTCHA if present
            from celery_tasks.captcha_handler import get_captcha_handler
            captcha_handler = get_captcha_handler()
            
            captcha_info = captcha_handler.detect_captcha(driver)
            if captcha_info:
                logger.info(f"CAPTCHA detected, attempting to solve...")
                captcha_solved = captcha_handler.handle_captcha_in_form(driver, captcha_info)
                
                if not captcha_solved:
                    logger.warning("Failed to solve CAPTCHA, proceeding anyway...")
            
            # Submit form
            try:
                submit_button = driver.find_element(By.CSS_SELECTOR, "input[type='submit'], button[type='submit']")
                submit_button.click()
                logger.info("Form submitted successfully")
            except Exception as e:
                logger.warning(f"Could not find submit button: {e}")
                # Try alternative submit methods
                try:
                    submit_button = driver.find_element(By.CSS_SELECTOR, "button:contains('Send'), button:contains('Submit')")
                    submit_button.click()
                except:
                    pass
            
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
            
            driver.quit()
            return result
            
        except Exception as e:
            logger.error(f"Error submitting form with Selenium: {e}")
            selenium_error = str(e)
            if driver:
                driver.quit()
            
            # Fallback to simple form submission
            logger.info(f"🔄 Falling back to simple form submission for {form_data['form_url']}")
            try:
                result = self.simple_submitter.submit_contact_form(form_data, generated_message)
                if result:
                    logger.info(f"✅ Simple form submission successful for {form_data['form_url']}")
                    return result
                else:
                    logger.error(f"❌ Simple form submission also failed for {form_data['form_url']}")
            return {
                'success': False,
                        'error': f'Selenium failed: {selenium_error}. Simple submission returned no result.',
                        'submission_time': datetime.now(),
                        'form_url': form_data.get('form_url', '')
                    }
            except Exception as simple_error:
                logger.error(f"❌ Simple form submission failed: {simple_error}")
                return {
                    'success': False,
                    'error': f"Selenium failed: {str(e)}. Simple submission failed: {str(simple_error)}",
                'submission_time': datetime.now(),
                'form_url': form_data.get('form_url', '')
            }
        finally:
            if driver:
                driver.quit()
            # Clean up Firefox profile directory
            if profile_dir and os.path.exists(profile_dir):
                try:
                    import shutil
                    shutil.rmtree(profile_dir)
                    logger.info(f"Cleaned up Firefox profile directory: {profile_dir}")
                except Exception as cleanup_error:
                    logger.warning(f"Could not clean up Firefox profile directory {profile_dir}: {cleanup_error}")
            
            # Clean up Chrome profile directory if it exists
            if 'chrome_profile_dir' in locals() and chrome_profile_dir and os.path.exists(chrome_profile_dir):
                try:
                    import shutil
                    shutil.rmtree(chrome_profile_dir)
                    logger.info(f"Cleaned up Chrome profile directory: {chrome_profile_dir}")
                except Exception as cleanup_error:
                    logger.warning(f"Could not clean up Chrome profile directory {chrome_profile_dir}: {cleanup_error}")

@celery_app.task(bind=True)
def contact_form_submission_task(self, websites_with_messages: List[Dict], user_config: Dict = None):
    """
    Submit contact forms with generated messages
    """
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
                    logger.info(f"Successfully submitted form for {website.get('websiteUrl')}")
                else:
                    failed_submissions += 1
                    logger.warning(f"Failed to submit form for {website.get('websiteUrl')}: {submission_result.get('error')}")
                
                # 4. Update progress
                progress = int((i + 1) / total_websites * 100)
                self.update_state(
                    state='PROGRESS',
                    meta={
                        'current': i + 1,
                        'total': total_websites,
                        'progress': progress,
                        'successful_submissions': successful_submissions,
                        'failed_submissions': failed_submissions
                    }
                )
                
                # Rate limiting
                time.sleep(random.uniform(2, 5))
                
            except Exception as e:
                failed_submissions += 1
                logger.error(f"Error submitting form for {website.get('websiteUrl', 'Unknown')}: {e}")
                continue
        
        logger.info(f"Form submission completed. Successful: {successful_submissions}, Failed: {failed_submissions}")
        
        return {
            'status': 'success',
            'total_websites': total_websites,
            'successful_submissions': successful_submissions,
            'failed_submissions': failed_submissions,
            'results': submission_results
        }
        
    except Exception as e:
        logger.error(f"Error in form submission task: {e}")
        raise 

@celery_app.task(bind=True)
def submit_contact_forms_task(self, websites_with_messages: List[Dict], user_config: Dict = None):
    """
    Submit contact forms with generated messages - main entry point for automatic triggering
    """
    # Initialize file_upload_id at the top level to avoid UnboundLocalError
    file_upload_id = None
    
    try:
        logger.info(f"🚀 Starting contact form submission task for {len(websites_with_messages)} websites")
        
        # Initialize form submitter and database manager
        submitter = ContactFormSubmitter()
        db_manager = DatabaseManager()
        submission_results = []
        
        total_websites = len(websites_with_messages)
        successful_submissions = 0
        failed_submissions = 0
        
        # Get file upload ID from the first website for status updates
        if websites_with_messages:
            file_upload_id = websites_with_messages[0].get('fileUploadId')
        
        for i, website in enumerate(websites_with_messages):
            try:
                # Skip if no contact form URL
                if not website.get('contactFormUrl'):
                    logger.info(f"Skipping {website.get('websiteUrl', 'Unknown')} - no contact form URL")
                    failed_submissions += 1
                    continue
                
                logger.info(f"Processing {website.get('websiteUrl', 'Unknown')} - contact form: {website.get('contactFormUrl')}")
                
                # 1. Use AI-powered intelligent form submission (primary method)
                logger.info(f"🤖 Using AI-powered intelligent form submission for {website['websiteUrl']}")
                submission_result = submitter.submit_contact_form_intelligent(
                    website_data=website,
                    generated_message=website['generatedMessage']
                )
                
                # If AI-powered submission fails, fallback to traditional method
                if not submission_result.get('success'):
                    logger.warning(f"🔄 AI submission failed, trying traditional method for {website['websiteUrl']}")
                    
                    # Fallback: Detect form structure using traditional method
                    form_data = submitter.detect_contact_form_fields(website['contactFormUrl'])
                    
                    if form_data:
                        logger.info(f"✅ Traditional form detection successful for {website['websiteUrl']}")
                        # Try traditional submission
                        traditional_result = submitter.submit_contact_form(
                    form_data=form_data,
                    generated_message=website['generatedMessage']
                )
                        
                        # Use traditional result if it's better
                        if traditional_result.get('success'):
                            submission_result = traditional_result
                            submission_result['submission_method'] = 'traditional_fallback'
                        else:
                            # Keep AI result but mark as fallback attempted
                            submission_result['fallback_attempted'] = True
                            submission_result['fallback_error'] = traditional_result.get('error', 'Unknown error')
                    else:
                        logger.error(f"❌ Both AI and traditional form detection failed for {website['websiteUrl']}")
                        submission_result['fallback_attempted'] = True
                        submission_result['fallback_error'] = "Traditional form detection also failed"
                
                # Log detailed submission result
                logger.info(f"📊 Form submission result for {website['websiteUrl']}: {submission_result}")
                
                # 3. Create contact inquiry record
                contact_inquiry_id = None
                if submission_result.get('success'):
                    try:
                        contact_inquiry_id = db_manager.create_contact_inquiry(
                            website_id=website.get('id'),
                            userId=website.get('userId'),
                            contactFormUrl=website.get('contactFormUrl'),
                            submitted_message=website.get('generatedMessage'),
                            status="SUBMITTED",
                            response_content=submission_result.get('response_page', '')
                        )
                        logger.info(f"✅ Created contact inquiry record: {contact_inquiry_id}")
                    except Exception as db_error:
                        logger.error(f"❌ Failed to create contact inquiry record: {db_error}")
                        # Mark submission as failed due to database error
                        submission_result['success'] = False
                        submission_result['error'] = f"Database error: {db_error}"
                else:
                    logger.error(f"❌ Form submission FAILED for {website['websiteUrl']}: {submission_result.get('error', 'Unknown error')}")
                
                # 4. Update website submission status
                try:
                    success = db_manager.update_website_submission(
                        website_id=website.get('id'),
                        submission_status="SUBMITTED" if submission_result.get('success') else "FAILED",
                        submission_time=submission_result.get('submission_time'),
                        response_content=submission_result.get('response_page', ''),
                        error_message=submission_result.get('error', '')
                    )
                    logger.info(f"✅ Updated website submission status for {website['websiteUrl']}")
                except Exception as update_error:
                    logger.error(f"❌ Failed to update website submission status: {update_error}")
                    # Continue processing but log the error
                
                submission_results.append({
                    'website_id': website.get('id'),
                    'url': website.get('websiteUrl'),
                    'contact_form_url': website.get('contactFormUrl'),
                    'success': submission_result['success'],
                    'submission_time': submission_result['submission_time'],
                    'error': submission_result.get('error'),
                    'contact_inquiry_id': contact_inquiry_id
                })
                
                if submission_result.get('success'):
                    successful_submissions += 1
                    logger.info(f"✅ Successfully submitted form for {website.get('websiteUrl')}")
                else:
                    failed_submissions += 1
                    logger.error(f"❌ Failed to submit form for {website.get('websiteUrl')}: {submission_result.get('error', 'Unknown error')}")
                    
                    # Update website with detailed error information
                    try:
                        db_manager.update_website_submission(
                            website_id=website.get('id'),
                            submission_status="FAILED",
                            submission_time=datetime.now(),
                            error_message=submission_result.get('error', 'Unknown error')
                        )
                    except Exception as update_error:
                        logger.error(f"Failed to update website error status: {update_error}")
                
                # 5. Update progress
                progress = int((i + 1) / total_websites * 100)
                self.update_state(
                    state='PROGRESS',
                    meta={
                        'current': i + 1,
                        'total': total_websites,
                        'progress': progress,
                        'successful_submissions': successful_submissions,
                        'failed_submissions': failed_submissions
                    }
                )
                
                # Rate limiting
                time.sleep(random.uniform(2, 5))
                
            except Exception as e:
                failed_submissions += 1
                logger.error(f"Error submitting form for {website.get('websiteUrl', 'Unknown')}: {e}")
                continue
        
        # 6. Update file upload status if we have a file upload ID
        if file_upload_id:
            try:
                if successful_submissions > 0:
                    status_update = {
                        'status': 'CONTACT_FORM_SUBMISSION_COMPLETED',
                        'contactFormsProcessed': successful_submissions
                    }
                    if failed_submissions > 0:
                        status_update['status'] = 'CONTACT_FORM_SUBMISSION_PARTIAL'
                        status_update['failedSubmissions'] = failed_submissions
                    
                    db_manager.update_file_upload(file_upload_id, status_update)
                    logger.info(f"✅ Updated file upload {file_upload_id} status to {status_update['status']}")
                    logger.info(f"📊 Final results: {successful_submissions} successful, {failed_submissions} failed")
                else:
                    db_manager.update_file_upload(file_upload_id, {
                        'status': 'CONTACT_FORM_SUBMISSION_FAILED',
                        'failedSubmissions': failed_submissions
                    })
                    logger.error(f"❌ Updated file upload {file_upload_id} status to CONTACT_FORM_SUBMISSION_FAILED")
                    logger.error(f"📊 All {failed_submissions} submissions failed")
            except Exception as e:
                logger.error(f"❌ Failed to update file upload status: {e}")
                # Try to update with a generic error status
                try:
                    db_manager.update_file_upload(file_upload_id, {
                        'status': 'CONTACT_FORM_SUBMISSION_ERROR',
                        'errorMessage': f"Status update failed: {e}"
                    })
                except Exception as final_error:
                    logger.error(f"❌ Critical: Could not update file upload status at all: {final_error}")
        
        logger.info(f"🎯 Form submission task completed. Successful: {successful_submissions}, Failed: {failed_submissions}")
        
        # Determine overall task status
        if failed_submissions == 0:
            task_status = 'success'
            logger.info(f"🎉 All {successful_submissions} form submissions completed successfully!")
        elif successful_submissions == 0:
            task_status = 'failed'
            logger.error(f"💥 All {failed_submissions} form submissions failed!")
        else:
            task_status = 'partial_success'
            logger.warning(f"⚠️ Mixed results: {successful_submissions} successful, {failed_submissions} failed")
        
        return {
            'status': task_status,
            'total_websites': total_websites,
            'successful_submissions': successful_submissions,
            'failed_submissions': failed_submissions,
            'results': submission_results,
            'task_summary': f"{successful_submissions}/{total_websites} forms submitted successfully"
        }
        
    except Exception as e:
        logger.error(f"💥 Critical error in form submission task: {e}")
        logger.error(f"Stack trace:", exc_info=True)
        
        # Try to update file upload status to show critical error
        if file_upload_id:
            try:
                db_manager.update_file_upload(file_upload_id, {
                    'status': 'CONTACT_FORM_SUBMISSION_CRITICAL_ERROR',
                    'errorMessage': f"Task crashed: {e}"
                })
            except Exception as update_error:
                logger.error(f"❌ Could not update file upload status after critical error: {update_error}")
        
        raise 