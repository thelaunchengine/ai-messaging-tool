"""
AI-Powered Form Detection and Analysis Module
Uses Gemini AI to intelligently detect and analyze contact forms
"""

import os
import json
import logging
import google.generativeai as genai
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
import time
from ai_services.robust_json_parser import RobustJSONParser, ParseResult

logger = logging.getLogger(__name__)

@dataclass
class FormAnalysisResult:
    """Result of AI form analysis"""
    success: bool
    confidence_score: float
    form_elements: List[Dict[str, Any]]
    contact_sections: List[Dict[str, Any]]
    submission_methods: List[str]
    field_mappings: Dict[str, str]
    alternative_contact_methods: List[Dict[str, str]]
    captcha_detected: bool = False
    captcha_type: Optional[str] = None
    captcha_selectors: List[str] = None
    captcha_site_key: Optional[str] = None
    captcha_challenges: List[str] = None
    error_message: Optional[str] = None
    analysis_time: float = 0.0

class AIFormAnalyzer:
    """AI-powered form detection and analysis using Gemini"""
    
    def __init__(self):
        """Initialize the AI form analyzer with Gemini API"""
        self.api_key = os.getenv('GEMINI_API_KEY')
        if not self.api_key:
            raise ValueError("GEMINI_API_KEY environment variable is required")
        
        # Configure Gemini
        genai.configure(api_key=self.api_key)
        self.model = genai.GenerativeModel('gemini-1.5-pro')
        
        # Initialize robust JSON parser
        self.json_parser = RobustJSONParser()
        
        # Analysis cache to reduce API calls
        self.analysis_cache = {}
        
    def analyze_page_for_forms(self, page_html: str, page_url: str, page_title: str = "") -> FormAnalysisResult:
        """
        Use AI to analyze page content and identify potential contact forms
        
        Args:
            page_html: The HTML content of the page
            page_url: The URL of the page
            page_title: Optional page title for context
            
        Returns:
            FormAnalysisResult with analysis details
        """
        start_time = time.time()
        
        try:
            # Check cache first
            cache_key = f"{page_url}_{hash(page_html[:1000])}"
            if cache_key in self.analysis_cache:
                logger.info(f"Using cached analysis for {page_url}")
                cached_result = self.analysis_cache[cache_key]
                cached_result.analysis_time = time.time() - start_time
                return cached_result
            
            # Prepare HTML content (limit size for API)
            html_content = self._prepare_html_content(page_html)
            
            # Create analysis prompt
            prompt = self._create_form_analysis_prompt(page_url, page_title, html_content)
            
            logger.info(f"Analyzing page for forms: {page_url}")
            
            # Call Gemini API with retry logic
            response = None
            for attempt in range(self.json_parser.max_retries):
                try:
                    logger.info(f"🤖 Calling Gemini API (attempt {attempt + 1}/{self.json_parser.max_retries})")
                    response = self.model.generate_content(prompt)
                    break
                except Exception as e:
                    logger.warning(f"⚠️ Gemini API call failed (attempt {attempt + 1}): {e}")
                    if attempt == self.json_parser.max_retries - 1:
                        raise e
                    time.sleep(2 ** attempt)  # Exponential backoff
            
            # Parse AI response with robust parsing
            result = self._parse_ai_response_robust(response.text, page_url)
            result.analysis_time = time.time() - start_time
            
            # Cache successful results
            if result.success:
                self.analysis_cache[cache_key] = result
                logger.info(f"Analysis completed for {page_url} in {result.analysis_time:.2f}s")
            
            return result
            
        except Exception as e:
            logger.error(f"Error analyzing page {page_url}: {e}")
            return FormAnalysisResult(
                success=False,
                confidence_score=0.0,
                form_elements=[],
                contact_sections=[],
                submission_methods=[],
                field_mappings={},
                alternative_contact_methods=[],
                error_message=str(e),
                analysis_time=time.time() - start_time
            )
    
    def map_form_fields(self, form_html: str, page_context: str, page_url: str) -> Dict[str, Any]:
        """
        Use AI to intelligently map form fields to standard contact form fields
        
        Args:
            form_html: HTML content of the specific form
            page_context: Additional context about the page
            page_url: URL of the page for context
            
        Returns:
            Dictionary with field mappings and selectors
        """
        try:
            prompt = self._create_field_mapping_prompt(form_html, page_context, page_url)
            
            logger.info(f"Mapping form fields for {page_url}")
            
            response = self.model.generate_content(prompt)
            
            # Parse field mapping response with robust parsing
            field_mapping = self._parse_field_mapping_response_robust(response.text)
            
            logger.info(f"Field mapping completed for {page_url}")
            return field_mapping
            
        except Exception as e:
            logger.error(f"Error mapping form fields for {page_url}: {e}")
            return {
                'success': False,
                'field_mappings': {},
                'selectors': {},
                'error': str(e)
            }
    
    def suggest_submission_strategy(self, form_data: Dict, generated_message: str, page_context: str) -> Dict[str, Any]:
        """
        Use AI to determine the best form submission strategy
        
        Args:
            form_data: Detected form structure and fields
            generated_message: The AI-generated message to submit
            page_context: Additional page context
            
        Returns:
            Dictionary with submission strategy recommendations
        """
        try:
            prompt = self._create_submission_strategy_prompt(form_data, generated_message, page_context)
            
            logger.info("Determining submission strategy")
            
            response = self.model.generate_content(prompt)
            
            # Parse submission strategy response with robust parsing
            strategy = self._parse_submission_strategy_response_robust(response.text)
            
            logger.info("Submission strategy determined")
            return strategy
            
        except Exception as e:
            logger.error(f"Error determining submission strategy: {e}")
            return {
                'success': False,
                'strategy': 'traditional',
                'recommendations': [],
                'error': str(e)
            }
    
    def _prepare_html_content(self, page_html: str, max_length: int = 8000) -> str:
        """Prepare HTML content for AI analysis, limiting size"""
        # Remove script and style tags to focus on structure
        import re
        
        # Remove script and style content
        html_clean = re.sub(r'<script[^>]*>.*?</script>', '', page_html, flags=re.DOTALL | re.IGNORECASE)
        html_clean = re.sub(r'<style[^>]*>.*?</style>', '', html_clean, flags=re.DOTALL | re.IGNORECASE)
        
        # Remove excessive whitespace
        html_clean = re.sub(r'\s+', ' ', html_clean)
        
        # Limit length
        if len(html_clean) > max_length:
            html_clean = html_clean[:max_length] + "..."
        
        return html_clean
    
    def _create_form_analysis_prompt(self, page_url: str, page_title: str, html_content: str) -> str:
        """Create the prompt for form analysis"""
        return f"""
Analyze this webpage HTML and identify all potential contact forms or contact methods.

URL: {page_url}
Title: {page_title}
HTML Content: {html_content}

Please look for:
1. Traditional <form> elements with contact-related fields
2. Contact sections with input fields (even without <form> tags)
3. Modal forms or popup contact forms
4. Contact buttons that might trigger forms
5. Alternative contact methods (email links, phone numbers, contact info)
6. Any interactive elements that could be used for contact
7. CAPTCHA systems (reCAPTCHA, hCaptcha, Cloudflare, custom CAPTCHAs)
8. Security challenges and anti-bot measures

Return your analysis as a JSON object with this structure:
{{
    "success": true/false,
    "confidence_score": 0.0-1.0,
    "form_elements": [
        {{
            "type": "form|section|button|modal",
            "selector": "CSS selector to find this element",
            "description": "What this element appears to be",
            "fields_detected": ["name", "email", "phone", "message", "subject"],
            "submission_method": "form_submit|ajax|modal|button_click",
            "confidence": 0.0-1.0
        }}
    ],
    "contact_sections": [
        {{
            "selector": "CSS selector",
            "description": "Description of contact section",
            "contains_form": true/false,
            "contact_methods": ["email", "phone", "form", "chat"]
        }}
    ],
    "submission_methods": ["form_submit", "ajax", "modal", "email_link"],
    "alternative_contact_methods": [
        {{
            "type": "email|phone|chat|social",
            "value": "contact@example.com",
            "selector": "CSS selector if applicable"
        }}
    ],
    "captcha_detected": true/false,
    "captcha_type": "recaptcha_v2|recaptcha_v3|hcaptcha|cloudflare|custom|none",
    "captcha_selectors": [
        ".g-recaptcha",
        "#captcha",
        "[data-sitekey]"
    ],
    "captcha_site_key": "6Lc...",
    "captcha_challenges": [
        "image_recognition",
        "checkbox_verification", 
        "invisible_verification",
        "audio_challenge",
        "math_problem"
    ],
    "recommendations": [
        "Specific recommendations for form detection and submission"
    ]
}}

Focus on finding practical, actionable contact methods that can be automated.
"""
    
    def _create_field_mapping_prompt(self, form_html: str, page_context: str, page_url: str) -> str:
        """Create the prompt for field mapping"""
        return f"""
Analyze this form HTML and map fields to standard contact form fields.

Page URL: {page_url}
Page Context: {page_context}
Form HTML: {form_html}

Map to these standard fields:
- name: Full name, first name, last name, etc.
- email: Email address
- phone: Phone number, telephone
- subject: Subject line, topic, inquiry type
- message: Message, comment, inquiry details
- company: Company name, business name

Return JSON with this structure:
{{
    "success": true/false,
    "field_mappings": {{
        "name": "CSS selector for name field",
        "email": "CSS selector for email field",
        "phone": "CSS selector for phone field",
        "subject": "CSS selector for subject field",
        "message": "CSS selector for message field",
        "company": "CSS selector for company field"
    }},
    "selectors": {{
        "name": ["input[name*='name']", "input[placeholder*='name']"],
        "email": ["input[type='email']", "input[name*='email']"],
        "phone": ["input[type='tel']", "input[name*='phone']"],
        "subject": ["input[name*='subject']", "input[placeholder*='subject']"],
        "message": ["textarea[name*='message']", "textarea[placeholder*='message']"],
        "company": ["input[name*='company']", "input[placeholder*='company']"]
    }},
    "form_attributes": {{
        "action": "form action URL",
        "method": "GET|POST",
        "enctype": "application/x-www-form-urlencoded|multipart/form-data"
    }},
    "submit_button": "CSS selector for submit button",
    "validation_required": ["email", "name"],
    "notes": "Additional notes about the form structure"
}}

Provide multiple CSS selectors for each field to increase detection success.
"""
    
    def _create_submission_strategy_prompt(self, form_data: Dict, generated_message: str, page_context: str) -> str:
        """Create the prompt for submission strategy"""
        return f"""
Given this form structure and generated message, determine the best submission strategy.

Form Data: {json.dumps(form_data, indent=2)}
Generated Message: {generated_message}
Page Context: {page_context}

Provide recommendations for:
1. Field mapping strategy
2. Submission method (form submit, AJAX, etc.)
3. Required fields and validation
4. Potential challenges and solutions
5. Fallback strategies if primary method fails

Return JSON with this structure:
{{
    "success": true/false,
    "strategy": "traditional|ajax|modal|alternative",
    "field_mapping_strategy": "exact|fuzzy|ai_guided",
    "submission_method": "form_submit|ajax_post|button_click",
    "required_fields": ["name", "email", "message"],
    "optional_fields": ["phone", "company", "subject"],
    "validation_approach": "client_side|server_side|both",
    "challenges": ["CAPTCHA", "dynamic_loading", "custom_validation"],
    "solutions": ["Use 2captcha", "Wait for dynamic content", "Handle validation errors"],
    "fallback_strategies": ["email_submission", "alternative_form", "contact_page"],
    "confidence": 0.0-1.0,
    "estimated_success_rate": 0.0-1.0
}}
"""
    
    def _parse_ai_response_robust(self, response_text: str, page_url: str) -> FormAnalysisResult:
        """Parse AI response using robust JSON parsing with multiple fallback strategies"""
        try:
            logger.info(f"🔍 Parsing AI response for {page_url}")
            
            # Expected structure for validation
            expected_structure = {
                'success': bool,
                'confidence_score': float,
                'form_elements': list,
                'contact_sections': list,
                'submission_methods': list,
                'field_mappings': dict,
                'alternative_contact_methods': list,
                'captcha_detected': bool,
                'captcha_type': str,
                'captcha_selectors': list,
                'captcha_site_key': str,
                'captcha_challenges': list
            }
            
            # Use robust JSON parser
            parse_result = self.json_parser.parse_ai_response(response_text, expected_structure)
            
            if not parse_result.success:
                logger.error(f"❌ All JSON parsing methods failed for {page_url}: {parse_result.error_message}")
                return FormAnalysisResult(
                    success=False,
                    confidence_score=0.0,
                    form_elements=[],
                    contact_sections=[],
                    submission_methods=[],
                    field_mappings={},
                    alternative_contact_methods=[],
                    error_message=f"JSON parsing failed: {parse_result.error_message}",
                    analysis_time=0.0
                )
            
            # Validate structure
            if not self.json_parser.validate_structure(parse_result.data, expected_structure):
                logger.warning(f"⚠️ Structure validation failed for {page_url}, using partial data")
            
            # Extract data with defaults
            data = parse_result.data or {}
            
            logger.info(f"✅ Successfully parsed AI response using {parse_result.method_used} (confidence: {parse_result.confidence})")
            
            return FormAnalysisResult(
                success=data.get('success', False),
                confidence_score=data.get('confidence_score', 0.0),
                form_elements=data.get('form_elements', []),
                contact_sections=data.get('contact_sections', []),
                submission_methods=data.get('submission_methods', []),
                field_mappings=data.get('field_mappings', {}),
                alternative_contact_methods=data.get('alternative_contact_methods', []),
                captcha_detected=data.get('captcha_detected', False),
                captcha_type=data.get('captcha_type'),
                captcha_selectors=data.get('captcha_selectors', []),
                captcha_site_key=data.get('captcha_site_key'),
                captcha_challenges=data.get('captcha_challenges', []),
                error_message=None
            )
            
        except Exception as e:
            logger.error(f"❌ Error in robust AI response parsing for {page_url}: {e}")
            return FormAnalysisResult(
                success=False,
                confidence_score=0.0,
                form_elements=[],
                contact_sections=[],
                submission_methods=[],
                field_mappings={},
                alternative_contact_methods=[],
                error_message=f"Robust parsing error: {str(e)}",
                analysis_time=0.0
            )

    def _parse_ai_response(self, response_text: str, page_url: str) -> FormAnalysisResult:
        """Parse the AI response for form analysis"""
        try:
            # Extract JSON from response
            json_start = response_text.find('{')
            json_end = response_text.rfind('}') + 1
            
            if json_start == -1 or json_end == 0:
                raise ValueError("No JSON found in AI response")
            
            json_str = response_text[json_start:json_end]
            data = json.loads(json_str)
            
            return FormAnalysisResult(
                success=data.get('success', False),
                confidence_score=data.get('confidence_score', 0.0),
                form_elements=data.get('form_elements', []),
                contact_sections=data.get('contact_sections', []),
                submission_methods=data.get('submission_methods', []),
                field_mappings=data.get('field_mappings', {}),
                alternative_contact_methods=data.get('alternative_contact_methods', []),
                captcha_detected=data.get('captcha_detected', False),
                captcha_type=data.get('captcha_type'),
                captcha_selectors=data.get('captcha_selectors', []),
                captcha_site_key=data.get('captcha_site_key'),
                captcha_challenges=data.get('captcha_challenges', []),
                error_message=None
            )
            
        except Exception as e:
            logger.error(f"Error parsing AI response for {page_url}: {e}")
            return FormAnalysisResult(
                success=False,
                confidence_score=0.0,
                form_elements=[],
                contact_sections=[],
                submission_methods=[],
                field_mappings={},
                alternative_contact_methods=[],
                error_message=f"Failed to parse AI response: {e}"
            )
    
    def _parse_field_mapping_response_robust(self, response_text: str) -> Dict[str, Any]:
        """Parse field mapping response with robust JSON parsing"""
        try:
            expected_structure = {
                'success': bool,
                'field_mappings': dict,
                'selectors': dict,
                'form_attributes': dict,
                'submit_button': str,
                'validation_required': list,
                'notes': str
            }
            
            parse_result = self.json_parser.parse_ai_response(response_text, expected_structure)
            
            if parse_result.success:
                return parse_result.data or {}
            else:
                logger.warning(f"Field mapping parsing failed: {parse_result.error_message}")
                return {
                    'success': False,
                    'field_mappings': {},
                    'selectors': {},
                    'error': parse_result.error_message
                }
                
        except Exception as e:
            logger.error(f"Error in robust field mapping parsing: {e}")
            return {
                'success': False,
                'field_mappings': {},
                'selectors': {},
                'error': str(e)
            }

    def _parse_submission_strategy_response_robust(self, response_text: str) -> Dict[str, Any]:
        """Parse submission strategy response with robust JSON parsing"""
        try:
            expected_structure = {
                'success': bool,
                'strategy': str,
                'field_mapping_strategy': str,
                'submission_method': str,
                'required_fields': list,
                'optional_fields': list,
                'validation_approach': str,
                'challenges': list,
                'solutions': list,
                'fallback_strategies': list,
                'confidence': float,
                'estimated_success_rate': float
            }
            
            parse_result = self.json_parser.parse_ai_response(response_text, expected_structure)
            
            if parse_result.success:
                return parse_result.data or {}
            else:
                logger.warning(f"Submission strategy parsing failed: {parse_result.error_message}")
                return {
                    'success': False,
                    'strategy': 'traditional',
                    'recommendations': [],
                    'error': parse_result.error_message
                }
                
        except Exception as e:
            logger.error(f"Error in robust submission strategy parsing: {e}")
            return {
                'success': False,
                'strategy': 'traditional',
                'recommendations': [],
                'error': str(e)
            }

    def _parse_field_mapping_response(self, response_text: str) -> Dict[str, Any]:
        """Parse the AI response for field mapping"""
        try:
            json_start = response_text.find('{')
            json_end = response_text.rfind('}') + 1
            
            if json_start == -1 or json_end == 0:
                raise ValueError("No JSON found in field mapping response")
            
            json_str = response_text[json_start:json_end]
            return json.loads(json_str)
            
        except Exception as e:
            logger.error(f"Error parsing field mapping response: {e}")
            return {
                'success': False,
                'field_mappings': {},
                'selectors': {},
                'error': str(e)
            }
    
    def _parse_submission_strategy_response(self, response_text: str) -> Dict[str, Any]:
        """Parse the AI response for submission strategy"""
        try:
            json_start = response_text.find('{')
            json_end = response_text.rfind('}') + 1
            
            if json_start == -1 or json_end == 0:
                raise ValueError("No JSON found in submission strategy response")
            
            json_str = response_text[json_start:json_end]
            return json.loads(json_str)
            
        except Exception as e:
            logger.error(f"Error parsing submission strategy response: {e}")
            return {
                'success': False,
                'strategy': 'traditional',
                'recommendations': [],
                'error': str(e)
            }
    
    def clear_cache(self):
        """Clear the analysis cache"""
        self.analysis_cache.clear()
        logger.info("Analysis cache cleared")
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        return {
            'cache_size': len(self.analysis_cache),
            'cache_keys': list(self.analysis_cache.keys())
        }
