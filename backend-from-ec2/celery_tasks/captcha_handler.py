"""
CAPTCHA Handling Module with 2captcha Integration
"""
import os
import time
import logging
from typing import Dict, Any, Optional
import requests
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

logger = logging.getLogger(__name__)

class CaptchaHandler:
    """Handle CAPTCHA challenges using 2captcha service"""
    
    def __init__(self):
        self.api_key = os.getenv('CAPTCHA_API_KEY')
        self.base_url = "http://2captcha.com/in.php"
        self.result_url = "http://2captcha.com/res.php"
        
    def detect_captcha(self, driver) -> Optional[Dict[str, Any]]:
        """
        Detect CAPTCHA on the current page
        """
        try:
            # Common CAPTCHA selectors
            captcha_selectors = [
                "iframe[src*='recaptcha']",
                "iframe[src*='captcha']",
                "div[class*='recaptcha']",
                "div[class*='captcha']",
                "img[src*='captcha']",
                "canvas[id*='captcha']"
            ]
            
            captcha_info = {}
            
            for selector in captcha_selectors:
                try:
                    elements = driver.find_elements(By.CSS_SELECTOR, selector)
                    if elements:
                        captcha_info['type'] = self._determine_captcha_type(selector)
                        captcha_info['element'] = elements[0]
                        captcha_info['selector'] = selector
                        break
                except:
                    continue
            
            if captcha_info:
                logger.info(f"CAPTCHA detected: {captcha_info['type']}")
                return captcha_info
            
            return None
            
        except Exception as e:
            logger.error(f"Error detecting CAPTCHA: {e}")
            return None
    
    def _determine_captcha_type(self, selector: str) -> str:
        """Determine CAPTCHA type based on selector"""
        if 'recaptcha' in selector.lower():
            return 'recaptcha'
        elif 'captcha' in selector.lower():
            return 'image_captcha'
        else:
            return 'unknown'
    
    def solve_recaptcha(self, site_key: str, page_url: str) -> Optional[str]:
        """
        Solve reCAPTCHA using 2captcha service
        """
        try:
            if not self.api_key:
                logger.warning("No CAPTCHA API key provided")
                return None
            
            # Submit CAPTCHA to 2captcha
            params = {
                'key': self.api_key,
                'method': 'userrecaptcha',
                'googlekey': site_key,
                'pageurl': page_url,
                'json': 1
            }
            
            response = requests.get(self.base_url, params=params)
            result = response.json()
            
            if result.get('status') != 1:
                logger.error(f"2captcha submission failed: {result}")
                return None
            
            captcha_id = result.get('request')
            logger.info(f"CAPTCHA submitted to 2captcha, ID: {captcha_id}")
            
            # Wait for solution
            solution = self._wait_for_solution(captcha_id)
            
            if solution:
                logger.info("CAPTCHA solved successfully")
                return solution
            else:
                logger.error("CAPTCHA solution failed")
                return None
                
        except Exception as e:
            logger.error(f"Error solving reCAPTCHA: {e}")
            return None
    
    def solve_image_captcha(self, image_url: str) -> Optional[str]:
        """
        Solve image CAPTCHA using 2captcha service
        """
        try:
            if not self.api_key:
                logger.warning("No CAPTCHA API key provided")
                return None
            
            # Download CAPTCHA image
            image_response = requests.get(image_url)
            if image_response.status_code != 200:
                logger.error(f"Failed to download CAPTCHA image: {image_response.status_code}")
                return None
            
            # Submit to 2captcha
            files = {'file': ('captcha.jpg', image_response.content)}
            data = {
                'key': self.api_key,
                'method': 'post',
                'json': 1
            }
            
            response = requests.post(self.base_url, files=files, data=data)
            result = response.json()
            
            if result.get('status') != 1:
                logger.error(f"2captcha image submission failed: {result}")
                return None
            
            captcha_id = result.get('request')
            logger.info(f"Image CAPTCHA submitted to 2captcha, ID: {captcha_id}")
            
            # Wait for solution
            solution = self._wait_for_solution(captcha_id)
            
            if solution:
                logger.info("Image CAPTCHA solved successfully")
                return solution
            else:
                logger.error("Image CAPTCHA solution failed")
                return None
                
        except Exception as e:
            logger.error(f"Error solving image CAPTCHA: {e}")
            return None
    
    def _wait_for_solution(self, captcha_id: str, max_wait: int = 120) -> Optional[str]:
        """
        Wait for CAPTCHA solution from 2captcha
        """
        start_time = time.time()
        
        while time.time() - start_time < max_wait:
            try:
                params = {
                    'key': self.api_key,
                    'action': 'get',
                    'id': captcha_id,
                    'json': 1
                }
                
                response = requests.get(self.result_url, params=params)
                result = response.json()
                
                if result.get('status') == 1:
                    return result.get('request')
                elif result.get('request') == 'CAPCHA_NOT_READY':
                    time.sleep(5)  # Wait 5 seconds before checking again
                    continue
                else:
                    logger.error(f"CAPTCHA solution failed: {result}")
                    return None
                    
            except Exception as e:
                logger.error(f"Error checking CAPTCHA solution: {e}")
                time.sleep(5)
                continue
        
        logger.error("CAPTCHA solution timeout")
        return None
    
    def handle_captcha_in_form(self, driver, captcha_info: Dict[str, Any]) -> bool:
        """
        Handle CAPTCHA in form submission
        """
        try:
            captcha_type = captcha_info.get('type')
            
            if captcha_type == 'recaptcha':
                return self._handle_recaptcha(driver, captcha_info)
            elif captcha_type == 'image_captcha':
                return self._handle_image_captcha(driver, captcha_info)
            else:
                logger.warning(f"Unknown CAPTCHA type: {captcha_type}")
                return False
                
        except Exception as e:
            logger.error(f"Error handling CAPTCHA: {e}")
            return False
    
    def _handle_recaptcha(self, driver, captcha_info: Dict[str, Any]) -> bool:
        """Handle reCAPTCHA"""
        try:
            # Find reCAPTCHA iframe
            iframe = driver.find_element(By.CSS_SELECTOR, "iframe[src*='recaptcha']")
            
            # Get site key from iframe src
            iframe_src = iframe.get_attribute('src')
            site_key = self._extract_site_key(iframe_src)
            
            if not site_key:
                logger.error("Could not extract reCAPTCHA site key")
                return False
            
            # Solve CAPTCHA
            solution = self.solve_recaptcha(site_key, driver.current_url)
            
            if not solution:
                return False
            
            # Execute JavaScript to set reCAPTCHA response
            script = f"""
            document.querySelector('[name="g-recaptcha-response"]').value = '{solution}';
            """
            driver.execute_script(script)
            
            logger.info("reCAPTCHA response set successfully")
            return True
            
        except Exception as e:
            logger.error(f"Error handling reCAPTCHA: {e}")
            return False
    
    def _handle_image_captcha(self, driver, captcha_info: Dict[str, Any]) -> bool:
        """Handle image CAPTCHA"""
        try:
            # Find CAPTCHA image
            captcha_img = driver.find_element(By.CSS_SELECTOR, "img[src*='captcha']")
            image_url = captcha_img.get_attribute('src')
            
            if not image_url:
                logger.error("Could not get CAPTCHA image URL")
                return False
            
            # Solve CAPTCHA
            solution = self.solve_image_captcha(image_url)
            
            if not solution:
                return False
            
            # Find input field and fill solution
            input_field = driver.find_element(By.CSS_SELECTOR, "input[name*='captcha'], input[id*='captcha']")
            input_field.clear()
            input_field.send_keys(solution)
            
            logger.info("Image CAPTCHA solution entered successfully")
            return True
            
        except Exception as e:
            logger.error(f"Error handling image CAPTCHA: {e}")
            return False
    
    def _extract_site_key(self, iframe_src: str) -> Optional[str]:
        """Extract reCAPTCHA site key from iframe src"""
        try:
            import re
            match = re.search(r'k=([^&]+)', iframe_src)
            if match:
                return match.group(1)
            return None
        except:
            return None

# Global CAPTCHA handler instance
captcha_handler = None

def get_captcha_handler() -> CaptchaHandler:
    """Get or create CAPTCHA handler instance"""
    global captcha_handler
    if captcha_handler is None:
        captcha_handler = CaptchaHandler()
    return captcha_handler 