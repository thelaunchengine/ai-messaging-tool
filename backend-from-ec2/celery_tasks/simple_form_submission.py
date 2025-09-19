"""
Simple form submission using requests + BeautifulSoup instead of Selenium
This is more reliable and doesn't have browser conflicts
"""

import requests
from bs4 import BeautifulSoup
import logging
import time
import os
from typing import Dict, Any, Optional, List
from urllib.parse import urljoin, urlparse
import re

logger = logging.getLogger(__name__)

class SimpleFormSubmitter:
    """Simple form submitter using requests + BeautifulSoup"""
    
    def __init__(self):
        self.session = requests.Session()
        # Disable SSL verification to handle certificate issues
        self.session.verify = False
        # Disable SSL warnings
        import urllib3
        urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
        
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        })
        self.user_config = self._get_user_config()
    
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
        Detect contact form fields using requests + BeautifulSoup
        """
        try:
            logger.info(f"🔍 Starting simple form detection for {form_url}")
            
            # Get the page
            response = self.session.get(form_url, timeout=30)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Find all forms on the page
            forms = soup.find_all('form')
            
            if not forms:
                logger.warning(f"No forms found on {form_url}")
                return None
            
            # Use the first form (usually the main contact form)
            form = forms[0]
            
            # Extract form attributes
            form_action = form.get('action', '')
            form_method = form.get('method', 'POST').upper()
            
            # If action is relative, make it absolute
            if form_action and not form_action.startswith('http'):
                form_action = urljoin(form_url, form_action)
            
            # Find all input fields
            inputs = form.find_all(['input', 'textarea', 'select'])
            
            field_mapping = {}
            form_fields = []
            
            for input_elem in inputs:
                field_type = input_elem.get('type', 'text').lower()
                field_name = input_elem.get('name', '')
                field_id = input_elem.get('id', '')
                field_placeholder = input_elem.get('placeholder', '').lower()
                
                if not field_name:
                    continue
                
                # Map field based on name, id, or placeholder
                field_category = self._categorize_field(field_name, field_id, field_placeholder, field_type)
                
                if field_category:
                    field_mapping[field_category] = field_name
                    form_fields.append({
                        'name': field_name,
                        'type': field_type,
                        'category': field_category,
                        'required': input_elem.has_attr('required')
                    })
            
            logger.info(f"✅ Form detection successful - found {len(form_fields)} fields")
            logger.info(f"📊 Field mapping: {field_mapping}")
            
            return {
                'form_element': str(form),
                'field_mapping': field_mapping,
                'form_action': form_action,
                'form_method': form_method,
                'form_url': form_url,
                'detection_method': 'simple_requests',
                'confidence_score': 0.8,
                'submission_strategy': 'direct_post',
                'form_fields': form_fields
            }
            
        except Exception as e:
            logger.error(f"Error detecting form fields: {e}")
            return None
    
    def _categorize_field(self, name: str, field_id: str, placeholder: str, field_type: str) -> Optional[str]:
        """Categorize a form field based on its attributes"""
        
        # Combine all text for analysis
        all_text = f"{name} {field_id} {placeholder}".lower()
        
        # Name field patterns
        if any(pattern in all_text for pattern in ['name', 'fullname', 'firstname', 'lastname', 'fname', 'lname']):
            return 'name'
        
        # Email field patterns
        if any(pattern in all_text for pattern in ['email', 'e-mail', 'mail', 'address']):
            return 'email'
        
        # Phone field patterns
        if any(pattern in all_text for pattern in ['phone', 'tel', 'mobile', 'cell', 'number']):
            return 'phone'
        
        # Subject field patterns
        if any(pattern in all_text for pattern in ['subject', 'title', 'topic']):
            return 'subject'
        
        # Message field patterns
        if any(pattern in all_text for pattern in ['message', 'comment', 'inquiry', 'question', 'body', 'content']):
            return 'message'
        
        # Company field patterns
        if any(pattern in all_text for pattern in ['company', 'business', 'organization', 'org']):
            return 'company'
        
        # Website field patterns
        if any(pattern in all_text for pattern in ['website', 'url', 'site', 'web']):
            return 'website'
        
        return None
    
    def submit_contact_form(self, form_data: Dict, generated_message: str) -> Dict[str, Any]:
        """
        Submit contact form using requests
        """
        try:
            logger.info(f"📤 Submitting form to {form_data['form_url']}")
            
            # Prepare form data
            form_payload = {}
            field_mapping = form_data['field_mapping']
            
            # Fill in the fields
            if 'name' in field_mapping:
                form_payload[field_mapping['name']] = self.user_config['sender_name']
            
            if 'email' in field_mapping:
                form_payload[field_mapping['email']] = self.user_config['sender_email']
            
            if 'phone' in field_mapping:
                form_payload[field_mapping['phone']] = self.user_config['sender_phone']
            
            if 'subject' in field_mapping:
                form_payload[field_mapping['subject']] = self.user_config['message_subject']
            
            if 'message' in field_mapping:
                form_payload[field_mapping['message']] = generated_message
            
            if 'company' in field_mapping:
                form_payload[field_mapping['company']] = self.user_config['company_name']
            
            # Add any additional fields that might be required
            for field in form_data.get('form_fields', []):
                field_name = field['name']
                if field_name not in form_payload and field.get('required', False):
                    # Fill with default values for required fields
                    if field['type'] in ['text', 'email', 'tel']:
                        form_payload[field_name] = 'N/A'
                    elif field['type'] == 'textarea':
                        form_payload[field_name] = generated_message
                    elif field['type'] == 'select':
                        # Try to find the first option
                        form_payload[field_name] = '1'  # Default to first option
            
            logger.info(f"📝 Form payload: {form_payload}")
            
            # Submit the form
            submit_url = form_data['form_action'] or form_data['form_url']
            method = form_data['form_method']
            
            if method == 'POST':
                response = self.session.post(submit_url, data=form_payload, timeout=30)
            else:
                response = self.session.get(submit_url, params=form_payload, timeout=30)
            
            # Check response
            response.raise_for_status()
            
            # Check for success indicators
            success_indicators = [
                'thank you', 'success', 'message sent', 'form submitted',
                'we\'ll be in touch', 'contact received', 'submitted successfully'
            ]
            
            page_text = response.text.lower()
            success = any(indicator in page_text for indicator in success_indicators)
            
            # Also check status code
            if response.status_code in [200, 201, 302]:
                success = True
            
            logger.info(f"✅ Form submission {'successful' if success else 'completed'}")
            
            return {
                'success': success,
                'message': 'Form submitted successfully' if success else 'Form submitted but success unclear',
                'status_code': response.status_code,
                'response_url': response.url,
                'submission_time': time.time()
            }
            
        except Exception as e:
            logger.error(f"Error submitting form: {e}")
            return {
                'success': False,
                'message': f'Error submitting form: {str(e)}',
                'status_code': 0,
                'response_url': '',
                'submission_time': time.time()
            }
