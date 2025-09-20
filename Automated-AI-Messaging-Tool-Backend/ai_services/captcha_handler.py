"""
AI-Powered CAPTCHA Detection and Solving Service
Handles various types of CAPTCHAs including reCAPTCHA, hCaptcha, and custom CAPTCHAs
"""

import os
import json
import logging
import time
import requests
import base64
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from selenium.webdriver.firefox.service import Service as FirefoxService
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
import google.generativeai as genai

logger = logging.getLogger(__name__)

@dataclass
class CaptchaResult:
    """Result of CAPTCHA solving attempt"""
    success: bool
    captcha_type: str
    solution: Optional[str] = None
    confidence: float = 0.0
    error_message: Optional[str] = None
    solving_time: float = 0.0
    method_used: str = "unknown"

class CaptchaHandler:
    """AI-powered CAPTCHA detection and solving"""
    
    def __init__(self):
        """Initialize CAPTCHA handler with AI and solving services"""
        self.gemini_api_key = os.getenv('GEMINI_API_KEY')
        if self.gemini_api_key:
            genai.configure(api_key=self.gemini_api_key)
            self.gemini_model = genai.GenerativeModel('gemini-1.5-pro')
        
        # CAPTCHA solving service API keys (optional)
        self.two_captcha_api_key = os.getenv('TWO_CAPTCHA_API_KEY')
        self.anticaptcha_api_key = os.getenv('ANTICAPTCHA_API_KEY')
        self.capmonster_api_key = os.getenv('CAPMONSTER_API_KEY')
        
        # CAPTCHA detection patterns
        self.captcha_patterns = {
            'recaptcha_v2': [
                '.g-recaptcha',
                '[data-sitekey]',
                'iframe[src*="recaptcha"]',
                '.recaptcha-checkbox'
            ],
            'recaptcha_v3': [
                '[data-sitekey]',
                'script[src*="recaptcha"]',
                '.grecaptcha-badge'
            ],
            'hcaptcha': [
                '.h-captcha',
                '[data-sitekey]',
                'iframe[src*="hcaptcha"]'
            ],
            'cloudflare': [
                '.cf-turnstile',
                '[data-sitekey]',
                'iframe[src*="challenges.cloudflare.com"]'
            ],
            'custom': [
                '#captcha',
                '.captcha',
                'input[name*="captcha"]',
                'img[src*="captcha"]'
            ]
        }
    
    def detect_captcha(self, page_html: str, page_url: str) -> Dict[str, Any]:
        """
        Detect CAPTCHA presence and type using AI analysis
        
        Args:
            page_html: HTML content of the page
            page_url: URL of the page
            
        Returns:
            Dictionary with CAPTCHA detection results
        """
        try:
            logger.info(f"🔍 Detecting CAPTCHA on {page_url}")
            
            # Use AI to analyze page for CAPTCHAs
            if self.gemini_api_key:
                ai_result = self._detect_captcha_with_ai(page_html, page_url)
                if ai_result['success']:
                    return ai_result
            
            # Fallback to pattern matching
            return self._detect_captcha_patterns(page_html, page_url)
            
        except Exception as e:
            logger.error(f"Error detecting CAPTCHA on {page_url}: {e}")
            return {
                'success': False,
                'captcha_detected': False,
                'captcha_type': None,
                'error': str(e)
            }
    
    def solve_captcha(self, captcha_info: Dict, driver: webdriver = None) -> CaptchaResult:
        """
        Solve detected CAPTCHA using appropriate method
        
        Args:
            captcha_info: CAPTCHA detection information
            driver: Optional Selenium driver for interactive solving
            
        Returns:
            CaptchaResult with solving details
        """
        start_time = time.time()
        captcha_type = captcha_info.get('captcha_type')
        
        try:
            logger.info(f"🧩 Solving {captcha_type} CAPTCHA")
            
            if captcha_type == 'recaptcha_v2':
                return self._solve_recaptcha_v2(captcha_info, driver)
            elif captcha_type == 'recaptcha_v3':
                return self._solve_recaptcha_v3(captcha_info, driver)
            elif captcha_type == 'hcaptcha':
                return self._solve_hcaptcha(captcha_info, driver)
            elif captcha_type == 'cloudflare':
                return self._solve_cloudflare(captcha_info, driver)
            elif captcha_type == 'custom':
                return self._solve_custom_captcha(captcha_info, driver)
            else:
                return CaptchaResult(
                    success=False,
                    captcha_type=captcha_type or 'unknown',
                    error_message=f"Unsupported CAPTCHA type: {captcha_type}",
                    solving_time=time.time() - start_time
                )
                
        except Exception as e:
            logger.error(f"Error solving CAPTCHA: {e}")
            return CaptchaResult(
                success=False,
                captcha_type=captcha_type or 'unknown',
                error_message=str(e),
                solving_time=time.time() - start_time
            )
    
    def _detect_captcha_with_ai(self, page_html: str, page_url: str) -> Dict[str, Any]:
        """Use AI to detect CAPTCHAs"""
        try:
            prompt = f"""
            Analyze this webpage HTML and detect any CAPTCHA systems present.
            
            URL: {page_url}
            HTML Content: {page_html[:4000]}...
            
            Look for:
            1. reCAPTCHA v2 (checkbox, "I'm not a robot")
            2. reCAPTCHA v3 (invisible, score-based)
            3. hCaptcha (checkbox alternative)
            4. Cloudflare Turnstile
            5. Custom CAPTCHA images
            6. Math problems or text challenges
            7. Audio challenges
            
            Return JSON:
            {{
                "success": true/false,
                "captcha_detected": true/false,
                "captcha_type": "recaptcha_v2|recaptcha_v3|hcaptcha|cloudflare|custom|none",
                "captcha_selectors": ["CSS selectors for CAPTCHA elements"],
                "captcha_site_key": "site key if found",
                "captcha_challenges": ["types of challenges present"],
                "confidence": 0.0-1.0,
                "recommendations": ["solving strategy recommendations"]
            }}
            """
            
            response = self.gemini_model.generate_content(prompt)
            
            # Parse AI response
            json_start = response.text.find('{')
            json_end = response.text.rfind('}') + 1
            
            if json_start != -1 and json_end > 0:
                json_str = response.text[json_start:json_end]
                result = json.loads(json_str)
                result['success'] = True
                return result
            
        except Exception as e:
            logger.error(f"AI CAPTCHA detection failed: {e}")
        
        return {'success': False, 'captcha_detected': False}
    
    def _detect_captcha_patterns(self, page_html: str, page_url: str) -> Dict[str, Any]:
        """Detect CAPTCHAs using pattern matching"""
        from bs4 import BeautifulSoup
        
        soup = BeautifulSoup(page_html, 'html.parser')
        detected_captchas = []
        
        for captcha_type, selectors in self.captcha_patterns.items():
            for selector in selectors:
                elements = soup.select(selector)
                if elements:
                    detected_captchas.append({
                        'type': captcha_type,
                        'selector': selector,
                        'count': len(elements)
                    })
        
        if detected_captchas:
            # Get the most common type
            captcha_type = max(set(c['type'] for c in detected_captchas), 
                             key=[c['type'] for c in detected_captchas].count)
            
            return {
                'success': True,
                'captcha_detected': True,
                'captcha_type': captcha_type,
                'captcha_selectors': [c['selector'] for c in detected_captchas if c['type'] == captcha_type],
                'confidence': 0.8,
                'detected_captchas': detected_captchas
            }
        
        return {
            'success': True,
            'captcha_detected': False,
            'captcha_type': None,
            'confidence': 0.9
        }
    
    def _solve_recaptcha_v2(self, captcha_info: Dict, driver: webdriver) -> CaptchaResult:
        """Solve reCAPTCHA v2 using 2captcha service"""
        start_time = time.time()
        
        try:
            if not self.two_captcha_api_key:
                return CaptchaResult(
                    success=False,
                    captcha_type='recaptcha_v2',
                    error_message="2captcha API key not configured",
                    solving_time=time.time() - start_time
                )
            
            site_key = captcha_info.get('captcha_site_key')
            if not site_key:
                return CaptchaResult(
                    success=False,
                    captcha_type='recaptcha_v2',
                    error_message="reCAPTCHA site key not found",
                    solving_time=time.time() - start_time
                )
            
            # Submit CAPTCHA to 2captcha
            submit_data = {
                'key': self.two_captcha_api_key,
                'method': 'userrecaptcha',
                'googlekey': site_key,
                'pageurl': captcha_info.get('page_url', ''),
                'json': 1
            }
            
            response = requests.post('http://2captcha.com/in.php', data=submit_data)
            result = response.json()
            
            if result.get('status') != 1:
                return CaptchaResult(
                    success=False,
                    captcha_type='recaptcha_v2',
                    error_message=f"2captcha submission failed: {result.get('error_text')}",
                    solving_time=time.time() - start_time
                )
            
            captcha_id = result['request']
            
            # Wait for solution
            for _ in range(30):  # Wait up to 5 minutes
                time.sleep(10)
                
                check_response = requests.get(
                    f'http://2captcha.com/res.php?key={self.two_captcha_api_key}&action=get&id={captcha_id}&json=1'
                )
                check_result = check_response.json()
                
                if check_result.get('status') == 1:
                    solution = check_result.get('request')
                    
                    # Inject solution into page
                    if driver:
                        driver.execute_script(f"""
                            document.getElementById('g-recaptcha-response').innerHTML = '{solution}';
                        """)
                    
                    return CaptchaResult(
                        success=True,
                        captcha_type='recaptcha_v2',
                        solution=solution,
                        confidence=0.9,
                        solving_time=time.time() - start_time,
                        method_used='2captcha_service'
                    )
                elif check_result.get('error_text'):
                    return CaptchaResult(
                        success=False,
                        captcha_type='recaptcha_v2',
                        error_message=f"2captcha solving failed: {check_result.get('error_text')}",
                        solving_time=time.time() - start_time
                    )
            
            return CaptchaResult(
                success=False,
                captcha_type='recaptcha_v2',
                error_message="2captcha timeout - solution not received",
                solving_time=time.time() - start_time
            )
            
        except Exception as e:
            return CaptchaResult(
                success=False,
                captcha_type='recaptcha_v2',
                error_message=str(e),
                solving_time=time.time() - start_time
            )
    
    def _solve_recaptcha_v3(self, captcha_info: Dict, driver: webdriver) -> CaptchaResult:
        """Solve reCAPTCHA v3 (invisible)"""
        start_time = time.time()
        
        try:
            # reCAPTCHA v3 is usually handled automatically by the page
            # We just need to wait for it to complete
            if driver:
                # Wait for reCAPTCHA to complete
                WebDriverWait(driver, 10).until(
                    lambda d: d.execute_script("return typeof grecaptcha !== 'undefined'")
                )
                
                # Trigger reCAPTCHA execution
                driver.execute_script("""
                    if (typeof grecaptcha !== 'undefined' && grecaptcha.execute) {
                        grecaptcha.execute();
                    }
                """)
                
                time.sleep(2)  # Wait for execution
                
                return CaptchaResult(
                    success=True,
                    captcha_type='recaptcha_v3',
                    solution='executed',
                    confidence=0.8,
                    solving_time=time.time() - start_time,
                    method_used='automatic_execution'
                )
            
            return CaptchaResult(
                success=False,
                captcha_type='recaptcha_v3',
                error_message="No driver provided for reCAPTCHA v3",
                solving_time=time.time() - start_time
            )
            
        except Exception as e:
            return CaptchaResult(
                success=False,
                captcha_type='recaptcha_v3',
                error_message=str(e),
                solving_time=time.time() - start_time
            )
    
    def _solve_hcaptcha(self, captcha_info: Dict, driver: webdriver) -> CaptchaResult:
        """Solve hCaptcha using 2captcha service"""
        start_time = time.time()
        
        try:
            if not self.two_captcha_api_key:
                return CaptchaResult(
                    success=False,
                    captcha_type='hcaptcha',
                    error_message="2captcha API key not configured",
                    solving_time=time.time() - start_time
                )
            
            site_key = captcha_info.get('captcha_site_key')
            if not site_key:
                return CaptchaResult(
                    success=False,
                    captcha_type='hcaptcha',
                    error_message="hCaptcha site key not found",
                    solving_time=time.time() - start_time
                )
            
            # Submit to 2captcha
            submit_data = {
                'key': self.two_captcha_api_key,
                'method': 'hcaptcha',
                'sitekey': site_key,
                'pageurl': captcha_info.get('page_url', ''),
                'json': 1
            }
            
            response = requests.post('http://2captcha.com/in.php', data=submit_data)
            result = response.json()
            
            if result.get('status') != 1:
                return CaptchaResult(
                    success=False,
                    captcha_type='hcaptcha',
                    error_message=f"2captcha hCaptcha submission failed: {result.get('error_text')}",
                    solving_time=time.time() - start_time
                )
            
            captcha_id = result['request']
            
            # Wait for solution
            for _ in range(30):
                time.sleep(10)
                
                check_response = requests.get(
                    f'http://2captcha.com/res.php?key={self.two_captcha_api_key}&action=get&id={captcha_id}&json=1'
                )
                check_result = check_response.json()
                
                if check_result.get('status') == 1:
                    solution = check_result.get('request')
                    
                    # Inject solution
                    if driver:
                        driver.execute_script(f"""
                            document.querySelector('[name="h-captcha-response"]').value = '{solution}';
                        """)
                    
                    return CaptchaResult(
                        success=True,
                        captcha_type='hcaptcha',
                        solution=solution,
                        confidence=0.9,
                        solving_time=time.time() - start_time,
                        method_used='2captcha_service'
                    )
                elif check_result.get('error_text'):
                    return CaptchaResult(
                        success=False,
                        captcha_type='hcaptcha',
                        error_message=f"2captcha hCaptcha solving failed: {check_result.get('error_text')}",
                        solving_time=time.time() - start_time
                    )
            
            return CaptchaResult(
                success=False,
                captcha_type='hcaptcha',
                error_message="2captcha hCaptcha timeout",
                solving_time=time.time() - start_time
            )
            
        except Exception as e:
            return CaptchaResult(
                success=False,
                captcha_type='hcaptcha',
                error_message=str(e),
                solving_time=time.time() - start_time
            )
    
    def _solve_cloudflare(self, captcha_info: Dict, driver: webdriver) -> CaptchaResult:
        """Solve Cloudflare Turnstile"""
        start_time = time.time()
        
        try:
            if driver:
                # Cloudflare Turnstile usually auto-solves
                # Wait for it to complete
                WebDriverWait(driver, 15).until(
                    lambda d: d.execute_script("""
                        return document.querySelector('.cf-turnstile') !== null;
                    """)
                )
                
                time.sleep(3)  # Wait for auto-solve
                
                return CaptchaResult(
                    success=True,
                    captcha_type='cloudflare',
                    solution='auto_solved',
                    confidence=0.7,
                    solving_time=time.time() - start_time,
                    method_used='auto_solve'
                )
            
            return CaptchaResult(
                success=False,
                captcha_type='cloudflare',
                error_message="No driver provided for Cloudflare",
                solving_time=time.time() - start_time
            )
            
        except Exception as e:
            return CaptchaResult(
                success=False,
                captcha_type='cloudflare',
                error_message=str(e),
                solving_time=time.time() - start_time
            )
    
    def _solve_custom_captcha(self, captcha_info: Dict, driver: webdriver) -> CaptchaResult:
        """Solve custom CAPTCHAs using AI image recognition"""
        start_time = time.time()
        
        try:
            if not driver:
                return CaptchaResult(
                    success=False,
                    captcha_type='custom',
                    error_message="Driver required for custom CAPTCHA solving",
                    solving_time=time.time() - start_time
                )
            
            # Find CAPTCHA image
            captcha_img = None
            for selector in captcha_info.get('captcha_selectors', []):
                try:
                    captcha_img = driver.find_element(By.CSS_SELECTOR, selector)
                    break
                except:
                    continue
            
            if not captcha_img:
                return CaptchaResult(
                    success=False,
                    captcha_type='custom',
                    error_message="CAPTCHA image not found",
                    solving_time=time.time() - start_time
                )
            
            # Get image data
            img_src = captcha_img.get_attribute('src')
            if not img_src:
                return CaptchaResult(
                    success=False,
                    captcha_type='custom',
                    error_message="CAPTCHA image source not found",
                    solving_time=time.time() - start_time
                )
            
            # Use AI to solve the CAPTCHA
            if self.gemini_api_key:
                solution = self._solve_captcha_with_ai(img_src)
                if solution:
                    # Enter solution
                    input_field = driver.find_element(By.CSS_SELECTOR, 'input[name*="captcha"]')
                    input_field.clear()
                    input_field.send_keys(solution)
                    
                    return CaptchaResult(
                        success=True,
                        captcha_type='custom',
                        solution=solution,
                        confidence=0.6,
                        solving_time=time.time() - start_time,
                        method_used='ai_image_recognition'
                    )
            
            return CaptchaResult(
                success=False,
                captcha_type='custom',
                error_message="AI CAPTCHA solving not available",
                solving_time=time.time() - start_time
            )
            
        except Exception as e:
            return CaptchaResult(
                success=False,
                captcha_type='custom',
                error_message=str(e),
                solving_time=time.time() - start_time
            )
    
    def _solve_captcha_with_ai(self, image_src: str) -> Optional[str]:
        """Use AI to solve CAPTCHA image"""
        try:
            # Download image
            response = requests.get(image_src)
            image_data = response.content
            
            # Convert to base64
            image_b64 = base64.b64encode(image_data).decode()
            
            # Use Gemini to solve
            prompt = f"""
            Analyze this CAPTCHA image and provide the text or solution.
            Return only the solution text, nothing else.
            
            Image: data:image/png;base64,{image_b64}
            """
            
            response = self.gemini_model.generate_content(prompt)
            solution = response.text.strip()
            
            if solution and len(solution) > 0:
                return solution
            
        except Exception as e:
            logger.error(f"AI CAPTCHA solving failed: {e}")
        
        return None
    
    def get_captcha_solving_strategies(self, captcha_type: str) -> List[str]:
        """Get recommended solving strategies for CAPTCHA type"""
        strategies = {
            'recaptcha_v2': [
                'Use 2captcha service for checkbox solving',
                'Try invisible reCAPTCHA bypass',
                'Use residential proxies for better success rates'
            ],
            'recaptcha_v3': [
                'Wait for automatic execution',
                'Trigger grecaptcha.execute() manually',
                'Use high-quality residential proxies'
            ],
            'hcaptcha': [
                'Use 2captcha hCaptcha service',
                'Try alternative solving services',
                'Use mobile user agents'
            ],
            'cloudflare': [
                'Wait for auto-solve (usually works)',
                'Use Cloudflare bypass techniques',
                'Try different browser configurations'
            ],
            'custom': [
                'Use AI image recognition (Gemini)',
                'Try OCR services',
                'Use manual solving services'
            ]
        }
        
        return strategies.get(captcha_type, ['Unknown CAPTCHA type'])
