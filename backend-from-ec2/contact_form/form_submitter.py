#!/usr/bin/env python3
"""
Contact Form Submission Engine
Fills and submits contact forms using AI-generated messages
"""

import logging
import time
import random
from typing import Dict, List, Optional, Any, Tuple
import requests
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import TimeoutException, WebDriverException, NoSuchElementException
from urllib.parse import urljoin, urlparse
import json

logger = logging.getLogger(__name__)

class ContactFormSubmitter:
    """Submits contact forms with AI-generated messages"""
    
    def __init__(self):
        self.session = self._create_session()
        self.chrome_options = self._setup_chrome_options()
        self.sender_config = self._get_default_sender_config()
        
    def _create_session(self):
        """Create HTTP session with headers"""
        session = requests.Session()
        session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        })
        return session
    
    def _setup_chrome_options(self):
        """Setup Chrome options for Selenium"""
        options = Options()
        options.add_argument('--headless')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--disable-gpu')
        options.add_argument('--window-size=1920,1080')
        options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36')
        options.add_argument('--disable-blink-features=AutomationControlled')
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option('useAutomationExtension', False)
        return options
    
    def _get_default_sender_config(self) -> Dict[str, str]:
        """Get default sender configuration"""
        return {
            'name': 'John Doe',
            'email': 'john.doe@company.com',
            'phone': '+1-555-123-4567',
            'company': 'Your Company Name',
            'subject': 'Business Inquiry',
            'website': 'https://yourcompany.com'
        }
    
    def submit_contact_form(self, website_data: Dict[str, Any], ai_message: str, message_type: str = "general") -> Dict[str, Any]:
        """
        Submit a contact form with AI-generated message
        
        Args:
            website_data: Website information including contact form details
            ai_message: AI-generated message to submit
            message_type: Type of message (general, partnership, inquiry, custom)
            
        Returns:
            Dictionary with submission result
        """
        try:
            website_url = website_data.get('websiteUrl', '')
            contact_form_url = website_data.get('contactFormUrl', '')
            company_name = website_data.get('companyName', 'Unknown Company')
            
            logger.info(f"🚀 Starting contact form submission for {company_name}")
            logger.info(f"🌐 Website: {website_url}")
            logger.info(f"📝 Contact Form: {contact_form_url}")
            
            if not contact_form_url:
                return {
                    'success': False,
                    'error': 'No contact form URL found',
                    'website': company_name,
                    'submission_method': 'none'
                }
            
            # Try HTTP POST first (faster)
            http_result = self._submit_via_http(contact_form_url, ai_message, message_type)
            
            if http_result['success']:
                logger.info(f"✅ HTTP submission successful for {company_name}")
                return http_result
            
            # Fallback to Selenium if HTTP fails
            logger.info(f"🔄 HTTP submission failed, trying Selenium for {company_name}")
            selenium_result = self._submit_via_selenium(contact_form_url, ai_message, message_type)
            
            if selenium_result['success']:
                logger.info(f"✅ Selenium submission successful for {company_name}")
                return selenium_result
            
            # Both methods failed
            logger.error(f"❌ Both HTTP and Selenium submission failed for {company_name}")
            return {
                'success': False,
                'error': f"HTTP: {http_result.get('error', 'Unknown')}, Selenium: {selenium_result.get('error', 'Unknown')}",
                'website': company_name,
                'submission_method': 'both_failed',
                'http_result': http_result,
                'selenium_result': selenium_result
            }
            
        except Exception as e:
            logger.error(f"❌ Error submitting contact form for {website_data.get('companyName', 'Unknown')}: {e}")
            return {
                'success': False,
                'error': str(e),
                'website': website_data.get('companyName', 'Unknown'),
                'submission_method': 'error'
            }
    
    def _submit_via_http(self, form_url: str, ai_message: str, message_type: str) -> Dict[str, Any]:
        """Submit contact form via HTTP POST"""
        try:
            # Prepare form data
            form_data = self._prepare_form_data(ai_message, message_type)
            
            # Add random delay to avoid detection
            time.sleep(random.uniform(1, 3))
            
            # Submit form
            response = self.session.post(
                form_url,
                data=form_data,
                timeout=30,
                allow_redirects=True
            )
            
            # Check response
            if response.status_code == 200:
                # Check if submission was successful (basic check)
                if self._check_submission_success(response.text):
                    return {
                        'success': True,
                        'submission_method': 'http_post',
                        'response_code': response.status_code,
                        'response_url': response.url,
                        'message': 'Form submitted successfully via HTTP POST'
                    }
                else:
                    return {
                        'success': False,
                        'error': 'Form submission may have failed (success indicator not found)',
                        'submission_method': 'http_post',
                        'response_code': response.status_code,
                        'response_url': response.url
                    }
            else:
                return {
                    'success': False,
                    'error': f'HTTP {response.status_code}: {response.reason}',
                    'submission_method': 'http_post',
                    'response_code': response.status_code
                }
                
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'submission_method': 'http_post'
            }
    
    def _submit_via_selenium(self, form_url: str, ai_message: str, message_type: str) -> Dict[str, Any]:
        """Submit contact form via Selenium browser automation"""
        driver = None
        try:
            driver = webdriver.Chrome(options=self.chrome_options)
            driver.set_page_load_timeout(30)
            
            # Navigate to form
            logger.info(f"🌐 Navigating to: {form_url}")
            driver.get(form_url)
            
            # Wait for page to load
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.TAG_NAME, "body"))
            )
            
            # Find and fill form fields
            form_filled = self._fill_form_fields(driver, ai_message, message_type)
            
            if not form_filled:
                return {
                    'success': False,
                    'error': 'Could not fill form fields',
                    'submission_method': 'selenium'
                }
            
            # Submit form
            submission_success = self._submit_form(driver)
            
            if submission_success:
                # Wait for submission response
                time.sleep(3)
                
                # Check if submission was successful
                if self._check_selenium_submission_success(driver):
                    return {
                        'success': True,
                        'submission_method': 'selenium',
                        'final_url': driver.current_url,
                        'message': 'Form submitted successfully via Selenium'
                    }
                else:
                    return {
                        'success': False,
                        'error': 'Form submission may have failed (success indicator not found)',
                        'submission_method': 'selenium',
                        'final_url': driver.current_url
                    }
            else:
                return {
                    'success': False,
                    'error': 'Could not submit form',
                    'submission_method': 'selenium'
                }
                
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'submission_method': 'selenium'
            }
        finally:
            if driver:
                driver.quit()
    
    def _prepare_form_data(self, ai_message: str, message_type: str) -> Dict[str, str]:
        """Prepare form data for HTTP submission"""
        form_data = {}
        
        # Map common field names to values
        field_mappings = {
            'name': self.sender_config['name'],
            'first_name': self.sender_config['name'].split()[0],
            'last_name': ' '.join(self.sender_config['name'].split()[1:]) if len(self.sender_config['name'].split()) > 1 else '',
            'full_name': self.sender_config['name'],
            'email': self.sender_config['email'],
            'e-mail': self.sender_config['email'],
            'mail': self.sender_config['email'],
            'phone': self.sender_config['phone'],
            'telephone': self.sender_config['phone'],
            'tel': self.sender_config['phone'],
            'mobile': self.sender_config['phone'],
            'company': self.sender_config['company'],
            'organization': self.sender_config['company'],
            'org': self.sender_config['company'],
            'business': self.sender_config['company'],
            'subject': self.sender_config['subject'],
            'topic': self.sender_config['subject'],
            'reason': self.sender_config['subject'],
            'message': ai_message,
            'comment': ai_message,
            'inquiry': ai_message,
            'description': ai_message,
            'content': ai_message,
            'text': ai_message
        }
        
        # Add common variations
        for field_name, value in field_mappings.items():
            # Add variations with underscores, hyphens, and camelCase
            variations = [
                field_name,
                field_name.replace('_', ''),
                field_name.replace('_', '-'),
                field_name.replace('_', ' '),
                field_name.title().replace(' ', ''),
                field_name.upper()
            ]
            
            for variation in variations:
                if variation:
                    form_data[variation] = value
        
        # Add some common hidden fields
        form_data['source'] = 'website'
        form_data['utm_source'] = 'organic'
        form_data['utm_medium'] = 'contact_form'
        
        return form_data
    
    def _fill_form_fields(self, driver, ai_message: str, message_type: str) -> bool:
        """Fill form fields using Selenium"""
        try:
            # Prepare field values
            field_values = {
                'name': self.sender_config['name'],
                'email': self.sender_config['email'],
                'phone': self.sender_config['phone'],
                'company': self.sender_config['company'],
                'subject': self.sender_config['subject'],
                'message': ai_message
            }
            
            # Find and fill input fields
            inputs = driver.find_elements(By.TAG_NAME, "input")
            textareas = driver.find_elements(By.TAG_NAME, "textarea")
            selects = driver.find_elements(By.TAG_NAME, "select")
            
            fields_filled = 0
            
            # Fill input fields
            for input_field in inputs:
                if self._fill_input_field(input_field, field_values):
                    fields_filled += 1
            
            # Fill textarea fields
            for textarea in textareas:
                if self._fill_textarea_field(textarea, field_values):
                    fields_filled += 1
            
            # Fill select fields
            for select in selects:
                if self._fill_select_field(select, field_values):
                    fields_filled += 1
            
            logger.info(f"✅ Filled {fields_filled} form fields")
            return fields_filled > 0
            
        except Exception as e:
            logger.error(f"Error filling form fields: {e}")
            return False
    
    def _fill_input_field(self, input_field, field_values: Dict[str, str]) -> bool:
        """Fill a single input field"""
        try:
            field_type = input_field.get_attribute('type') or 'text'
            field_name = input_field.get_attribute('name') or ''
            field_id = input_field.get_attribute('id') or ''
            field_placeholder = input_field.get_attribute('placeholder') or ''
            
            # Skip non-fillable fields
            if field_type in ['submit', 'button', 'reset', 'hidden', 'file', 'image']:
                return False
            
            # Determine field category
            field_category = self._categorize_field_name(field_name, field_id, field_placeholder)
            
            if field_category and field_category in field_values:
                # Clear field first
                input_field.clear()
                
                # Add random delay to simulate human typing
                time.sleep(random.uniform(0.1, 0.3))
                
                # Fill field
                input_field.send_keys(field_values[field_category])
                
                logger.info(f"✅ Filled {field_category} field: {field_values[field_category]}")
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Error filling input field: {e}")
            return False
    
    def _fill_textarea_field(self, textarea, field_values: Dict[str, str]) -> bool:
        """Fill a textarea field"""
        try:
            field_name = textarea.get_attribute('name') or ''
            field_id = textarea.get_attribute('id') or ''
            field_placeholder = textarea.get_attribute('placeholder') or ''
            
            # Determine field category
            field_category = self._categorize_field_name(field_name, field_id, field_placeholder)
            
            if field_category and field_category in field_values:
                # Clear field first
                textarea.clear()
                
                # Add random delay
                time.sleep(random.uniform(0.1, 0.3))
                
                # Fill field
                textarea.send_keys(field_values[field_category])
                
                logger.info(f"✅ Filled {field_category} textarea: {field_values[field_category][:50]}...")
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Error filling textarea field: {e}")
            return False
    
    def _fill_select_field(self, select, field_values: Dict[str, str]) -> bool:
        """Fill a select field"""
        try:
            field_name = select.get_attribute('name') or ''
            field_id = select.get_attribute('id') or ''
            
            # Determine field category
            field_category = self._categorize_field_name(field_name, field_id, '')
            
            if field_category and field_category in field_values:
                # Find options
                options = select.find_elements(By.TAG_NAME, "option")
                
                if options:
                    # Select first non-empty option
                    for option in options:
                        option_value = option.get_attribute('value') or ''
                        if option_value and option_value.strip():
                            option.click()
                            logger.info(f"✅ Selected option for {field_category}: {option_value}")
                            return True
            
            return False
            
        except Exception as e:
            logger.error(f"Error filling select field: {e}")
            return False
    
    def _categorize_field_name(self, name: str, field_id: str, placeholder: str) -> Optional[str]:
        """Categorize a field name to determine what to fill it with"""
        all_text = f"{name} {field_id} {placeholder}".lower()
        
        # Name fields
        if any(n in all_text for n in ['name', 'first', 'last', 'full']):
            return 'name'
        
        # Email fields
        if any(e in all_text for e in ['email', 'e-mail', 'mail']):
            return 'email'
        
        # Phone fields
        if any(p in all_text for p in ['phone', 'tel', 'telephone', 'mobile']):
            return 'phone'
        
        # Company fields
        if any(c in all_text for c in ['company', 'organization', 'org', 'business']):
            return 'company'
        
        # Subject fields
        if any(s in all_text for s in ['subject', 'topic', 'reason']):
            return 'subject'
        
        # Message fields
        if any(m in all_text for m in ['message', 'comment', 'inquiry', 'description', 'content']):
            return 'message'
        
        return None
    
    def _submit_form(self, driver) -> bool:
        """Submit the filled form"""
        try:
            # Look for submit button
            submit_selectors = [
                "input[type='submit']",
                "button[type='submit']",
                "button:contains('Submit')",
                "button:contains('Send')",
                "button:contains('Submit Message')",
                "input[value*='Submit']",
                "input[value*='Send']"
            ]
            
            for selector in submit_selectors:
                try:
                    submit_button = driver.find_element(By.CSS_SELECTOR, selector)
                    if submit_button.is_displayed() and submit_button.is_enabled():
                        # Add random delay before clicking
                        time.sleep(random.uniform(0.5, 1.5))
                        
                        # Click submit button
                        submit_button.click()
                        logger.info("✅ Form submitted via submit button")
                        return True
                except NoSuchElementException:
                    continue
            
            # Try pressing Enter in the last filled field
            try:
                last_field = driver.find_element(By.CSS_SELECTOR, "input, textarea")
                last_field.send_keys(Keys.RETURN)
                logger.info("✅ Form submitted via Enter key")
                return True
            except:
                pass
            
            logger.warning("⚠️ Could not find submit button")
            return False
            
        except Exception as e:
            logger.error(f"Error submitting form: {e}")
            return False
    
    def _check_submission_success(self, response_text: str) -> bool:
        """Check if HTTP submission was successful"""
        success_indicators = [
            'thank you',
            'success',
            'submitted',
            'received',
            'confirmation',
            'thank you for your message',
            'we have received your message',
            'message sent successfully'
        ]
        
        response_lower = response_text.lower()
        return any(indicator in response_lower for indicator in success_indicators)
    
    def _check_selenium_submission_success(self, driver) -> bool:
        """Check if Selenium submission was successful"""
        try:
            page_source = driver.page_source.lower()
            return self._check_submission_success(page_source)
        except:
            return False
    
    def update_sender_config(self, new_config: Dict[str, str]):
        """Update sender configuration"""
        self.sender_config.update(new_config)
        logger.info(f"✅ Updated sender config: {new_config}")
    
    def get_sender_config(self) -> Dict[str, str]:
        """Get current sender configuration"""
        return self.sender_config.copy()
