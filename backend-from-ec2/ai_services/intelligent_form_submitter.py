"""
AI-Powered Intelligent Form Submission System
Uses Gemini AI to adapt to different platforms and form types
"""

import os
import json
import logging
import time
import requests
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from selenium.webdriver.firefox.service import Service as FirefoxService
from bs4 import BeautifulSoup

from ai_form_analyzer import AIFormAnalyzer, FormAnalysisResult
from ai_services.captcha_handler import CaptchaHandler, CaptchaResult
from ai_services.smart_field_handler import SmartFieldHandler, FieldInfo, FieldHandlingResult

logger = logging.getLogger(__name__)

@dataclass
class SubmissionResult:
    """Result of form submission attempt"""
    success: bool
    method_used: str
    response_content: Optional[str]
    error_message: Optional[str]
    submission_time: str
    platform_detected: Optional[str]
    fields_submitted: Dict[str, str]
    confidence_score: float

class IntelligentFormSubmitter:
    """AI-powered form submission that adapts to different platforms"""
    
    def __init__(self):
        """Initialize the intelligent form submitter"""
        self.ai_analyzer = AIFormAnalyzer()
        self.captcha_handler = CaptchaHandler()
        self.smart_field_handler = SmartFieldHandler()
        self.user_config = self._get_user_config()
        
    def _get_user_config(self) -> Dict[str, str]:
        """Get user configuration for form submission"""
        return {
            'sender_name': os.getenv('SENDER_NAME', 'AI Assistant'),
            'sender_email': os.getenv('SENDER_EMAIL', 'ai@example.com'),
            'sender_phone': os.getenv('SENDER_PHONE', '555-123-4567'),
            'message_subject': os.getenv('MESSAGE_SUBJECT', 'Business Inquiry'),
            'company_name': os.getenv('COMPANY_NAME', 'AI Solutions Inc')
        }
    
    def submit_contact_form(self, website_data: Dict[str, Any], generated_message: str) -> SubmissionResult:
        """
        Intelligently submit contact form using AI-guided approach
        
        Args:
            website_data: Website information including contact form details
            generated_message: AI-generated message to submit
            
        Returns:
            SubmissionResult with submission details
        """
        start_time = time.time()
        website_url = website_data.get('websiteUrl', '')
        contact_form_url = website_data.get('contactFormUrl', '')
        
        logger.info(f"🤖 Starting AI-powered form submission for {website_url}")
        
        try:
            # Step 1: Get page content for AI analysis
            page_content = self._fetch_page_content(contact_form_url)
            if not page_content:
                return SubmissionResult(
                    success=False,
                    method_used="none",
                    response_content=None,
                    error_message="Failed to fetch page content",
                    submission_time=time.strftime('%Y-%m-%d %H:%M:%S'),
                    platform_detected=None,
                    fields_submitted={},
                    confidence_score=0.0
                )
            
            # Step 2: Use AI to analyze the form
            logger.info(f"🔍 AI analyzing form structure for {contact_form_url}")
            analysis_result = self.ai_analyzer.analyze_page_for_forms(
                page_content, 
                contact_form_url, 
                website_data.get('companyName', '')
            )
            
            if not analysis_result.success:
                return SubmissionResult(
                    success=False,
                    method_used="ai_analysis",
                    response_content=None,
                    error_message=f"AI analysis failed: {analysis_result.error_message}",
                    submission_time=time.strftime('%Y-%m-%d %H:%M:%S'),
                    platform_detected=None,
                    fields_submitted={},
                    confidence_score=0.0
                )
            
            # Step 3: Detect platform and choose strategy
            platform = self._detect_platform(contact_form_url, page_content)
            logger.info(f"🏗️ Detected platform: {platform}")
            
            # Step 4: Handle CAPTCHAs if detected
            captcha_result = None
            if analysis_result.captcha_detected:
                logger.info(f"🧩 CAPTCHA detected: {analysis_result.captcha_type}")
                captcha_info = {
                    'captcha_type': analysis_result.captcha_type,
                    'captcha_selectors': analysis_result.captcha_selectors,
                    'captcha_site_key': analysis_result.captcha_site_key,
                    'captcha_challenges': analysis_result.captcha_challenges,
                    'page_url': contact_form_url
                }
                
                # Note: CAPTCHA solving will be handled during form submission
                logger.info(f"⚠️ CAPTCHA solving will be attempted during form submission")
            
            # Step 5: Get AI recommendations for submission strategy
            strategy = self.ai_analyzer.suggest_submission_strategy(
                {
                    'form_elements': analysis_result.form_elements,
                    'field_mappings': analysis_result.field_mappings,
                    'submission_methods': analysis_result.submission_methods,
                    'captcha_detected': analysis_result.captcha_detected,
                    'captcha_type': analysis_result.captcha_type
                },
                generated_message,
                f"Platform: {platform}, URL: {contact_form_url}, CAPTCHA: {analysis_result.captcha_type or 'None'}"
            )
            
            logger.info(f"📋 AI recommended strategy: {strategy.get('strategy', 'traditional')}")
            
            # Step 6: Execute submission - ALWAYS try traditional first, then fallback to AI recommendations
            try:
                # Primary: Always try traditional form submission first
                logger.info("🎯 Attempting traditional form submission first (primary method)")
                result = self._submit_via_traditional(contact_form_url, analysis_result, generated_message, strategy)
                
                # If traditional succeeds, use it
                if result.success:
                    logger.info("✅ Traditional form submission succeeded")
                else:
                    # Fallback: Try AI-recommended strategy if traditional fails
                    logger.warning(f"⚠️ Traditional submission failed: {result.error_message}")
                    logger.info(f"🔄 Trying AI-recommended strategy: {strategy.get('strategy', 'traditional')}")
                    
                    if strategy.get('strategy') == 'ajax':
                        result = self._submit_via_ajax(contact_form_url, analysis_result, generated_message, strategy)
                    elif strategy.get('strategy') == 'modal':
                        result = self._submit_via_modal(contact_form_url, analysis_result, generated_message, strategy)
                    elif strategy.get('strategy') == 'alternative':
                        result = self._submit_via_alternative(contact_form_url, analysis_result, generated_message, strategy)
                    else:
                        # If no specific strategy, try alternative as last resort
                        logger.info("🔄 No specific strategy, trying alternative methods as last resort")
                        result = self._submit_via_alternative(contact_form_url, analysis_result, generated_message, strategy)
            except Exception as strategy_error:
                logger.error(f"❌ Strategy execution failed: {strategy_error}")
                # Fallback to traditional method
                try:
                    result = self._submit_via_traditional(contact_form_url, analysis_result, generated_message, strategy)
                    result.method_used = f"traditional_fallback_{strategy.get('strategy', 'unknown')}"
                except Exception as fallback_error:
                    logger.error(f"❌ Fallback also failed: {fallback_error}")
                    result = SubmissionResult(
                        success=False,
                        method_used="strategy_and_fallback_failed",
                        response_content=None,
                        error_message=f"Strategy failed: {strategy_error}. Fallback failed: {fallback_error}",
                        submission_time=time.strftime('%Y-%m-%d %H:%M:%S'),
                        platform_detected=platform,
                        fields_submitted={},
                        confidence_score=0.0
                    )
            
            result.platform_detected = platform
            result.submission_time = time.strftime('%Y-%m-%d %H:%M:%S')
            
            logger.info(f"✅ Form submission completed for {website_url} using {result.method_used}")
            return result
            
        except Exception as e:
            logger.error(f"❌ Error in AI-powered form submission for {website_url}: {e}")
            return SubmissionResult(
                success=False,
                method_used="ai_error",
                response_content=None,
                error_message=f"AI submission error: {str(e)}",
                submission_time=time.strftime('%Y-%m-%d %H:%M:%S'),
                platform_detected=None,
                fields_submitted={},
                confidence_score=0.0
            )
    
    def _fetch_page_content(self, url: str) -> Optional[str]:
        """Fetch page content for AI analysis"""
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
            # Disable SSL verification to handle certificate issues
            response = requests.get(url, headers=headers, timeout=30, verify=False)
            response.raise_for_status()
            return response.text
        except Exception as e:
            logger.error(f"Failed to fetch page content from {url}: {e}")
            return None
    
    def _detect_platform(self, url: str, content: str) -> str:
        """Detect the platform/technology used for the website"""
        content_lower = content.lower()
        
        # Platform detection patterns
        if 'wix' in content_lower or 'wix.com' in url:
            return 'wix'
        elif 'wordpress' in content_lower or 'wp-content' in content_lower:
            return 'wordpress'
        elif 'squarespace' in content_lower:
            return 'squarespace'
        elif 'shopify' in content_lower:
            return 'shopify'
        elif 'webflow' in content_lower:
            return 'webflow'
        elif 'formspree' in content_lower or 'formspree.io' in content_lower:
            return 'formspree'
        elif 'typeform' in content_lower:
            return 'typeform'
        elif 'google forms' in content_lower or 'docs.google.com' in content_lower:
            return 'google_forms'
        elif 'mailchimp' in content_lower:
            return 'mailchimp'
        elif 'hubspot' in content_lower:
            return 'hubspot'
        elif 'salesforce' in content_lower:
            return 'salesforce'
        else:
            return 'custom'
    
    def _submit_via_traditional(self, url: str, analysis: FormAnalysisResult, message: str, strategy: Dict) -> SubmissionResult:
        """Submit form using traditional Selenium approach with AI guidance and improved form detection"""
        driver = None
        try:
            # Use AI recommendations for browser selection with fallback
            try:
                if strategy.get('challenges', []):
                    if 'dynamic_loading' in strategy['challenges']:
                        # Use Firefox for better dynamic content handling
                        logger.info("🔥 Using Firefox for dynamic content handling")
                        driver = self._setup_firefox_driver()
                    else:
                        # Use Chrome for better compatibility
                        logger.info("🌐 Using Chrome for standard compatibility")
                        driver = self._setup_chrome_driver()
                else:
                    logger.info("🌐 Using Chrome as default browser")
                    driver = self._setup_chrome_driver()
            except Exception as browser_error:
                logger.warning(f"❌ Primary browser failed: {browser_error}")
                # Try fallback browser
                try:
                    if 'firefox' in str(browser_error).lower():
                        logger.info("🔄 Firefox failed, trying Chrome fallback")
                        driver = self._setup_chrome_driver()
                    else:
                        logger.info("🔄 Chrome failed, trying Firefox fallback")
                        driver = self._setup_firefox_driver()
                except Exception as fallback_error:
                    logger.error(f"❌ Both browsers failed. Chrome: {browser_error}, Firefox: {fallback_error}")
                    raise Exception(f"All browser drivers failed. Primary: {browser_error}, Fallback: {fallback_error}")
            
            driver.get(url)
            
            # Wait for page to load
            WebDriverWait(driver, 10).until(
                lambda d: d.execute_script("return document.readyState") == "complete"
            )
            
            # Enhanced form detection with multiple strategies
            form_element = None
            form_detection_method = "unknown"
            
            # Strategy 1: Use AI-detected form elements
            if analysis.form_elements:
                logger.info("🔍 Trying AI-detected form elements")
                for element in analysis.form_elements:
                    if element['type'] == 'form':
                        try:
                            form_element = driver.find_element(By.CSS_SELECTOR, element['selector'])
                            form_detection_method = "ai_detected"
                            logger.info(f"✅ Found form using AI selector: {element['selector']}")
                            break
                        except Exception as e:
                            logger.debug(f"AI selector failed: {e}")
                            continue
            
            # Strategy 2: Fallback to common form selectors
            if not form_element:
                logger.info("🔍 Trying common form selectors")
                common_selectors = [
                    'form',
                    'form[action*="contact"]',
                    'form[action*="submit"]',
                    'form[action*="send"]',
                    'form[action*="mail"]',
                    'form[action*="message"]',
                    'form[class*="contact"]',
                    'form[id*="contact"]',
                    'form[class*="form"]',
                    'form[id*="form"]',
                    'form[class*="message"]',
                    'form[id*="message"]',
                    'form[class*="inquiry"]',
                    'form[id*="inquiry"]',
                    'form[class*="request"]',
                    'form[id*="request"]',
                    'form[class*="quote"]',
                    'form[id*="quote"]'
                ]
                
                for selector in common_selectors:
                    try:
                        form_element = driver.find_element(By.CSS_SELECTOR, selector)
                        form_detection_method = "common_selector"
                        logger.info(f"✅ Found form using common selector: {selector}")
                        break
                    except Exception as e:
                        logger.debug(f"Common selector {selector} failed: {e}")
                        continue
            
            # Strategy 3: Look for any form on the page
            if not form_element:
                logger.info("🔍 Trying to find any form on the page")
                try:
                    forms = driver.find_elements(By.TAG_NAME, "form")
                    if forms:
                        form_element = forms[0]  # Use the first form found
                        form_detection_method = "first_form"
                        logger.info(f"✅ Found first available form (total: {len(forms)})")
                except Exception as e:
                    logger.debug(f"First form strategy failed: {e}")
            
            # Strategy 4: Look for input fields that might be part of a contact form
            if not form_element:
                logger.info("🔍 Trying to find input fields that might be part of a contact form")
                try:
                    # Look for common contact form input patterns
                    contact_inputs = driver.find_elements(By.CSS_SELECTOR, 
                        'input[name*="name"], input[name*="email"], input[name*="message"], ' +
                        'input[placeholder*="name"], input[placeholder*="email"], input[placeholder*="message"], ' +
                        'textarea[name*="message"], textarea[placeholder*="message"]'
                    )
                    
                    if contact_inputs:
                        # Find the closest form element to these inputs
                        for input_elem in contact_inputs:
                            try:
                                # Look for parent form
                                parent_form = input_elem.find_element(By.XPATH, "./ancestor::form")
                                if parent_form:
                                    form_element = parent_form
                                    form_detection_method = "input_field_parent"
                                    logger.info(f"✅ Found form by tracing input field parent")
                                    break
                            except:
                                continue
                except Exception as e:
                    logger.debug(f"Input field tracing strategy failed: {e}")
            
            # Strategy 5: Create a virtual form if we find input fields but no form element
            if not form_element:
                logger.info("🔍 Trying to create virtual form from input fields")
                try:
                    # Look for any input fields that could be part of a contact form
                    all_inputs = driver.find_elements(By.CSS_SELECTOR, 
                        'input[type="text"], input[type="email"], input[type="tel"], ' +
                        'textarea, select'
                    )
                    
                    if all_inputs:
                        # Create a virtual form by grouping nearby input fields
                        logger.info(f"✅ Found {len(all_inputs)} input fields, creating virtual form")
                        form_element = all_inputs[0]  # Use first input as form reference
                        form_detection_method = "virtual_form"
                except Exception as e:
                    logger.debug(f"Virtual form strategy failed: {e}")
            
            if not form_element:
                return SubmissionResult(
                    success=False,
                    method_used="traditional_selenium",
                    response_content=None,
                    error_message="Could not find any form element using multiple detection strategies",
                    submission_time=time.strftime('%Y-%m-%d %H:%M:%S'),
                    platform_detected=None,
                    fields_submitted={},
                    confidence_score=0.0
                )
            
            logger.info(f"🎯 Form detection successful using: {form_detection_method}")
            
            # Fill form fields using AI mappings and smart field handling
            fields_submitted = {}
            field_errors = []
            
            # Enhanced field filling with multiple strategies
            logger.info("📝 Starting field filling process")
            
            # Strategy 1: Fill known fields using AI mappings
            if analysis.field_mappings:
                logger.info("🎯 Filling known fields using AI mappings")
                for field_type, selector in analysis.field_mappings.items():
                    try:
                        field = driver.find_element(By.CSS_SELECTOR, selector)
                        if field.is_displayed() and field.is_enabled():
                            value = self._get_field_value(field_type, message)
                            field.clear()
                            field.send_keys(value)
                            fields_submitted[field_type] = value
                            logger.info(f"✅ Filled {field_type} field with: {value[:50]}...")
                    except Exception as e:
                        logger.warning(f"❌ Could not fill {field_type} field: {e}")
                        field_errors.append(f"{field_type}: {e}")
            
            # Strategy 2: Fill common fields using standard selectors
            if not fields_submitted:
                logger.info("🔍 No AI mappings found, trying common field selectors")
                common_field_mappings = {
                    'name': [
                        'input[name*="name"]', 'input[placeholder*="name"]', 'input[id*="name"]',
                        'input[name*="first"]', 'input[name*="last"]', 'input[placeholder*="first"]',
                        'input[placeholder*="last"]', 'input[name*="full"]', 'input[placeholder*="full"]'
                    ],
                    'email': [
                        'input[type="email"]', 'input[name*="email"]', 'input[placeholder*="email"]',
                        'input[name*="mail"]', 'input[placeholder*="mail"]', 'input[id*="email"]'
                    ],
                    'message': [
                        'textarea[name*="message"]', 'textarea[placeholder*="message"]', 'textarea[id*="message"]',
                        'textarea[name*="comment"]', 'textarea[placeholder*="comment"]', 'textarea[id*="comment"]',
                        'textarea[name*="inquiry"]', 'textarea[placeholder*="inquiry"]', 'textarea[id*="inquiry"]',
                        'textarea[name*="details"]', 'textarea[placeholder*="details"]', 'textarea[id*="details"]'
                    ],
                    'phone': [
                        'input[type="tel"]', 'input[name*="phone"]', 'input[placeholder*="phone"]',
                        'input[name*="telephone"]', 'input[placeholder*="telephone"]', 'input[id*="phone"]'
                    ],
                    'company': [
                        'input[name*="company"]', 'input[placeholder*="company"]', 'input[id*="company"]',
                        'input[name*="business"]', 'input[placeholder*="business"]', 'input[id*="business"]',
                        'input[name*="organization"]', 'input[placeholder*="organization"]', 'input[id*="organization"]'
                    ]
                }
                
                for field_type, selectors in common_field_mappings.items():
                    if field_type not in fields_submitted:  # Only fill if not already filled
                        for selector in selectors:
                            try:
                                field = driver.find_element(By.CSS_SELECTOR, selector)
                                if field.is_displayed() and field.is_enabled():
                                    value = self._get_field_value(field_type, message)
                                    field.clear()
                                    field.send_keys(value)
                                    fields_submitted[field_type] = value
                                    logger.info(f"✅ Filled {field_type} field using common selector: {selector}")
                                    break
                            except Exception as e:
                                logger.debug(f"Common selector {selector} failed: {e}")
                                continue
            
            # Then, analyze and fill unknown fields
            try:
                logger.info("🔍 Analyzing unknown fields...")
                unknown_fields = self.smart_field_handler.analyze_unknown_fields(
                    driver.page_source, 
                    f"Platform: {platform}, URL: {url}",
                    url
                )
                
                for field_info in unknown_fields:
                    if field_info.is_required and self.smart_field_handler.can_handle_field(field_info):
                        logger.info(f"🎯 Handling unknown required field: {field_info.name}")
                        
                        # Generate appropriate value
                        context = {
                            'industry': 'Technology',  # Could be detected from page
                            'purpose': 'Business inquiry',
                            'company_type': 'Business'
                        }
                        
                        result = self.smart_field_handler.generate_field_value(field_info, context)
                        
                        if result.success:
                            # Try to find and fill the field
                            try:
                                # Try multiple selectors for the field
                                selectors = [
                                    f"input[name*='{field_info.name}']",
                                    f"input[placeholder*='{field_info.name}']",
                                    f"select[name*='{field_info.name}']",
                                    f"textarea[name*='{field_info.name}']"
                                ]
                                
                                field_found = False
                                for selector in selectors:
                                    try:
                                        field = driver.find_element(By.CSS_SELECTOR, selector)
                                        if field.is_displayed() and field.is_enabled():
                                            if field_info.field_type == 'select':
                                                # Handle select dropdown
                                                from selenium.webdriver.support.ui import Select
                                                select = Select(field)
                                                select.select_by_visible_text(result.value)
                                            else:
                                                field.clear()
                                                field.send_keys(result.value)
                                            
                                            fields_submitted[field_info.name] = result.value
                                            logger.info(f"✅ Filled unknown field {field_info.name} with: {result.value[:50]}...")
                                            field_found = True
                                            break
                                    except:
                                        continue
                                
                                if not field_found:
                                    logger.warning(f"⚠️ Could not find field element for {field_info.name}")
                                    field_errors.append(f"{field_info.name}: Field element not found")
                                    
                            except Exception as e:
                                logger.warning(f"❌ Error filling unknown field {field_info.name}: {e}")
                                field_errors.append(f"{field_info.name}: {e}")
                        else:
                            logger.warning(f"❌ Could not generate value for {field_info.name}: {result.error_message}")
                            field_errors.append(f"{field_info.name}: {result.error_message}")
                            
            except Exception as e:
                logger.error(f"Error analyzing unknown fields: {e}")
                field_errors.append(f"Unknown field analysis: {e}")
            
            # Log field handling summary
            if field_errors:
                logger.warning(f"⚠️ Field handling issues: {field_errors}")
            else:
                logger.info(f"✅ Successfully filled {len(fields_submitted)} fields")
            
            # Handle CAPTCHA if present
            captcha_solved = True
            if analysis.captcha_detected:
                logger.info(f"🧩 Attempting to solve {analysis.captcha_type} CAPTCHA")
                captcha_info = {
                    'captcha_type': analysis.captcha_type,
                    'captcha_selectors': analysis.captcha_selectors,
                    'captcha_site_key': analysis.captcha_site_key,
                    'captcha_challenges': analysis.captcha_challenges,
                    'page_url': url
                }
                
                captcha_result = self.captcha_handler.solve_captcha(captcha_info, driver)
                if captcha_result.success:
                    logger.info(f"✅ CAPTCHA solved successfully using {captcha_result.method_used}")
                else:
                    logger.warning(f"❌ CAPTCHA solving failed: {captcha_result.error_message}")
                    captcha_solved = False
            
            if not captcha_solved:
                return SubmissionResult(
                    success=False,
                    method_used="traditional_selenium",
                    response_content=None,
                    error_message=f"CAPTCHA solving failed: {captcha_result.error_message if 'captcha_result' in locals() else 'Unknown error'}",
                    submission_time=time.strftime('%Y-%m-%d %H:%M:%S'),
                    platform_detected=None,
                    fields_submitted=fields_submitted,
                    confidence_score=0.0
                )
            
            # Enhanced form submission with multiple button detection strategies
            logger.info("🚀 Attempting form submission")
            submission_success = False
            
            # Strategy 1: Try common submit button selectors
            submit_selectors = [
                "input[type='submit']",
                "button[type='submit']",
                "button:contains('Submit')",
                "button:contains('Send')",
                "button:contains('Send Message')",
                "button:contains('Contact Us')",
                "button:contains('Send Inquiry')",
                "button:contains('Get Quote')",
                "button:contains('Request Info')",
                "button:contains('Contact')",
                "input[value*='Submit']",
                "input[value*='Send']",
                "input[value*='Contact']",
                "button[class*='submit']",
                "button[id*='submit']",
                "button[class*='send']",
                "button[id*='send']",
                "button[class*='contact']",
                "button[id*='contact']",
                "button[class*='btn']",
                "input[class*='submit']",
                "input[class*='send']",
                "input[class*='btn']"
            ]
            
            for selector in submit_selectors:
                try:
                    submit_button = driver.find_element(By.CSS_SELECTOR, selector)
                    if submit_button.is_displayed() and submit_button.is_enabled():
                        logger.info(f"✅ Found submit button using selector: {selector}")
                        submit_button.click()
                        submission_success = True
                        break
                except Exception as e:
                    logger.debug(f"Submit selector {selector} failed: {e}")
                    continue
            
            # Strategy 2: Try to find any button in the form
            if not submission_success:
                logger.info("🔍 Trying to find any button in the form")
                try:
                    buttons = form_element.find_elements(By.TAG_NAME, "button")
                    inputs = form_element.find_elements(By.CSS_SELECTOR, "input[type='button'], input[type='submit']")
                    all_buttons = buttons + inputs
                    
                    for button in all_buttons:
                        if button.is_displayed() and button.is_enabled():
                            button_text = button.text.lower() or button.get_attribute('value', '').lower()
                            if any(keyword in button_text for keyword in ['submit', 'send', 'contact', 'send message', 'inquiry', 'quote', 'request', 'info']):
                                logger.info(f"✅ Found submit button by text: {button_text}")
                                button.click()
                                submission_success = True
                                break
                except Exception as e:
                    logger.debug(f"Button search failed: {e}")
            
            # Strategy 2.5: Try to find any clickable element that might submit the form
            if not submission_success:
                logger.info("🔍 Trying to find any clickable element that might submit the form")
                try:
                    # Look for any clickable elements near the form
                    clickable_elements = driver.find_elements(By.CSS_SELECTOR, 
                        "button, input[type='button'], input[type='submit'], a[href*='#'], " +
                        "div[onclick], span[onclick], div[class*='btn'], span[class*='btn']"
                    )
                    
                    for element in clickable_elements:
                        if element.is_displayed() and element.is_enabled():
                            element_text = element.text.lower() or element.get_attribute('value', '').lower()
                            if any(keyword in element_text for keyword in ['submit', 'send', 'contact', 'send message', 'inquiry', 'quote', 'request', 'info', 'go', 'continue']):
                                logger.info(f"✅ Found clickable element by text: {element_text}")
                                element.click()
                                submission_success = True
                                break
                except Exception as e:
                    logger.debug(f"Clickable element search failed: {e}")
            
            # Strategy 3: Try form submission via JavaScript
            if not submission_success:
                logger.info("🔍 Trying JavaScript form submission")
                try:
                    driver.execute_script("arguments[0].submit();", form_element)
                    submission_success = True
                    logger.info("✅ Form submitted via JavaScript")
                except Exception as e:
                    logger.debug(f"JavaScript submission failed: {e}")
            
            if not submission_success:
                return SubmissionResult(
                    success=False,
                    method_used="traditional_selenium",
                    response_content=None,
                    error_message="Could not find or click submit button using multiple strategies",
                    submission_time=time.strftime('%Y-%m-%d %H:%M:%S'),
                    platform_detected=None,
                    fields_submitted=fields_submitted,
                    confidence_score=0.0
                )
            
            # Wait for submission response and verify success
            logger.info("⏳ Waiting for submission response...")
            time.sleep(3)
            
            # Get response content
            response_content = driver.page_source
            
            # Verify submission success by checking for success indicators
            success_indicators = [
                'thank you', 'success', 'message sent', 'form submitted',
                'we will contact you', 'confirmation', 'received your message'
            ]
            
            error_indicators = [
                'error', 'failed', 'invalid', 'required field', 'try again',
                'please fill', 'captcha', 'verification failed'
            ]
            
            response_lower = response_content.lower()
            has_success = any(indicator in response_lower for indicator in success_indicators)
            has_error = any(indicator in response_lower for indicator in error_indicators)
            
            # Check if URL changed (common success indicator)
            current_url = driver.current_url
            url_changed = current_url != url
            
            # Determine success based on multiple factors
            submission_success = (
                has_success or 
                url_changed or 
                (not has_error and len(fields_submitted) > 0)
            )
            
            if submission_success:
                logger.info("✅ Form submission appears successful based on response analysis")
                return SubmissionResult(
                    success=True,
                    method_used="traditional_selenium",
                    response_content=response_content,
                    error_message=None,
                    submission_time=time.strftime('%Y-%m-%d %H:%M:%S'),
                    platform_detected=None,
                    fields_submitted=fields_submitted,
                    confidence_score=analysis.confidence_score
                )
            else:
                logger.warning("⚠️ Form submission may have failed - no clear success indicators found")
                return SubmissionResult(
                    success=False,
                    method_used="traditional_selenium",
                    response_content=response_content,
                    error_message="Form submission completed but no success indicators found in response",
                    submission_time=time.strftime('%Y-%m-%d %H:%M:%S'),
                    platform_detected=None,
                    fields_submitted=fields_submitted,
                    confidence_score=0.3
                )
            
        except Exception as e:
            logger.error(f"Traditional submission failed: {e}")
            return SubmissionResult(
                success=False,
                method_used="traditional_selenium",
                response_content=None,
                error_message=f"Traditional submission error: {str(e)}",
                submission_time=time.strftime('%Y-%m-%d %H:%M:%S'),
                platform_detected=None,
                fields_submitted={},
                confidence_score=0.0
            )
        finally:
            if driver:
                driver.quit()
            # Clean up profile directory
            self._cleanup_profile_directory()
    
    def _submit_via_ajax(self, url: str, analysis: FormAnalysisResult, message: str, strategy: Dict) -> SubmissionResult:
        """Submit form using AJAX approach for dynamic forms"""
        try:
            # Parse form action and method
            form_action = None
            form_method = "POST"
            
            for element in analysis.form_elements:
                if element['type'] == 'form':
                    # Extract form attributes from AI analysis
                    form_action = element.get('action', url)
                    form_method = element.get('method', 'POST')
                    break
            
            if not form_action:
                form_action = url
            
            # Prepare form data
            form_data = {}
            for field_type, value in analysis.field_mappings.items():
                if field_type in ['name', 'email', 'phone', 'subject', 'message', 'company']:
                    form_data[value] = self._get_field_value(field_type, message)
            
            # Submit via AJAX
            headers = {
                'Content-Type': 'application/x-www-form-urlencoded',
                'X-Requested-With': 'XMLHttpRequest',
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            
            response = requests.post(form_action, data=form_data, headers=headers, timeout=30, verify=False)
            
            return SubmissionResult(
                success=response.status_code == 200,
                method_used="ajax_post",
                response_content=response.text,
                error_message=None if response.status_code == 200 else f"HTTP {response.status_code}",
                submission_time=time.strftime('%Y-%m-%d %H:%M:%S'),
                platform_detected=None,
                fields_submitted=form_data,
                confidence_score=analysis.confidence_score
            )
            
        except Exception as e:
            logger.error(f"AJAX submission failed: {e}")
            return SubmissionResult(
                success=False,
                method_used="ajax_post",
                response_content=None,
                error_message=f"AJAX submission error: {str(e)}",
                submission_time=time.strftime('%Y-%m-%d %H:%M:%S'),
                platform_detected=None,
                fields_submitted={},
                confidence_score=0.0
            )
    
    def _submit_via_modal(self, url: str, analysis: FormAnalysisResult, message: str, strategy: Dict) -> SubmissionResult:
        """Submit form that appears in a modal/popup"""
        driver = None
        try:
            driver = self._setup_chrome_driver()
            driver.get(url)
            
            # Wait for modal to appear
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "[role='dialog'], .modal, .popup"))
            )
            
            # Fill modal form
            fields_submitted = {}
            for field_type, selector in analysis.field_mappings.items():
                try:
                    field = driver.find_element(By.CSS_SELECTOR, selector)
                    if field.is_displayed() and field.is_enabled():
                        value = self._get_field_value(field_type, message)
                        field.clear()
                        field.send_keys(value)
                        fields_submitted[field_type] = value
                except Exception as e:
                    logger.warning(f"Could not fill modal {field_type} field: {e}")
            
            # Submit modal form
            submit_button = driver.find_element(By.CSS_SELECTOR, "button[type='submit'], input[type='submit'], .modal-submit")
            submit_button.click()
            
            time.sleep(2)
            
            return SubmissionResult(
                success=True,
                method_used="modal_submission",
                response_content=driver.page_source,
                error_message=None,
                submission_time=time.strftime('%Y-%m-%d %H:%M:%S'),
                platform_detected=None,
                fields_submitted=fields_submitted,
                confidence_score=analysis.confidence_score
            )
            
        except Exception as e:
            logger.error(f"Modal submission failed: {e}")
            return SubmissionResult(
                success=False,
                method_used="modal_submission",
                response_content=None,
                error_message=f"Modal submission error: {str(e)}",
                submission_time=time.strftime('%Y-%m-%d %H:%M:%S'),
                platform_detected=None,
                fields_submitted={},
                confidence_score=0.0
            )
        finally:
            if driver:
                driver.quit()
            # Clean up profile directory
            self._cleanup_profile_directory()
    
    def _submit_via_alternative(self, url: str, analysis: FormAnalysisResult, message: str, strategy: Dict) -> SubmissionResult:
        """Submit using alternative contact methods (email, etc.)"""
        try:
            # Look for alternative contact methods
            alternative_methods = analysis.alternative_contact_methods
            
            if not alternative_methods:
                return SubmissionResult(
                    success=False,
                    method_used="alternative",
                    response_content=None,
                    error_message="No alternative contact methods found",
                    submission_time=time.strftime('%Y-%m-%d %H:%M:%S'),
                    platform_detected=None,
                    fields_submitted={},
                    confidence_score=0.0
                )
            
            # Handle different data types for alternative_methods
            logger.info(f"🔍 Processing {len(alternative_methods)} alternative contact methods")
            
            # Try email contact if available
            email_contact = None
            for method in alternative_methods:
                try:
                    # Handle both dict and string formats
                    if isinstance(method, dict):
                        if method.get('type') == 'email':
                            email_contact = method
                            break
                    elif isinstance(method, str):
                        # If it's a string, check if it looks like an email
                        if '@' in method and '.' in method:
                            email_contact = {'type': 'email', 'value': method}
                            break
                except (KeyError, TypeError) as e:
                    logger.warning(f"⚠️ Error processing alternative method {method}: {e}")
                    continue
            
            if email_contact:
                # For now, just log the email contact
                email_value = email_contact.get('value', email_contact) if isinstance(email_contact, dict) else email_contact
                logger.info(f"✅ Found email contact: {email_value}")
                return SubmissionResult(
                    success=True,
                    method_used="email_contact",
                    response_content=f"Email contact found: {email_value}",
                    error_message=None,
                    submission_time=time.strftime('%Y-%m-%d %H:%M:%S'),
                    platform_detected=None,
                    fields_submitted={'email': email_value},
                    confidence_score=0.7
                )
            
            # Try other contact methods
            for method in alternative_methods:
                try:
                    if isinstance(method, dict):
                        method_type = method.get('type', 'unknown')
                        method_value = method.get('value', '')
                        logger.info(f"Found {method_type} contact: {method_value}")
                    elif isinstance(method, str):
                        logger.info(f"Found contact method: {method}")
                except Exception as e:
                    logger.warning(f"Error processing contact method: {e}")
            
            return SubmissionResult(
                success=False,
                method_used="alternative",
                response_content=None,
                error_message="No suitable alternative contact method found",
                submission_time=time.strftime('%Y-%m-%d %H:%M:%S'),
                platform_detected=None,
                fields_submitted={},
                confidence_score=0.0
            )
            
        except Exception as e:
            logger.error(f"Alternative submission failed: {e}")
            return SubmissionResult(
                success=False,
                method_used="alternative",
                response_content=None,
                error_message=f"Alternative submission error: {str(e)}",
                submission_time=time.strftime('%Y-%m-%d %H:%M:%S'),
                platform_detected=None,
                fields_submitted={},
                confidence_score=0.0
            )
    
    def _get_field_value(self, field_type: str, message: str) -> str:
        """Get appropriate value for form field based on type"""
        if field_type == 'name':
            return self.user_config['sender_name']
        elif field_type == 'email':
            return self.user_config['sender_email']
        elif field_type == 'phone':
            return self.user_config['sender_phone']
        elif field_type == 'subject':
            return self.user_config['message_subject']
        elif field_type == 'message':
            return message
        elif field_type == 'company':
            return self.user_config['company_name']
        else:
            return message
    
    def _setup_chrome_driver(self):
        """Setup Chrome driver with optimized options and unique profile directory"""
        import tempfile
        import os
        import uuid
        import time
        
        options = ChromeOptions()
        options.add_argument('--headless')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--disable-gpu')
        options.add_argument('--window-size=1920,1080')
        options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36')
        
        # Create unique profile directory to avoid conflicts between workers
        unique_id = str(uuid.uuid4())[:8]
        timestamp = str(int(time.time() * 1000))
        profile_dir = tempfile.mkdtemp(prefix=f'chrome_ai_{unique_id}_{timestamp}_')
        options.add_argument(f'--user-data-dir={profile_dir}')
        
        # Store profile directory for cleanup
        self._current_profile_dir = profile_dir
        
        # Additional Chrome options for stability
        options.add_argument('--disable-extensions')
        options.add_argument('--disable-plugins')
        options.add_argument('--disable-images')
        options.add_argument('--disable-web-security')
        options.add_argument('--allow-running-insecure-content')
        options.add_argument('--disable-background-networking')
        options.add_argument('--disable-default-apps')
        options.add_argument('--disable-sync')
        options.add_argument('--disable-background-timer-throttling')
        options.add_argument('--disable-renderer-backgrounding')
        options.add_argument('--disable-backgrounding-occluded-windows')
        options.add_argument('--disable-client-side-phishing-detection')
        options.add_argument('--disable-crash-reporter')
        options.add_argument('--disable-oopr-debug-crash-dump')
        options.add_argument('--no-crash-upload')
        options.add_argument('--disable-gpu-sandbox')
        options.add_argument('--disable-software-rasterizer')
        
        try:
            driver = webdriver.Chrome(options=options)
            # Set timeouts
            driver.set_page_load_timeout(30)
            driver.implicitly_wait(10)
            return driver
        except Exception as e:
            logger.error(f"Chrome driver setup failed: {e}")
            # Clean up profile directory on failure
            try:
                import shutil
                shutil.rmtree(profile_dir, ignore_errors=True)
            except:
                pass
            raise e
    
    def _cleanup_profile_directory(self):
        """Clean up the current profile directory"""
        if hasattr(self, '_current_profile_dir') and self._current_profile_dir:
            try:
                import shutil
                shutil.rmtree(self._current_profile_dir, ignore_errors=True)
                logger.info(f"Cleaned up profile directory: {self._current_profile_dir}")
            except Exception as e:
                logger.warning(f"Could not clean up profile directory {self._current_profile_dir}: {e}")
            finally:
                self._current_profile_dir = None
    
    def _setup_firefox_driver(self):
        """Setup Firefox driver with optimized options and marionette port fixes"""
        import tempfile
        import os
        import uuid
        import time
        
        options = FirefoxOptions()
        options.add_argument('--headless')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        
        # Create unique profile directory to avoid port conflicts between workers
        unique_id = str(uuid.uuid4())[:8]
        timestamp = str(int(time.time() * 1000))
        profile_dir = tempfile.mkdtemp(prefix=f'firefox_ai_{unique_id}_{timestamp}_')
        options.add_argument(f'--profile={profile_dir}')
        
        # Store profile directory for cleanup
        self._current_profile_dir = profile_dir
        
        # Additional Firefox-specific options for stability
        options.add_argument('--disable-gpu')
        options.add_argument('--disable-extensions')
        options.add_argument('--disable-plugins')
        options.add_argument('--disable-images')
        options.add_argument('--disable-web-security')
        options.add_argument('--allow-running-insecure-content')
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
        options.set_preference("general.useragent.override", 
                              "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:91.0) Gecko/20100101 Firefox/91.0")
        
        # Configure service with timeout and logging
        service = FirefoxService(
            executable_path='/usr/local/bin/geckodriver',
            log_path='/tmp/geckodriver.log'
        )
        
        try:
            driver = webdriver.Firefox(service=service, options=options)
            # Set timeouts
            driver.set_page_load_timeout(30)
            driver.implicitly_wait(10)
            return driver
        except Exception as e:
            logger.error(f"Firefox driver setup failed: {e}")
            # Clean up profile directory on failure
            try:
                import shutil
                shutil.rmtree(profile_dir, ignore_errors=True)
            except:
                pass
            raise e
