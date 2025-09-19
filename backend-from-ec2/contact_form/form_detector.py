#!/usr/bin/env python3
"""
Contact Form Detection and Analysis Engine
Detects contact forms on websites and maps their fields
"""

import logging
import re
from typing import Dict, List, Optional, Any
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import requests
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException, WebDriverException

logger = logging.getLogger(__name__)

class ContactFormDetector:
    """Detects and analyzes contact forms on websites"""
    
    def __init__(self):
        self.session = self._create_session()
        self.chrome_options = self._setup_chrome_options()
        
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
        return options
    
    def detect_contact_forms(self, url: str) -> Dict[str, Any]:
        """
        Detect contact forms on a website using multiple methods
        
        Args:
            url: Website URL to analyze
            
        Returns:
            Dictionary with form detection results
        """
        try:
            logger.info(f"🔍 Detecting contact forms on: {url}")
            
            # Method 1: Static HTML analysis
            static_result = self._detect_static_forms(url)
            
            # Method 2: Selenium dynamic analysis (if static fails)
            dynamic_result = None
            if not static_result['forms_found']:
                dynamic_result = self._detect_dynamic_forms(url)
            
            # Combine results
            result = {
                'url': url,
                'forms_found': static_result['forms_found'] or (dynamic_result and dynamic_result['forms_found']),
                'contact_form_url': static_result.get('contact_form_url') or dynamic_result.get('contact_form_url'),
                'has_contact_form': static_result['forms_found'] or (dynamic_result and dynamic_result['forms_found']),
                'detection_method': 'static' if static_result['forms_found'] else 'dynamic' if dynamic_result and dynamic_result['forms_found'] else 'none',
                'static_analysis': static_result,
                'dynamic_analysis': dynamic_result,
                'detection_timestamp': str(datetime.now())
            }
            
            logger.info(f"✅ Form detection completed for {url}: {result['forms_found']} forms found")
            return result
            
        except Exception as e:
            logger.error(f"❌ Error detecting contact forms on {url}: {e}")
            return {
                'url': url,
                'forms_found': False,
                'has_contact_form': False,
                'error': str(e),
                'detection_timestamp': str(datetime.now())
            }
    
    def _detect_static_forms(self, url: str) -> Dict[str, Any]:
        """Detect contact forms using static HTML analysis"""
        try:
            response = self.session.get(url, timeout=30)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Look for contact forms
            forms = soup.find_all('form')
            contact_forms = []
            
            for form in forms:
                if self._is_contact_form(form):
                    form_info = self._analyze_form_structure(form, url)
                    contact_forms.append(form_info)
            
            # Look for contact form URLs
            contact_urls = self._find_contact_urls(soup, url)
            
            result = {
                'forms_found': len(contact_forms) > 0 or len(contact_urls) > 0,
                'contact_forms': contact_forms,
                'contact_urls': contact_urls,
                'contact_form_url': contact_urls[0] if contact_urls else None,
                'total_forms': len(forms),
                'contact_forms_count': len(contact_forms)
            }
            
            return result
            
        except Exception as e:
            logger.error(f"Error in static form detection: {e}")
            return {'forms_found': False, 'error': str(e)}
    
    def _is_contact_form(self, form) -> bool:
        """Determine if a form is a contact form"""
        # Check form attributes
        form_text = form.get_text().lower()
        form_action = form.get('action', '').lower()
        form_class = form.get('class', [])
        form_id = form.get('id', '').lower()
        
        # Contact form indicators
        contact_indicators = [
            'contact', 'inquiry', 'message', 'support', 'help',
            'get in touch', 'reach out', 'contact us', 'send message'
        ]
        
        # Check if any contact indicators are present
        for indicator in contact_indicators:
            if (indicator in form_text or 
                indicator in form_action or 
                indicator in form_id or
                any(indicator in cls.lower() for cls in form_class)):
                return True
        
        # Check for contact-related input fields
        inputs = form.find_all('input')
        contact_fields = ['name', 'email', 'phone', 'message', 'subject']
        
        contact_field_count = 0
        for input_field in inputs:
            field_type = input_field.get('type', '').lower()
            field_name = input_field.get('name', '').lower()
            field_placeholder = input_field.get('placeholder', '').lower()
            
            for contact_field in contact_fields:
                if (contact_field in field_name or 
                    contact_field in field_placeholder or
                    (field_type == 'text' and contact_field in field_name)):
                    contact_field_count += 1
        
        # If we have at least 2 contact-related fields, it's likely a contact form
        return contact_field_count >= 2
    
    def _analyze_form_structure(self, form, base_url: str) -> Dict[str, Any]:
        """Analyze the structure of a contact form"""
        inputs = form.find_all('input')
        textareas = form.find_all('textarea')
        selects = form.find_all('select')
        
        form_fields = []
        
        # Analyze input fields
        for input_field in inputs:
            field_info = {
                'type': 'input',
                'input_type': input_field.get('type', 'text'),
                'name': input_field.get('name', ''),
                'id': input_field.get('id', ''),
                'placeholder': input_field.get('placeholder', ''),
                'required': input_field.get('required') is not None,
                'value': input_field.get('value', ''),
                'field_category': self._categorize_field(input_field)
            }
            form_fields.append(field_info)
        
        # Analyze textarea fields
        for textarea in textareas:
            field_info = {
                'type': 'textarea',
                'name': textarea.get('name', ''),
                'id': textarea.get('id', ''),
                'placeholder': textarea.get('placeholder', ''),
                'required': textarea.get('required') is not None,
                'rows': textarea.get('rows', ''),
                'cols': textarea.get('cols', ''),
                'field_category': self._categorize_field(textarea)
            }
            form_fields.append(field_info)
        
        # Analyze select fields
        for select in selects:
            options = []
            for option in select.find_all('option'):
                options.append({
                    'value': option.get('value', ''),
                    'text': option.get_text().strip()
                })
            
            field_info = {
                'type': 'select',
                'name': select.get('name', ''),
                'id': select.get('id', ''),
                'required': select.get('required') is not None,
                'options': options,
                'field_category': self._categorize_field(select)
            }
            form_fields.append(field_info)
        
        return {
            'action': form.get('action', ''),
            'method': form.get('method', 'get').upper(),
            'enctype': form.get('enctype', ''),
            'fields': form_fields,
            'submit_button': self._find_submit_button(form),
            'form_url': urljoin(base_url, form.get('action', ''))
        }
    
    def _categorize_field(self, field) -> str:
        """Categorize a form field based on its purpose"""
        field_name = field.get('name', '').lower()
        field_placeholder = field.get('placeholder', '').lower()
        field_id = field.get('id', '').lower()
        
        # Name fields
        if any(name in field_name for name in ['name', 'first', 'last', 'full']):
            return 'name'
        
        # Email fields
        if any(name in field_name for name in ['email', 'e-mail', 'mail']):
            return 'email'
        
        # Phone fields
        if any(name in field_name for name in ['phone', 'tel', 'telephone', 'mobile']):
            return 'phone'
        
        # Company fields
        if any(name in field_name for name in ['company', 'organization', 'org', 'business']):
            return 'company'
        
        # Subject fields
        if any(name in field_name for name in ['subject', 'topic', 'reason']):
            return 'subject'
        
        # Message fields
        if any(name in field_name for name in ['message', 'comment', 'inquiry', 'description']):
            return 'message'
        
        # Check placeholders and IDs
        all_text = f"{field_name} {field_placeholder} {field_id}".lower()
        
        if 'name' in all_text:
            return 'name'
        elif 'email' in all_text:
            return 'email'
        elif 'phone' in all_text:
            return 'phone'
        elif 'company' in all_text:
            return 'company'
        elif 'subject' in all_text:
            return 'subject'
        elif 'message' in all_text:
            return 'message'
        
        return 'unknown'
    
    def _find_submit_button(self, form) -> Dict[str, Any]:
        """Find the submit button in a form"""
        submit_button = form.find('input', {'type': 'submit'})
        if submit_button:
            return {
                'type': 'input',
                'value': submit_button.get('value', 'Submit'),
                'name': submit_button.get('name', ''),
                'id': submit_button.get('id', '')
            }
        
        button = form.find('button', {'type': 'submit'})
        if button:
            return {
                'type': 'button',
                'text': button.get_text().strip(),
                'name': button.get('name', ''),
                'id': button.get('id', '')
            }
        
        return None
    
    def _find_contact_urls(self, soup, base_url: str) -> List[str]:
        """Find contact-related URLs on the page"""
        contact_urls = []
        
        # Look for contact links
        links = soup.find_all('a', href=True)
        
        for link in links:
            link_text = link.get_text().lower().strip()
            link_href = link.get('href', '').lower()
            
            # Contact-related link patterns
            contact_patterns = [
                'contact', 'contact us', 'get in touch', 'reach out',
                'support', 'help', 'inquiry', 'message us'
            ]
            
            for pattern in contact_patterns:
                if pattern in link_text or pattern in link_href:
                    full_url = urljoin(base_url, link.get('href'))
                    if full_url not in contact_urls:
                        contact_urls.append(full_url)
        
        return contact_urls
    
    def _detect_dynamic_forms(self, url: str) -> Dict[str, Any]:
        """Detect contact forms using Selenium for dynamic content"""
        try:
            driver = webdriver.Chrome(options=self.chrome_options)
            driver.set_page_load_timeout(30)
            
            try:
                driver.get(url)
                
                # Wait for page to load
                WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.TAG_NAME, "body"))
                )
                
                # Look for forms
                forms = driver.find_elements(By.TAG_NAME, "form")
                contact_forms = []
                
                for form in forms:
                    if self._is_selenium_contact_form(form):
                        form_info = self._analyze_selenium_form(form, url)
                        contact_forms.append(form_info)
                
                # Look for contact URLs
                contact_urls = self._find_selenium_contact_urls(driver, url)
                
                result = {
                    'forms_found': len(contact_forms) > 0 or len(contact_urls) > 0,
                    'contact_forms': contact_forms,
                    'contact_urls': contact_urls,
                    'contact_form_url': contact_urls[0] if contact_urls else None,
                    'total_forms': len(forms),
                    'contact_forms_count': len(contact_forms)
                }
                
                return result
                
            finally:
                driver.quit()
                
        except Exception as e:
            logger.error(f"Error in dynamic form detection: {e}")
            return {'forms_found': False, 'error': str(e)}
    
    def _is_selenium_contact_form(self, form) -> bool:
        """Determine if a Selenium form element is a contact form"""
        try:
            form_text = form.text.lower()
            
            # Contact form indicators
            contact_indicators = [
                'contact', 'inquiry', 'message', 'support', 'help',
                'get in touch', 'reach out', 'contact us', 'send message'
            ]
            
            for indicator in contact_indicators:
                if indicator in form_text:
                    return True
            
            return False
            
        except Exception:
            return False
    
    def _analyze_selenium_form(self, form, base_url: str) -> Dict[str, Any]:
        """Analyze a Selenium form element"""
        try:
            # Get form attributes
            action = form.get_attribute('action') or ''
            method = form.get_attribute('method') or 'get'
            
            # Find form fields
            inputs = form.find_elements(By.TAG_NAME, "input")
            textareas = form.find_elements(By.TAG_NAME, "textarea")
            selects = form.find_elements(By.TAG_NAME, "select")
            
            form_fields = []
            
            # Analyze input fields
            for input_field in inputs:
                field_info = {
                    'type': 'input',
                    'input_type': input_field.get_attribute('type') or 'text',
                    'name': input_field.get_attribute('name') or '',
                    'id': input_field.get_attribute('id') or '',
                    'placeholder': input_field.get_attribute('placeholder') or '',
                    'required': input_field.get_attribute('required') is not None,
                    'value': input_field.get_attribute('value') or '',
                    'field_category': 'unknown'  # Simplified for Selenium
                }
                form_fields.append(field_info)
            
            # Analyze textarea fields
            for textarea in textareas:
                field_info = {
                    'type': 'textarea',
                    'name': textarea.get_attribute('name') or '',
                    'id': textarea.get_attribute('id') or '',
                    'placeholder': textarea.get_attribute('placeholder') or '',
                    'required': textarea.get_attribute('required') is not None,
                    'rows': textarea.get_attribute('rows') or '',
                    'cols': textarea.get_attribute('cols') or '',
                    'field_category': 'message'  # Assume textarea is for message
                }
                form_fields.append(field_info)
            
            return {
                'action': action,
                'method': method.upper(),
                'fields': form_fields,
                'form_url': urljoin(base_url, action)
            }
            
        except Exception as e:
            logger.error(f"Error analyzing Selenium form: {e}")
            return {'error': str(e)}
    
    def _find_selenium_contact_urls(self, driver, base_url: str) -> List[str]:
        """Find contact URLs using Selenium"""
        try:
            contact_urls = []
            links = driver.find_elements(By.TAG_NAME, "a")
            
            for link in links:
                try:
                    link_text = link.text.lower().strip()
                    link_href = link.get_attribute('href') or ''
                    
                    # Contact-related link patterns
                    contact_patterns = [
                        'contact', 'contact us', 'get in touch', 'reach out',
                        'support', 'help', 'inquiry', 'message us'
                    ]
                    
                    for pattern in contact_patterns:
                        if pattern in link_text or pattern in link_href.lower():
                            if link_href not in contact_urls:
                                contact_urls.append(link_href)
                            break
                            
                except Exception:
                    continue
            
            return contact_urls
            
        except Exception as e:
            logger.error(f"Error finding Selenium contact URLs: {e}")
            return []

# Import datetime at the top
from datetime import datetime
