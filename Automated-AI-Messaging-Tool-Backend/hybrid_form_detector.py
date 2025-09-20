"""
Hybrid Form Detection System
Combines traditional script-based detection with AI-powered analysis
"""

import logging
import time
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from ai_form_analyzer import AIFormAnalyzer, FormAnalysisResult

logger = logging.getLogger(__name__)

@dataclass
class DetectionResult:
    """Result of hybrid form detection"""
    success: bool
    method_used: str  # 'traditional', 'ai_enhanced', 'ai_guided'
    confidence_score: float
    form_data: Dict[str, Any]
    field_mappings: Dict[str, str]
    submission_strategy: Dict[str, Any]
    error_message: Optional[str] = None
    detection_time: float = 0.0

class HybridFormDetector:
    """Hybrid form detection combining traditional and AI methods"""
    
    def __init__(self):
        """Initialize the hybrid form detector"""
        self.ai_analyzer = AIFormAnalyzer()
        self.traditional_detector = TraditionalFormDetector()
        
    def detect_contact_form(self, form_url: str, driver: webdriver.Chrome) -> DetectionResult:
        """
        Detect contact form using hybrid approach
        
        Args:
            form_url: URL of the contact form page
            driver: Selenium WebDriver instance
            
        Returns:
            DetectionResult with form detection details
        """
        start_time = time.time()
        
        try:
            logger.info(f"Starting hybrid form detection for {form_url}")
            
            # Tier 1: Traditional script-based detection
            logger.info("Tier 1: Attempting traditional form detection")
            traditional_result = self.traditional_detector.detect_form(driver, form_url)
            
            if traditional_result['success']:
                logger.info(f"✅ Traditional detection successful for {form_url}")
                return DetectionResult(
                    success=True,
                    method_used='traditional',
                    confidence_score=traditional_result.get('confidence', 0.8),
                    form_data=traditional_result['form_data'],
                    field_mappings=traditional_result['field_mappings'],
                    submission_strategy={'method': 'traditional', 'confidence': 0.8},
                    detection_time=time.time() - start_time
                )
            
            # Tier 2: AI-enhanced detection
            logger.info("Tier 2: Attempting AI-enhanced detection")
            ai_result = self._ai_enhanced_detection(driver, form_url)
            
            if ai_result.success:
                logger.info(f"✅ AI-enhanced detection successful for {form_url}")
                return DetectionResult(
                    success=True,
                    method_used='ai_enhanced',
                    confidence_score=ai_result.confidence_score,
                    form_data=self._convert_ai_result_to_form_data(ai_result),
                    field_mappings=ai_result.field_mappings,
                    submission_strategy=self._get_ai_submission_strategy(ai_result),
                    detection_time=time.time() - start_time
                )
            
            # Tier 3: AI-guided analysis with fallback
            logger.info("Tier 3: Attempting AI-guided analysis")
            guided_result = self._ai_guided_analysis(driver, form_url)
            
            if guided_result.success:
                logger.info(f"✅ AI-guided analysis successful for {form_url}")
                return DetectionResult(
                    success=True,
                    method_used='ai_guided',
                    confidence_score=guided_result.confidence_score,
                    form_data=self._convert_ai_result_to_form_data(guided_result),
                    field_mappings=guided_result.field_mappings,
                    submission_strategy=self._get_ai_submission_strategy(guided_result),
                    detection_time=time.time() - start_time
                )
            
            # All methods failed
            logger.error(f"❌ All detection methods failed for {form_url}")
            return DetectionResult(
                success=False,
                method_used='none',
                confidence_score=0.0,
                form_data={},
                field_mappings={},
                submission_strategy={},
                error_message="All detection methods failed",
                detection_time=time.time() - start_time
            )
            
        except Exception as e:
            logger.error(f"Error in hybrid form detection for {form_url}: {e}")
            return DetectionResult(
                success=False,
                method_used='error',
                confidence_score=0.0,
                form_data={},
                field_mappings={},
                submission_strategy={},
                error_message=str(e),
                detection_time=time.time() - start_time
            )
    
    def _ai_enhanced_detection(self, driver: webdriver.Chrome, form_url: str) -> FormAnalysisResult:
        """Use AI to enhance form detection"""
        try:
            # Get page content
            page_html = driver.page_source
            page_title = driver.title
            
            # Use AI to analyze the page
            ai_result = self.ai_analyzer.analyze_page_for_forms(page_html, form_url, page_title)
            
            if ai_result.success and ai_result.confidence_score > 0.5:
                # Try to validate AI findings with Selenium
                validated_result = self._validate_ai_findings(driver, ai_result)
                return validated_result
            
            return ai_result
            
        except Exception as e:
            logger.error(f"Error in AI-enhanced detection: {e}")
            return FormAnalysisResult(
                success=False,
                confidence_score=0.0,
                form_elements=[],
                contact_sections=[],
                submission_methods=[],
                field_mappings={},
                alternative_contact_methods=[],
                error_message=str(e)
            )
    
    def _ai_guided_analysis(self, driver: webdriver.Chrome, form_url: str) -> FormAnalysisResult:
        """Use AI for guided analysis when other methods fail"""
        try:
            # Get page content
            page_html = driver.page_source
            page_title = driver.title
            
            # Use AI for comprehensive analysis
            ai_result = self.ai_analyzer.analyze_page_for_forms(page_html, form_url, page_title)
            
            # Even if confidence is low, try to use AI suggestions
            if ai_result.form_elements or ai_result.alternative_contact_methods:
                logger.info(f"Using AI suggestions with confidence {ai_result.confidence_score}")
                return ai_result
            
            return ai_result
            
        except Exception as e:
            logger.error(f"Error in AI-guided analysis: {e}")
            return FormAnalysisResult(
                success=False,
                confidence_score=0.0,
                form_elements=[],
                contact_sections=[],
                submission_methods=[],
                field_mappings={},
                alternative_contact_methods=[],
                error_message=str(e)
            )
    
    def _validate_ai_findings(self, driver: webdriver.Chrome, ai_result: FormAnalysisResult) -> FormAnalysisResult:
        """Validate AI findings using Selenium"""
        try:
            validated_elements = []
            
            for element in ai_result.form_elements:
                try:
                    # Try to find the element using the AI-suggested selector
                    if 'selector' in element:
                        found_element = driver.find_element(By.CSS_SELECTOR, element['selector'])
                        if found_element.is_displayed():
                            element['validated'] = True
                            validated_elements.append(element)
                        else:
                            element['validated'] = False
                    else:
                        element['validated'] = False
                        
                except Exception as e:
                    logger.debug(f"Could not validate element {element.get('selector', 'unknown')}: {e}")
                    element['validated'] = False
            
            # Update the result with validated elements
            ai_result.form_elements = validated_elements
            ai_result.confidence_score = len([e for e in validated_elements if e.get('validated', False)]) / max(len(validated_elements), 1)
            
            return ai_result
            
        except Exception as e:
            logger.error(f"Error validating AI findings: {e}")
            return ai_result
    
    def _convert_ai_result_to_form_data(self, ai_result: FormAnalysisResult) -> Dict[str, Any]:
        """Convert AI analysis result to form data format"""
        if not ai_result.form_elements:
            return {}
        
        # Use the first (most confident) form element
        best_element = max(ai_result.form_elements, key=lambda x: x.get('confidence', 0))
        
        return {
            'form_element': best_element,
            'field_mapping': ai_result.field_mappings,
            'form_action': best_element.get('action', ''),
            'form_method': best_element.get('method', 'POST'),
            'form_url': best_element.get('url', ''),
            'submission_method': best_element.get('submission_method', 'form_submit'),
            'confidence': ai_result.confidence_score
        }
    
    def _get_ai_submission_strategy(self, ai_result: FormAnalysisResult) -> Dict[str, Any]:
        """Get submission strategy from AI result"""
        if not ai_result.form_elements:
            return {'method': 'none', 'confidence': 0.0}
        
        best_element = max(ai_result.form_elements, key=lambda x: x.get('confidence', 0))
        
        return {
            'method': best_element.get('submission_method', 'form_submit'),
            'confidence': ai_result.confidence_score,
            'recommendations': ai_result.form_elements,
            'alternative_methods': ai_result.alternative_contact_methods
        }

class TraditionalFormDetector:
    """Traditional script-based form detection (existing logic)"""
    
    def detect_form(self, driver: webdriver.Chrome, form_url: str) -> Dict[str, Any]:
        """Traditional form detection using CSS selectors"""
        try:
            # Wait for page to load
            WebDriverWait(driver, 10).until(
                lambda d: d.execute_script("return document.readyState") == "complete"
            )
            
            # Find form elements with comprehensive detection
            form = None
            form_selectors = [
                "form",  # Basic form tag
                "form[action*='contact']",
                "form[action*='submit']", 
                "form[action*='send']",
                "form[action*='message']",
                "form[action*='inquiry']",
                "div[class*='contact-form']",
                "div[class*='contactform']",
                "div[class*='contact-form']",
                "div[id*='contact-form']",
                "div[id*='contactform']",
                "section[class*='contact']",
                "div[class*='form']",
                "div[id*='form']"
            ]
            
            for selector in form_selectors:
                try:
                    form = driver.find_element(By.CSS_SELECTOR, selector)
                    if form.is_displayed():
                        logger.info(f"✅ Found form element using selector: {selector}")
                        break
                except Exception as e:
                    logger.debug(f"Selector '{selector}' failed: {e}")
                    continue
            
            if not form:
                return {
                    'success': False,
                    'confidence': 0.0,
                    'form_data': {},
                    'field_mappings': {},
                    'error': 'No visible form element found'
                }
            
            # Map form fields
            field_mappings = self._detect_form_fields(driver)
            
            return {
                'success': True,
                'confidence': 0.8,
                'form_data': {
                    'form_element': form,
                    'form_action': form.get_attribute('action'),
                    'form_method': form.get_attribute('method'),
                    'form_url': form_url
                },
                'field_mappings': field_mappings
            }
            
        except Exception as e:
            logger.error(f"Error in traditional form detection: {e}")
            return {
                'success': False,
                'confidence': 0.0,
                'form_data': {},
                'field_mappings': {},
                'error': str(e)
            }
    
    def _detect_form_fields(self, driver: webdriver.Chrome) -> Dict[str, str]:
        """Detect form fields using traditional selectors"""
        field_mappings = {}
        
        # Name field detection
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
                    field_mappings['name'] = selector
                    break
            except:
                continue
        
        # Email field detection
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
                    field_mappings['email'] = selector
                    break
            except:
                continue
        
        # Phone field detection
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
                    field_mappings['phone'] = selector
                    break
            except:
                continue
        
        # Message field detection
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
                    field_mappings['message'] = selector
                    break
            except:
                continue
        
        # Subject field detection
        subject_selectors = [
            "input[name*='subject' i]",
            "input[id*='subject' i]",
            "input[placeholder*='subject' i]"
        ]
        
        for selector in subject_selectors:
            try:
                element = driver.find_element(By.CSS_SELECTOR, selector)
                if element.is_displayed():
                    field_mappings['subject'] = selector
                    break
            except:
                continue
        
        return field_mappings
