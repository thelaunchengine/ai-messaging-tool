"""
Celery tasks for website scraping with real data extraction
"""
from dotenv import load_dotenv
load_dotenv()
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from celery import current_task
from celery_app import celery_app
import time
import logging
from datetime import datetime
from typing import List, Dict, Any, Optional, Tuple
from database.database_manager import DatabaseManager
import asyncio
import aiohttp
import json
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import re
import random
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

logger = logging.getLogger(__name__)

# Import the generate_messages_task to fix the scope issue
# This will be imported when needed to avoid circular imports

# Configuration for testing limits
# TESTING_MODE_ENABLED: Set to 'true' to enable testing mode with limited AI message generation
# MAX_AI_MESSAGES_PER_FILE: Maximum number of AI messages to generate per CSV file (default: 2)
# 
# Environment Variables:
# - TESTING_MODE_ENABLED=true/false (default: true)
# - MAX_AI_MESSAGES_PER_FILE=2 (default: 2)
#
# Example:
# export TESTING_MODE_ENABLED=true
# export MAX_AI_MESSAGES_PER_FILE=5

MAX_AI_MESSAGES_PER_FILE = int(os.getenv('MAX_AI_MESSAGES_PER_FILE', '2'))
TESTING_MODE_ENABLED = os.getenv('TESTING_MODE_ENABLED', 'true').lower() == 'true'

logger.info(f"Testing mode enabled: {TESTING_MODE_ENABLED}")
logger.info(f"Maximum AI messages per file: {MAX_AI_MESSAGES_PER_FILE}")

class RobustWebScraper:
    """Comprehensive web scraper with robust error handling"""
    
    def __init__(self):
        self.session = self._create_robust_session()
        self.max_retries = 3
        self.backoff_factor = 2
    
    def _create_robust_session(self):
        """Create a session with robust error handling"""
        
        session = requests.Session()
        
        # Configure retry strategy
        retry_strategy = Retry(
            total=3,
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["HEAD", "GET", "OPTIONS"],
            backoff_factor=1,
            raise_on_status=False
        )
        
        adapter = HTTPAdapter(max_retries=retry_strategy)
        session.mount("http://", adapter)
        session.mount("https://", adapter)
        
        # Set headers to avoid detection
        session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        })
        
        return session
    
    def scrape_with_error_handling(self, url: str) -> Dict[str, Any]:
        """Scrape website with comprehensive error handling"""
        
        error_attempts = 0
        last_error = None
        
        while error_attempts < self.max_retries:
            try:
                # Add random delay to avoid overwhelming servers
                time.sleep(random.uniform(1, 3))
                
                # Attempt to scrape
                response = self.session.get(url, timeout=30)
                response.raise_for_status()
                
                return {
                    'success': True,
                    'content': response.text,
                    'status_code': response.status_code,
                    'url': url
                }
                
            except requests.exceptions.ConnectionError as e:
                last_error = f"Connection Error: {str(e)}"
                logger.warning(f"Connection error for {url}: {e}")
                
                # Handle specific connection errors
                if "Connection refused" in str(e):
                    return self._handle_connection_refused(url, error_attempts)
                elif "Max retries exceeded" in str(e):
                    return self._handle_max_retries_exceeded(url, error_attempts)
                elif "Name or service not known" in str(e):
                    return self._handle_dns_error(url, error_attempts)
                
            except requests.exceptions.Timeout as e:
                last_error = f"Timeout Error: {str(e)}"
                logger.warning(f"Timeout error for {url}: {e}")
                
            except requests.exceptions.SSLError as e:
                last_error = f"SSL Error: {str(e)}"
                logger.warning(f"SSL error for {url}: {e}")
                
            except requests.exceptions.HTTPError as e:
                last_error = f"HTTP Error: {str(e)}"
                logger.warning(f"HTTP error for {url}: {e}")
                
            except Exception as e:
                last_error = f"Unexpected Error: {str(e)}"
                logger.error(f"Unexpected error for {url}: {e}")
            
            error_attempts += 1
            
            # Exponential backoff
            if error_attempts < self.max_retries:
                wait_time = self.backoff_factor ** error_attempts
                logger.info(f"Retrying {url} in {wait_time} seconds...")
                time.sleep(wait_time)
        
        return {
            'success': False,
            'error': last_error,
            'url': url,
            'attempts': error_attempts
        }
    
    def _handle_connection_refused(self, url: str, attempt: int) -> Dict[str, Any]:
        """Handle connection refused errors"""
        
        strategies = [
            # Strategy 1: Try HTTP instead of HTTPS
            lambda: self._try_http_fallback(url),
            
            # Strategy 2: Try with different port
            lambda: self._try_port_variations(url),
            
            # Strategy 3: Try with different User-Agent
            lambda: self._try_different_user_agent(url),
            
            # Strategy 4: Try with proxy
            lambda: self._try_with_proxy(url)
        ]
        
        for strategy in strategies:
            try:
                result = strategy()
                if result['success']:
                    return result
            except Exception as e:
                logger.warning(f"Strategy failed: {e}")
                continue
        
        return {
            'success': False,
            'error': f"Connection refused after {attempt + 1} attempts",
            'url': url
        }
    
    def _handle_max_retries_exceeded(self, url: str, attempt: int) -> Dict[str, Any]:
        """Handle max retries exceeded errors"""
        
        # Try with longer timeout
        try:
            response = self.session.get(url, timeout=60)
            response.raise_for_status()
            return {
                'success': True,
                'content': response.text,
                'status_code': response.status_code,
                'url': url
            }
        except Exception as e:
            return {
                'success': False,
                'error': f"Max retries exceeded: {str(e)}",
                'url': url
            }
    
    def _handle_dns_error(self, url: str, attempt: int) -> Dict[str, Any]:
        """Handle DNS resolution errors"""
        
        # Try to resolve domain manually
        try:
            import socket
            from urllib.parse import urlparse
            
            parsed_url = urlparse(url)
            domain = parsed_url.netloc
            
            # Try to resolve IP
            ip = socket.gethostbyname(domain)
            
            # Try with IP instead of domain
            new_url = url.replace(domain, ip)
            response = self.session.get(new_url, timeout=30)
            response.raise_for_status()
            
            return {
                'success': True,
                'content': response.text,
                'status_code': response.status_code,
                'url': new_url
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f"DNS resolution failed: {str(e)}",
                'url': url
            }
    
    def _try_http_fallback(self, url: str) -> Dict[str, Any]:
        """Try HTTP if HTTPS fails"""
        
        if url.startswith('https://'):
            http_url = url.replace('https://', 'http://')
            try:
                response = self.session.get(http_url, timeout=30)
                response.raise_for_status()
                return {
                    'success': True,
                    'content': response.text,
                    'status_code': response.status_code,
                    'url': http_url
                }
            except Exception as e:
                return {'success': False, 'error': str(e)}
        
        return {'success': False, 'error': 'Not HTTPS URL'}
    
    def _try_port_variations(self, url: str) -> Dict[str, Any]:
        """Try different ports if default fails"""
        
        from urllib.parse import urlparse
        
        parsed_url = urlparse(url)
        domain = parsed_url.netloc
        path = parsed_url.path
        
        # Common ports to try
        ports = [80, 443, 8080, 8443]
        
        for port in ports:
            try:
                if port == 443:
                    test_url = f"https://{domain}:{port}{path}"
                else:
                    test_url = f"http://{domain}:{port}{path}"
                
                response = self.session.get(test_url, timeout=15)
                response.raise_for_status()
                
                return {
                    'success': True,
                    'content': response.text,
                    'status_code': response.status_code,
                    'url': test_url
                }
                
            except Exception:
                continue
        
        return {'success': False, 'error': 'All ports failed'}
    
    def _try_different_user_agent(self, url: str) -> Dict[str, Any]:
        """Try with different User-Agent"""
        
        user_agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36',
            'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36',
            'Mozilla/5.0 (iPhone; CPU iPhone OS 14_7_1 like Mac OS X) AppleWebKit/605.1.15'
        ]
        
        original_ua = self.session.headers.get('User-Agent')
        
        for ua in user_agents:
            try:
                self.session.headers.update({'User-Agent': ua})
                response = self.session.get(url, timeout=30)
                response.raise_for_status()
                
                return {
                    'success': True,
                    'content': response.text,
                    'status_code': response.status_code,
                    'url': url
                }
                
            except Exception:
                continue
        
        # Restore original User-Agent
        self.session.headers.update({'User-Agent': original_ua})
        return {'success': False, 'error': 'All User-Agents failed'}
    
    def _try_with_proxy(self, url: str) -> Dict[str, Any]:
        """Try with proxy if direct connection fails"""
        
        # For now, return failure (proxy implementation can be added later)
        return {'success': False, 'error': 'Proxy not implemented'}

def validate_website_url(url: str) -> bool:
    """Validate website URL format"""
    try:
        # Basic URL validation
        parsed = urlparse(url)
        
        # Must have scheme and netloc
        if not parsed.scheme or not parsed.netloc:
            return False
        
        # Must be HTTP/HTTPS
        if parsed.scheme not in ['http', 'https']:
            return False
        
        # Must have valid domain
        if len(parsed.netloc.split('.')) < 2:
            return False
        
        return True
        
    except Exception:
        return False

def handle_network_errors(url: str, max_retries: int = 3) -> Dict:
    """Handle network-related errors with retry logic"""
    for attempt in range(max_retries):
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.5',
                'Accept-Encoding': 'gzip, deflate',
                'Connection': 'keep-alive',
                'Upgrade-Insecure-Requests': '1',
            }
            
            response = requests.get(url, timeout=15, headers=headers, allow_redirects=True)
            response.raise_for_status()
            return {'success': True, 'content': response.text}
            
        except requests.exceptions.Timeout:
            logger.warning(f"Timeout error for {url}, attempt {attempt + 1}")
            if attempt < max_retries - 1:
                time.sleep(2 ** attempt)  # Exponential backoff
                continue
            return {'success': False, 'error': 'Timeout'}
            
        except requests.exceptions.ConnectionError:
            logger.warning(f"Connection error for {url}, attempt {attempt + 1}")
            if attempt < max_retries - 1:
                time.sleep(2 ** attempt)
                continue
            return {'success': False, 'error': 'Connection Error'}
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Request error for {url}: {str(e)}")
            return {'success': False, 'error': f'Request Error: {str(e)}'}
    
    return {'success': False, 'error': 'Max retries exceeded'}

def handle_parsing_errors(html_content: str, url: str) -> Dict:
    """Handle HTML parsing errors gracefully"""
    try:
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # Check if page is valid
        if not soup.find('html'):
            return {'success': False, 'error': 'Invalid HTML structure'}
        
        # Check for common error pages
        error_indicators = [
            '404 not found',
            'page not found',
            'access denied',
            'forbidden',
            'server error',
            'maintenance'
        ]
        
        page_text = soup.get_text().lower()
        for indicator in error_indicators:
            if indicator in page_text:
                return {'success': False, 'error': f'Error page detected: {indicator}'}
        
        return {'success': True, 'soup': soup}
        
    except Exception as e:
        logger.error(f"Parsing error for {url}: {str(e)}")
        return {'success': False, 'error': f'Parsing Error: {str(e)}'}

def select_best_contact_form(all_contact_options: List[Dict]) -> Dict:
    """Select the best contact form from multiple options"""
    if not all_contact_options:
        return None
    
    # Sort by priority first, then by score
    all_contact_options.sort(key=lambda x: (x['priority'], -x['score']))
    
    # Select the best option
    best_contact = all_contact_options[0]
    
    # Log all options for debugging
    logger.info(f"Found {len(all_contact_options)} contact options:")
    for i, option in enumerate(all_contact_options[:5]):
        logger.info(f"  {i+1}. {option['type']}: {option['text'][:50]} (score: {option['score']})")
    
    return best_contact

def extract_company_info(html: str, base_url: str) -> Dict[str, Any]:
    """
    Extract company information from website HTML
    """
    soup = BeautifulSoup(html, 'html.parser')
    
    # Title
    title = None
    if soup.title and soup.title.string:
        title = soup.title.string.strip()
    
    # Company Name (try multiple sources)
    companyName = None
    
    # Try og:site_name first
    meta_site_name = soup.find('meta', property='og:site_name')
    if meta_site_name and meta_site_name.get('content'):
        companyName = meta_site_name['content'].strip()
    
    # Try og:title
    if not companyName:
        meta_title = soup.find('meta', property='og:title')
        if meta_title and meta_title.get('content'):
            companyName = meta_title['content'].strip()
    
    # Try application-name
    if not companyName:
        meta_app_name = soup.find('meta', attrs={'name': 'application-name'})
        if meta_app_name and meta_app_name.get('content'):
            companyName = meta_app_name['content'].strip()
    
    # Try title tag with better cleaning
    if not companyName and title:
        # Clean up title more aggressively
        cleaned_title = title
        
        # Remove "Find a X Agent in Y, Z" patterns first
        cleaned_title = re.sub(r'^Find a [^|]+Agent in [^|]+\s*[-|]\s*', '', cleaned_title, flags=re.IGNORECASE)
        
        # Remove common business category prefixes
        cleaned_title = re.sub(r'^(Used Cars|New Cars|Auto Sales|Car Dealership|Auto Dealership)\s*[-|]\s*', '', cleaned_title, flags=re.IGNORECASE)
        
        # Remove common location patterns
        cleaned_title = re.sub(r'\s*[-|]\s*[A-Za-z\s,]+(?:NM|CA|TX|NY|FL|IL|PA|OH|GA|NC|MI|NJ|VA|WA|AZ|CO|TN|IN|MO|MD|MN|WI|AL|SC|LA|KY|OR|OK|CT|IA|MS|AR|KS|UT|NV|WV|NE|ID|HI|NH|ME|MT|RI|DE|SD|ND|AK|VT|WY)\s*[-|]?', '', cleaned_title, flags=re.IGNORECASE)
        
        # Remove city, state patterns at the beginning
        cleaned_title = re.sub(r'^[A-Za-z\s,]+(?:NM|CA|TX|NY|FL|IL|PA|OH|GA|NC|MI|NJ|VA|WA|AZ|CO|TN|IN|MO|MD|MN|WI|AL|SC|LA|KY|OR|OK|CT|IA|MS|AR|KS|UT|NV|WV|NE|ID|HI|NH|ME|MT|RI|DE|SD|ND|AK|VT|WY)\s*[-|]\s*', '', cleaned_title, flags=re.IGNORECASE)
        
        # Remove common suffixes
        cleaned_title = re.sub(r'\s*[-|]\s*(Home|Welcome|Official Site|Official Website|Dealership|Auto|Cars).*$', '', cleaned_title, flags=re.IGNORECASE)
        
        # Remove "Welcome to" prefixes
        cleaned_title = re.sub(r'^Welcome to\s+', '', cleaned_title, flags=re.IGNORECASE)
        
        # Remove "Official Site" and similar
        cleaned_title = re.sub(r'\s*[-|]\s*Official Site.*$', '', cleaned_title, flags=re.IGNORECASE)
        
        # Remove extra separators and clean up
        cleaned_title = re.sub(r'\s*[-|]\s*$', '', cleaned_title)
        cleaned_title = re.sub(r'^\s*[-|]\s*', '', cleaned_title)
        cleaned_title = cleaned_title.strip()
        
        # Only use if it looks like a company name (not too long, not just location)
        if cleaned_title and len(cleaned_title) < 100 and not re.match(r'^[A-Za-z\s,]+(?:NM|CA|TX|NY|FL|IL|PA|OH|GA|NC|MI|NJ|VA|WA|AZ|CO|TN|IN|MO|MD|MN|WI|AL|SC|LA|KY|OR|OK|CT|IA|MS|AR|KS|UT|NV|NM|WV|NE|ID|HI|NH|ME|MT|RI|DE|SD|ND|AK|VT|WY)$', cleaned_title):
            companyName = cleaned_title
    
    # Try h1 tag
    if not companyName:
        h1_tag = soup.find('h1')
        if h1_tag and h1_tag.get_text(strip=True):
            h1_text = h1_tag.get_text(strip=True)
            # Clean h1 text similar to title
            cleaned_h1 = re.sub(r'\s*[-|]\s*[A-Za-z\s,]+(?:NM|CA|TX|NY|FL|IL|PA|OH|GA|NC|MI|NJ|VA|WA|AZ|CO|TN|IN|MO|MD|MN|WI|AL|SC|LA|KY|OR|OK|CT|IA|MS|AR|KS|UT|NV|WV|NE|ID|HI|NH|ME|MT|RI|DE|SD|ND|AK|VT|WY)\s*[-|]?', '', h1_text, flags=re.IGNORECASE)
            cleaned_h1 = re.sub(r'^(Used Cars|New Cars|Auto Sales|Car Dealership|Auto Dealership)\s*[-|]\s*', '', cleaned_h1, flags=re.IGNORECASE)
            cleaned_h1 = cleaned_h1.strip()
            
            if cleaned_h1 and len(cleaned_h1) < 100:
                companyName = cleaned_h1
    
    # Industry (try meta tags and content analysis)
    industry = None
    
    # Try meta industry tag
    meta_industry = soup.find('meta', attrs={'name': 'industry'})
    if meta_industry and meta_industry.get('content'):
        industry = meta_industry['content'].strip()
    
    # Try to extract from content if not found
    if not industry:
        # Look for common industry keywords in the page
        page_text = soup.get_text().lower()
        industry_keywords = {
            'insurance': ['insurance', 'insurer', 'coverage', 'policy', 'premium', 'claim', 'farmers insurance', 'state farm', 'allstate', 'geico', 'progressive', 'agent', 'broker', 'underwriter'],
            'automotive': ['car dealership', 'auto dealership', 'used cars', 'new cars', 'auto sales', 'car sales', 'automotive dealer', 'vehicle dealer', 'car lot', 'auto lot'],
            'technology': ['tech', 'software', 'hardware', 'digital', 'ai', 'artificial intelligence', 'app', 'platform', 'saas', 'cloud', 'cyber', 'data'],
            'retail': ['shop', 'store', 'buy', 'sell', 'retail', 'commerce', 'online store', 'ecommerce', 'e-commerce', 'merchandise'],
            'finance': ['bank', 'financial', 'investment', 'credit', 'loan', 'mortgage', 'wealth', 'banking', 'financial services'],
            'healthcare': ['health', 'medical', 'hospital', 'clinic', 'pharmacy', 'doctor', 'physician', 'dental', 'healthcare', 'medical services'],
            'education': ['school', 'university', 'college', 'education', 'learning', 'academy', 'institute', 'educational'],
            'manufacturing': ['manufacturing', 'factory', 'production', 'industrial', 'manufacturer', 'manufacturing company'],
            'real estate': ['real estate', 'property', 'housing', 'construction', 'realtor', 'broker', 'realty', 'homes for sale'],
            'consulting': ['consulting', 'advisory', 'services', 'solutions', 'consultant', 'consulting firm'],
            'restaurant': ['restaurant', 'food', 'dining', 'cafe', 'bistro', 'grill', 'kitchen', 'restaurant', 'food service'],
            'legal': ['law', 'legal', 'attorney', 'lawyer', 'law firm', 'legal services', 'legal counsel']
        }
        
        # Check all industries and find the best match
        industry_scores = {}
        for ind, keywords in industry_keywords.items():
            score = sum(1 for keyword in keywords if keyword in page_text)
            if score > 0:
                industry_scores[ind] = score
        
        # Get the industry with the highest score
        if industry_scores:
            best_industry = max(industry_scores, key=industry_scores.get)
            # Map specific industry names to match frontend filter
            if best_industry == 'retail':
                industry = 'Retail'
            elif best_industry == 'real estate':
                industry = 'Real Estate'
            elif best_industry == 'automotive':
                industry = 'Automotive'
            elif best_industry == 'insurance':
                industry = 'Insurance'
            else:
                industry = best_industry.title()
    
    # Business Type (try meta tags and content analysis)
    businessType = None
    
    # Try meta business type tag
    meta_btype = soup.find('meta', attrs={'name': 'businessType'})
    if meta_btype and meta_btype.get('content'):
        businessType = meta_btype['content'].strip()
    
    # Try to extract from content
    if not businessType:
        page_text = soup.get_text().lower()
        if any(word in page_text for word in ['car dealership', 'auto dealership', 'dealership', 'used cars', 'new cars', 'auto sales', 'car sales']):
            businessType = 'Auto Dealership'
        elif any(word in page_text for word in ['startup', 'start-up']):
            businessType = 'Startup'
        elif any(word in page_text for word in ['enterprise', 'corporation', 'corp']):
            businessType = 'Enterprise'
        elif any(word in page_text for word in ['small business', 'sme']):
            businessType = 'Small Business'
        elif any(word in page_text for word in ['non-profit', 'nonprofit']):
            businessType = 'Non-Profit'
        else:
            businessType = 'Business'  # Default
    
    # Contact Form Detection - Enhanced for Multiple Forms
    contactFormUrl = None
    contact_links = []
    all_contact_options = []  # Store all contact options with scores
    
    # Look for contact links (existing logic)
    for a in soup.find_all('a', href=True):
        href = a['href'].lower()
        link_text = a.get_text().lower()
        
        # Skip third-party widgets and external services
        if any(external in href for external in ['usablenet', 'a40.', 'feedback', 'survey', 'zendesk', 'intercom']):
            continue
            
        # Skip about pages that might be misidentified as contact forms
        # UNLESS we're specifically looking for contact forms on about pages
        if any(word in href for word in ['about', 'about-us', 'aboutus', 'company', 'who-we-are', 'our-story']):
            # Only skip if we're not on an about page that was provided as contact form URL
            if not any(word in base_url for word in ['about', 'about-us', 'aboutus', 'company', 'who-we-are', 'our-story']):
                continue
            
        if any(word in href for word in ['contact', 'reach', 'get-in-touch']):
            contact_links.append(urljoin(base_url, a['href']))
            # Score this contact link
            score = 0
            if 'contact' in href: score += 10
            if 'contact' in link_text: score += 5
            if 'form' in href: score += 3
            if 'message' in href: score += 2
            
            all_contact_options.append({
                'type': 'static_link',
                'url': urljoin(base_url, a['href']),
                'text': link_text,
                'score': score,
                'priority': 1  # Static links get highest priority
            })
        elif any(word in link_text for word in ['contact', 'reach us', 'get in touch']):
            # Skip about pages that might be misidentified as contact forms
            # UNLESS we're specifically looking for contact forms on about pages
            if any(word in link_text for word in ['about', 'about us', 'company', 'who we are', 'our story']):
                # Only skip if we're not on an about page that was provided as contact form URL
                if not any(word in base_url for word in ['about', 'about-us', 'aboutus', 'company', 'who-we-are', 'our-story']):
                    continue
                
            contact_links.append(urljoin(base_url, a['href']))
            # Score this contact link
            score = 0
            if 'contact' in link_text: score += 8
            if 'reach' in link_text: score += 4
            if 'get in touch' in link_text: score += 6
            
            all_contact_options.append({
                'type': 'static_link',
                'url': urljoin(base_url, a['href']),
                'text': link_text,
                'score': score,
                'priority': 1
            })
    
    # Enhanced: Look for popup/modal contact forms
    popup_contact_forms = []
    
    # 1. Look for buttons with contact-related text
    for button in soup.find_all(['button', 'input', 'div', 'span'], class_=True):
        button_text = button.get_text().lower()
        button_classes = ' '.join(button.get('class', [])).lower()
        
        contact_keywords = ['contact', 'reach', 'get in touch', 'get-in-touch', 'message us', 'send message']
        if any(keyword in button_text for keyword in contact_keywords):
            popup_contact_forms.append({
                'type': 'button',
                'element': button,
                'text': button_text,
                'classes': button_classes
            })
            
            # Score this popup button
            score = 0
            if 'contact' in button_text: score += 7
            if 'get in touch' in button_text: score += 5
            if 'message' in button_text: score += 4
            if 'contact' in button_classes: score += 3
            
            all_contact_options.append({
                'type': 'popup_button',
                'url': None,  # Popup buttons don't have a specific URL
                'text': button_text,
                'score': score,
                'priority': 2,  # Popup buttons get medium priority
                'element_info': {
                    'classes': button_classes,
                    'tag': button.name
                }
            })
    
    # 2. Look for elements with contact-related classes
    contact_class_patterns = [
        'contact', 'modal', 'popup', 'form', 'dialog', 'overlay',
        'btn-contact', 'contact-btn', 'contact-button', 'contact-form',
        'modal-contact', 'popup-contact', 'contact-modal', 'contact-popup'
    ]
    
    for element in soup.find_all(['div', 'button', 'span', 'a'], class_=True):
        element_classes = ' '.join(element.get('class', [])).lower()
        if any(pattern in element_classes for pattern in contact_class_patterns):
            element_text = element.get_text().lower()
            if any(keyword in element_text for keyword in ['contact', 'reach', 'message', 'get in touch']):
                popup_contact_forms.append({
                    'type': 'element',
                    'element': element,
                    'text': element_text,
                    'classes': element_classes
                })
                
                # Score this element
                score = 0
                if 'contact' in element_classes: score += 6
                if 'modal' in element_classes: score += 4
                if 'form' in element_classes: score += 3
                if 'contact' in element_text: score += 5
                
                all_contact_options.append({
                    'type': 'popup_element',
                    'url': base_url,
                    'text': element_text,
                    'score': score,
                    'priority': 2,
                    'element_info': {
                        'classes': element_classes,
                        'tag': element.name
                    }
                })
    
    # 3. Look for data attributes that might trigger contact forms
    for element in soup.find_all(attrs={'data-toggle': True}):
        if 'modal' in element.get('data-toggle', '').lower():
            element_text = element.get_text().lower()
            if any(keyword in element_text for keyword in ['contact', 'reach', 'message']):
                popup_contact_forms.append({
                    'type': 'modal',
                    'element': element,
                    'text': element_text,
                    'data_toggle': element.get('data-toggle')
                })
                
                # Score this modal trigger
                score = 0
                if 'modal' in element.get('data-toggle', ''): score += 8
                if 'contact' in element_text: score += 6
                
                all_contact_options.append({
                    'type': 'modal_trigger',
                    'url': base_url,
                    'text': element_text,
                    'score': score,
                    'priority': 2,
                    'element_info': {
                        'data_toggle': element.get('data-toggle'),
                        'tag': element.name
                    }
                })
    
    # 4. Look for onclick handlers with contact-related functions
    for element in soup.find_all(attrs={'onclick': True}):
        onclick_value = element.get('onclick', '').lower()
        if any(keyword in onclick_value for keyword in ['contact', 'modal', 'popup', 'form']):
            element_text = element.get_text().lower()
            if any(keyword in element_text for keyword in ['contact', 'reach', 'message']):
                popup_contact_forms.append({
                    'type': 'onclick',
                    'element': element,
                    'text': element_text,
                    'onclick': element.get('onclick')
                })
                
                # Score this onclick element
                score = 0
                if 'contact' in onclick_value: score += 7
                if 'modal' in onclick_value: score += 5
                if 'form' in onclick_value: score += 4
                if 'contact' in element_text: score += 3
                
                all_contact_options.append({
                    'type': 'onclick_trigger',
                    'url': base_url,
                    'text': element_text,
                    'score': score,
                    'priority': 2,
                    'element_info': {
                        'onclick': element.get('onclick'),
                        'tag': element.name
                    }
                })
    
    # 5. Look for hidden contact forms in the page
    hidden_forms = []
    for form in soup.find_all('form'):
        form_text = form.get_text().lower()
        form_action = form.get('action', '').lower()
        form_id = form.get('id', '').lower()
        form_class = ' '.join(form.get('class', [])).lower()
        
        if any(keyword in form_text for keyword in ['contact', 'message', 'reach']) or \
           any(keyword in form_action for keyword in ['contact', 'message']) or \
           any(keyword in form_id for keyword in ['contact', 'message']) or \
           any(keyword in form_class for keyword in ['contact', 'message']):
            hidden_forms.append({
                'type': 'hidden_form',
                'form': form,
                'action': form_action,
                'id': form_id,
                'class': form_class
            })
            
            # Score this hidden form
            score = 0
            if 'contact' in form_text: score += 9
            if 'contact' in form_action: score += 8
            if 'contact' in form_id: score += 7
            if 'contact' in form_class: score += 6
            if form_action: score += 5  # Bonus for having an action URL
            
            # Only add if there's a valid form action URL
            if form_action and form_action.strip():
                all_contact_options.append({
                    'type': 'hidden_form',
                    'url': form_action,
                    'text': form_text[:50] + '...' if len(form_text) > 50 else form_text,
                    'score': score,
                    'priority': 1,  # Hidden forms get high priority
                    'element_info': {
                        'action': form_action,
                        'id': form_id,
                        'class': form_class
                    }
                })
    
    # Intelligent Contact Form Selection
    if all_contact_options:
        # Sort by priority first, then by score
        all_contact_options.sort(key=lambda x: (x['priority'], -x['score']))
        
        # Select the best contact form
        best_contact = all_contact_options[0]
        
        # Only set contact form URL if it's a valid URL (not None or empty)
        if best_contact.get('url') and best_contact['url'] != base_url:
            contactFormUrl = best_contact['url']
        
        # Log all found contact options for debugging
        logger.info(f"Found {len(all_contact_options)} contact options for {base_url}:")
        for i, option in enumerate(all_contact_options[:5]):  # Log top 5
            logger.info(f"  {i+1}. {option['type']}: {option['text'][:50]} (score: {option['score']}, priority: {option['priority']})")
    
    # Check if contact form exists (including popups)
    has_contact_form = bool(contactFormUrl) or bool(popup_contact_forms) or bool(hidden_forms)
    
    # About Us Content
    aboutUsContent = None
    about_url = None
    
    # Look for about links
    about_links = []
    logger.info(f"Searching for about links on {base_url}")
    
    for a in soup.find_all('a', href=True):
        href = a['href'].lower()
        link_text = a.get_text().lower()
        
        # Skip external links and third-party services
        if any(external in href for external in ['usablenet', 'a40.', 'facebook', 'twitter', 'instagram', 'youtube', 'pinterest']):
            continue
            
        if any(word in href for word in ['about', 'about-us', 'aboutus', 'company', 'who-we-are', 'our-story']):
            about_url = urljoin(base_url, a['href'])
            about_links.append(about_url)
            logger.info(f"Found about link by URL pattern: {about_url}")
        elif any(word in link_text for word in ['about', 'about us', 'company', 'who we are', 'our story']):
            about_url = urljoin(base_url, a['href'])
            about_links.append(about_url)
            logger.info(f"Found about link by text pattern: {about_url}")
    
    logger.info(f"Total about links found: {len(about_links)}")
    
    if about_links:
        about_url = about_links[0]  # Take the first about link
        logger.info(f"Fetching about page content from: {about_url}")
        
        # Try to fetch about page content
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
            about_resp = requests.get(about_url, timeout=10, headers=headers)
            logger.info(f"About page response status: {about_resp.status_code}")
            
            if about_resp.status_code == 200:
                about_soup = BeautifulSoup(about_resp.text, 'html.parser')
                
                # Try to get main content with multiple selectors
                main_content = None
                content_selectors = [
                    'main',
                    'article', 
                    'div.content',
                    'div.main-content',
                    'div#content',
                    'div#main',
                    'div.about',
                    'div.about-us'
                ]
                
                for selector in content_selectors:
                    main_content = about_soup.select_one(selector)
                    if main_content:
                        logger.info(f"Found main content with selector: {selector}")
                        break
                
                if main_content:
                    paragraphs = main_content.find_all('p')
                    logger.info(f"Found {len(paragraphs)} paragraphs in main content")
                else:
                    paragraphs = about_soup.find_all('p')
                    logger.info(f"Found {len(paragraphs)} paragraphs in full page")
                
                # Extract text from paragraphs
                content_parts = []
                for p in paragraphs:
                    text = p.get_text(strip=True)
                    if text and len(text) > 20:  # Only include substantial paragraphs
                        content_parts.append(text)
                
                logger.info(f"Extracted {len(content_parts)} substantial content parts")
                
                if content_parts:
                    aboutUsContent = '\n\n'.join(content_parts[:5])  # Limit to first 5 paragraphs
                    logger.info(f"Successfully extracted about page content ({len(aboutUsContent)} characters)")
                else:
                    # Fallback: Try to extract content from other elements
                    logger.info("No substantial paragraphs found, trying fallback extraction")
                    
                    # Try to get content from div elements with text
                    content_divs = about_soup.find_all('div')
                    for div in content_divs:
                        text = div.get_text(strip=True)
                        if text and len(text) > 50 and len(text) < 2000:  # Reasonable length
                            # Check if it contains about-related content
                            about_keywords = ['about', 'company', 'story', 'mission', 'vision', 'history']
                            if any(keyword in text.lower() for keyword in about_keywords):
                                content_parts.append(text)
                                logger.info(f"Found about content in div: {text[:100]}...")
                                break
                    
                    if content_parts:
                        aboutUsContent = '\n\n'.join(content_parts[:3])  # Limit to first 3 parts
                        logger.info(f"Successfully extracted about page content via fallback ({len(aboutUsContent)} characters)")
                    else:
                        logger.warning("No substantial content found in about page")
                    
        except Exception as e:
            logger.warning(f"Failed to fetch about page {about_url}: {str(e)}")
    else:
        logger.info("No about links found on the page")
    
    return {
        'title': title,
        'companyName': companyName,
        'industry': industry,
        'businessType': businessType,
        'contactFormUrl': contactFormUrl,
        'has_contact_form': has_contact_form,
        'aboutUsContent': aboutUsContent
    }

def validate_and_fix_url(url: str) -> str:
    """Validate URL and try to fix common issues"""
    
    # Remove common problematic characters
    url = url.strip()
    url = url.replace(' ', '')
    
    # Add protocol if missing
    if not url.startswith(('http://', 'https://')):
        url = 'https://' + url
    
    # Fix common domain issues
    url = url.replace('www.', '')  # Some sites don't like www
    
    return url

def get_alternative_urls(url: str) -> List[str]:
    """Generate alternative URLs to try"""
    
    alternatives = []
    
    # Try without www
    if 'www.' in url:
        alternatives.append(url.replace('www.', ''))
    
    # Try with www
    if 'www.' not in url:
        alternatives.append(url.replace('://', '://www.'))
    
    # Try HTTP if HTTPS
    if url.startswith('https://'):
        alternatives.append(url.replace('https://', 'http://'))
    
    # Try HTTPS if HTTP
    if url.startswith('http://'):
        alternatives.append(url.replace('http://', 'https://'))
    
    return alternatives

def robust_scrape_website(url: str) -> Dict[str, Any]:
    """Comprehensive scraping with multiple fallback strategies"""
    
    # Step 1: Validate and fix URL
    fixed_url = validate_and_fix_url(url)
    
    # Step 2: Try with requests first
    scraper = RobustWebScraper()
    result = scraper.scrape_with_error_handling(fixed_url)
    
    if result['success']:
        return result
    
    # Step 3: Try alternative URLs
    alternative_urls = get_alternative_urls(fixed_url)
    for alt_url in alternative_urls:
        result = scraper.scrape_with_error_handling(alt_url)
        if result['success']:
            return result
    
    # Step 4: Try Selenium fallback
    result = scrape_with_selenium_fallback(fixed_url)
    if result['success']:
        return result
    
    # Step 5: Try Selenium with alternative URLs
    for alt_url in alternative_urls:
        result = scrape_with_selenium_fallback(alt_url)
        if result['success']:
            return result
    
    # Step 6: Final failure
    return {
        'success': False,
        'error': 'All scraping strategies failed',
        'url': url,
        'attempted_urls': [fixed_url] + alternative_urls
    }

def scrape_with_selenium_fallback(url: str) -> Dict[str, Any]:
    """Use Selenium as fallback when requests fail"""
    
    try:
        from selenium import webdriver
        from selenium.webdriver.chrome.options import Options
        import tempfile
        import uuid
        import time
        
        options = Options()
        options.add_argument('--headless')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        
        # Create unique profile directory to avoid conflicts between workers
        unique_id = str(uuid.uuid4())[:8]
        timestamp = str(int(time.time() * 1000))
        profile_dir = tempfile.mkdtemp(prefix=f'chrome_scraping_{unique_id}_{timestamp}_')
        options.add_argument(f'--user-data-dir={profile_dir}')
        
        driver = webdriver.Chrome(options=options)
        driver.set_page_load_timeout(30)
        
        driver.get(url)
        
        # Wait for page to load
        time.sleep(3)
        
        content = driver.page_source
        driver.quit()
        
        # Clean up profile directory
        try:
            import shutil
            shutil.rmtree(profile_dir, ignore_errors=True)
        except:
            pass
        
        return {
            'success': True,
            'content': content,
            'url': url,
            'method': 'selenium'
        }
        
    except Exception as e:
        # Clean up profile directory on error
        try:
            import shutil
            shutil.rmtree(profile_dir, ignore_errors=True)
        except:
            pass
        
        return {
            'success': False,
            'error': f"Selenium fallback failed: {str(e)}",
            'url': url
        }

def scrape_website_data(url: str) -> Dict[str, Any]:
    """
    Scrape a single website and extract data using robust error handling
    """
    try:
        # Use robust scraping with comprehensive error handling
        result = robust_scrape_website(url)
        
        if not result['success']:
            logger.warning(f"Failed to scrape {url}: {result['error']}")
            return {
                'url': url,
                'title': '',
                'companyName': '',
                'industry': '',
                'businessType': '',
                'contactFormUrl': '',
                'has_contact_form': False,
                'aboutUsContent': '',
                'scrapingStatus': 'FAILED',
                'error_message': result['error']
            }
        
        # Extract company information from successful scrape
        info = extract_company_info(result['content'], url)
        
        logger.info(f"Successfully scraped {url} using {result.get('method', 'requests')}")
        
        # Enhanced: Try Selenium-based popup detection if no contact form found
        if not info['has_contact_form']:
            logger.info(f"No contact form found via static analysis for {url}, trying Selenium detection...")
            selenium_result = detect_popup_contact_forms_with_selenium(url)
            
            if selenium_result['has_contact_form']:
                # Only use Selenium result if it's not a third-party widget and has a valid URL
                best_form = selenium_result.get('best_contact_form', {})
                if best_form and best_form.get('url') and best_form['url'] != url:
                    # Check if it's not a third-party widget
                    if not any(external in best_form['url'].lower() for external in ['usablenet', 'a40.', 'feedback', 'survey']):
                        info['has_contact_form'] = True
                        info['contactFormUrl'] = best_form['url']
                        logger.info(f"Found valid popup contact form via Selenium for {url}")
                    else:
                        logger.info(f"Found third-party widget, not using as contact form for {url}")
                else:
                    logger.info(f"No valid contact form URL found via Selenium for {url}")
                
                # Log additional contact forms found
                if selenium_result['all_contact_forms']:
                    logger.info(f"Found {len(selenium_result['all_contact_forms'])} total contact forms")
                    for i, form in enumerate(selenium_result['all_contact_forms'][:3]):  # Log top 3
                        logger.info(f"  {i+1}. {form['type']}: score {form['score']}, priority {form['priority']}")
            else:
                logger.info(f"No valid contact forms found via Selenium for {url}")
        else:
            # If static analysis found contact forms, log the selection
            logger.info(f"Contact form found via static analysis for {url}: {info['contactFormUrl']}")
        
        return {
            'url': url,
            'title': info['title'],
            'companyName': info['companyName'],
            'industry': info['industry'],
            'businessType': info['businessType'],
            'contactFormUrl': info['contactFormUrl'],
            'has_contact_form': info['has_contact_form'],
            'aboutUsContent': info['aboutUsContent'],
            'scrapingStatus': 'COMPLETED',
            'error_message': ''
        }
        
    except Exception as e:
        logger.error(f"Unexpected error scraping website {url}: {str(e)}")
        return {
            'url': url,
            'title': '',
            'companyName': '',
            'industry': '',
            'businessType': '',
            'contactFormUrl': '',
            'has_contact_form': False,
            'aboutUsContent': '',
            'scrapingStatus': 'FAILED',
            'error_message': str(e)
        }

def detect_popup_contact_forms_with_selenium(url: str) -> Dict[str, Any]:
    """
    Use Selenium to detect popup contact forms that require JavaScript
    Enhanced to handle multiple contact forms with intelligent selection
    """
    try:
        from selenium import webdriver
        from selenium.webdriver.common.by import By
        from selenium.webdriver.support.ui import WebDriverWait
        from selenium.webdriver.support import expected_conditions as EC
        from selenium.webdriver.chrome.options import Options
        import time
        import tempfile
        import os
        
        # Create a unique temporary directory for user data
        temp_dir = tempfile.mkdtemp(prefix="chrome_user_data_")
        
        # Configure Chrome options for headless browsing
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--window-size=1920,1080")
        chrome_options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36")
        chrome_options.add_argument(f"--user-data-dir={temp_dir}")
        
        driver = webdriver.Chrome(options=chrome_options)
        driver.get(url)
        
        # Wait for page to load
        time.sleep(3)
        
        all_popup_forms = []
        contact_form_scores = []
        
        # 1. Look for contact buttons and click them to see if forms appear
        contact_button_selectors = [
            "button:contains('Contact')",
            "button:contains('Get in Touch')", 
            "button:contains('Reach Us')",
            "button:contains('Message Us')",
            "a:contains('Contact')",
            "[class*='contact']",
            "[id*='contact']",
            "[class*='btn-contact']",
            "[class*='contact-btn']"
        ]
        
        for selector in contact_button_selectors:
            try:
                elements = driver.find_elements(By.CSS_SELECTOR, selector)
                for element in elements:
                    if element.is_displayed():
                        element_text = element.text.lower()
                        
                        # Score this contact element
                        score = 0
                        if 'contact' in element_text: score += 10
                        if 'get in touch' in element_text: score += 8
                        if 'message' in element_text: score += 6
                        if 'reach' in element_text: score += 5
                        
                        # Click the element to trigger popup
                        driver.execute_script("arguments[0].click();", element)
                        time.sleep(1)
                        
                        # Check if a modal/popup appeared
                        modal_selectors = [
                            "[class*='modal']",
                            "[class*='popup']", 
                            "[class*='dialog']",
                            "[class*='overlay']",
                            "form",
                            "[role='dialog']",
                            "[class*='contact-form']",
                            "[class*='contact-modal']"
                        ]
                        
                        for modal_selector in modal_selectors:
                            modals = driver.find_elements(By.CSS_SELECTOR, modal_selector)
                            for modal in modals:
                                if modal.is_displayed():
                                    modal_text = modal.text.lower()
                                    
                                    # Score the modal content
                                    modal_score = score  # Start with trigger score
                                    if 'contact' in modal_text: modal_score += 8
                                    if 'form' in modal_text: modal_score += 6
                                    if 'email' in modal_text: modal_score += 4
                                    if 'name' in modal_text: modal_score += 3
                                    if 'message' in modal_text: modal_score += 5
                                    
                                    # Check if this is a third-party widget
                                    modal_html = modal.get_attribute('outerHTML').lower()
                                    if any(external in modal_html for external in ['usablenet', 'a40.', 'feedback', 'survey', 'zendesk', 'intercom']):
                                        continue  # Skip third-party widgets
                                        
                                    popup_form = {
                                        'type': 'selenium_detected',
                                        'trigger_element': element.text,
                                        'trigger_score': score,
                                        'modal_selector': modal_selector,
                                        'modal_text': modal.text[:100] if modal.text else '',
                                        'modal_score': modal_score,
                                        'total_score': modal_score,
                                        'url': None  # Popup forms don't have a specific URL
                                    }
                                    
                                    all_popup_forms.append(popup_form)
                                    # Don't add popup forms to contact_form_scores since they don't have a specific URL
                        
                        # Close modal if it appeared
                        try:
                            close_buttons = driver.find_elements(By.CSS_SELECTOR, "[class*='close'], [class*='dismiss'], .close, .dismiss, [aria-label='Close']")
                            for close_btn in close_buttons:
                                if close_btn.is_displayed():
                                    driver.execute_script("arguments[0].click();", close_btn)
                                    break
                        except:
                            pass
                            
            except Exception as e:
                logger.warning(f"Error clicking contact element: {e}")
                continue
        
        # 2. Look for static contact forms on the page
        static_form_selectors = [
            "form[action*='contact']",
            "form[id*='contact']",
            "form[class*='contact']",
            "form:contains('Contact')",
            "form:contains('Message')"
        ]
        
        for selector in static_form_selectors:
            try:
                forms = driver.find_elements(By.CSS_SELECTOR, selector)
                for form in forms:
                    if form.is_displayed():
                        form_text = form.text.lower()
                        form_action = form.get_attribute('action') or ''
                        
                        # Score this static form
                        score = 0
                        if 'contact' in form_text: score += 12
                        if 'contact' in form_action: score += 10
                        if 'form' in form_text: score += 6
                        if 'email' in form_text: score += 4
                        if 'name' in form_text: score += 3
                        
                        # Only add if there's a valid form action URL
                        if form_action and form_action.strip():
                            contact_form_scores.append({
                                'type': 'static_form',
                                'url': form_action,
                                'score': score,
                                'priority': 1,  # Static forms get higher priority
                                'details': {
                                    'type': 'static_form',
                                    'text': form_text[:100],
                                    'action': form_action
                                }
                            })
            except Exception as e:
                logger.warning(f"Error checking static forms: {e}")
                continue
        
        driver.quit()
        
        # Clean up temporary directory
        try:
            import shutil
            shutil.rmtree(temp_dir, ignore_errors=True)
        except Exception as e:
            logger.warning(f"Error cleaning up temp directory {temp_dir}: {e}")
        
        # Select the best contact form
        best_contact_form = None
        if contact_form_scores:
            # Sort by priority first, then by score
            contact_form_scores.sort(key=lambda x: (x['priority'], -x['score']))
            best_contact_form = contact_form_scores[0]
            
            # Log all found contact forms for debugging
            logger.info(f"Found {len(contact_form_scores)} contact forms via Selenium for {url}:")
            for i, form in enumerate(contact_form_scores[:5]):  # Log top 5
                logger.info(f"  {i+1}. {form['type']}: score {form['score']}, priority {form['priority']}")
        
        return {
            'popup_forms_detected': len(all_popup_forms) > 0,
            'popup_forms': all_popup_forms,
            'has_contact_form': bool(best_contact_form),
            'best_contact_form': best_contact_form,
            'all_contact_forms': contact_form_scores
        }
        
    except ImportError:
        logger.warning("Selenium not available for popup form detection")
        return {'popup_forms_detected': False, 'popup_forms': [], 'has_contact_form': False}
    except Exception as e:
        logger.error(f"Error in Selenium popup detection: {e}")
        return {'popup_forms_detected': False, 'popup_forms': [], 'has_contact_form': False}

@celery_app.task(bind=True)
def scrape_websites_task(self, fileUploadId: str, userId: str, websites: List[str], job_id: str = None):
    """
    Celery task to scrape websites and save real data to database
    """
    try:
        logger.info(f"Starting scraping task for {len(websites)} websites")
        
        # Initialize database manager
        db_manager = DatabaseManager()
        
        # Create file upload record if it doesn't exist
        # Calculate estimated file size based on number of websites (roughly 100 bytes per website)
        estimated_fileSize = len(websites) * 100
        
        db_manager.create_file_upload(
            fileUploadId=fileUploadId,
            userId=userId,
            filename=f"scraping-{fileUploadId}.csv",
            originalName=f"scraping-{fileUploadId}.csv",
            fileSize=estimated_fileSize,
            fileType="csv",
            status="PENDING",
            totalWebsites=len(websites),
            processedWebsites=0,
            failedWebsites=0,
            totalChunks=1,
            completedChunks=0
        )
        
        # Update job status to RUNNING
        if job_id:
            db_manager.update_scraping_job_status(job_id, "RUNNING")
        
        # Scrape websites
        scraped_data = []
        totalWebsites = len(websites)
        processedWebsites = 0
        failedWebsites = 0
        
        for i, website in enumerate(websites):
            try:
                logger.info(f"Scraping website {i+1}/{totalWebsites}: {website}")
                
                # Scrape the website
                website_data = scrape_website_data(website)
                
                # Update existing website record with scraping data
                success = db_manager.update_website_with_scraping_data(
                    fileUploadId=fileUploadId,
                    url=website_data['url'],
                    title=website_data['title'],
                    companyName=website_data['companyName'],
                    industry=website_data['industry'],
                    businessType=website_data['businessType'],
                    contactFormUrl=website_data['contactFormUrl'],
                    has_contact_form=website_data['has_contact_form'],
                    aboutUsContent=website_data['aboutUsContent'],
                    scrapingStatus=website_data['scrapingStatus'],
                    error_message=website_data['error_message']
                )
                
                if success:
                    scraped_data.append(website_data)
                    processedWebsites += 1
                    logger.info(f"Successfully scraped and updated: {website}")
                    
                    # 🚀 IMMEDIATELY TRIGGER AI MESSAGE GENERATION for this website
                    try:
                        logger.info(f"Starting AI message generation for {website}")
                        
                        # Get the specific website record for AI generation
                        website_record = db_manager.get_website_by_url(website_data['url'])
                        
                        if website_record:
                            # Start AI message generation task for this individual website
                            # Use apply_async to avoid circular imports and get task ID
                            message_task = celery_app.send_task(
                                'celery_tasks.scraping_tasks.generate_messages_task',
                                args=[[website_record], "general", fileUploadId, userId],
                                kwargs={}
                            )
                            logger.info(f"AI message generation task started for {website}: {message_task.id}")
                            
                            # 🚀 IMMEDIATELY TRIGGER CONTACT FORM SUBMISSION if contact form exists
                            if website_data.get('has_contact_form') and website_data.get('contactFormUrl'):
                                try:
                                    logger.info(f"Starting contact form submission for {website}")
                                    
                                    # Start contact form submission task for this individual website
                                    submission_task = celery_app.send_task(
                                        'celery_tasks.form_submission_tasks.submit_contact_forms_task',
                                        args=[[website_record], "general", fileUploadId, userId],
                                        kwargs={}
                                    )
                                    logger.info(f"Contact form submission task started for {website}: {submission_task.id}")
                                    
                                except Exception as e:
                                    logger.error(f"Error starting contact form submission for {website}: {e}")
                            else:
                                logger.info(f"No contact form found for {website}, skipping submission")
                        else:
                            logger.warning(f"Website record not found for {website}")
                    except Exception as e:
                        logger.error(f"Error starting AI message generation for {website}: {e}")
                    
                else:
                    failedWebsites += 1
                    logger.error(f"Failed to update website data for {website}")
                
                # Update progress
                progress = int((i + 1) / totalWebsites * 100)
                self.update_state(
                    state='PROGRESS',
                    meta={
                        'current': i + 1,
                        'total': totalWebsites,
                        'progress': progress,
                        'processedWebsites': processedWebsites,
                        'failedWebsites': failedWebsites
                    }
                )
                
                # Small delay to avoid overwhelming servers
                time.sleep(1)
                
            except Exception as e:
                failedWebsites += 1
                logger.error(f"Error scraping website {website}: {str(e)}")
                continue
        
        # Update job status to COMPLETED
        if job_id:
            db_manager.update_scraping_job(
                job_id=job_id,
                status="COMPLETED",
                total_websites=totalWebsites,
                processed_websites=processedWebsites,
                failed_websites=failedWebsites
            )
        
        logger.info(f"Scraping task completed. Processed {processedWebsites}/{totalWebsites} websites, Failed: {failedWebsites}")
        
        # ✅ AUTOMATICALLY TRIGGER AI MESSAGE GENERATION after successful scraping
        if processedWebsites > 0:
            try:
                logger.info(f"🚀 Automatically triggering AI message generation for {processedWebsites} successfully scraped websites")
                
                # Get the successfully scraped websites for AI generation
                successful_websites = db_manager.get_websites_by_file_upload_id(fileUploadId)
                successful_websites = [w for w in successful_websites if w.get('scrapingStatus') == 'COMPLETED']
                
                if successful_websites:
                    # Trigger AI message generation automatically
                    ai_task = celery_app.send_task(
                        'celery_tasks.scraping_tasks.generate_messages_task',
                        args=[successful_websites, "general", fileUploadId, userId],
                        kwargs={}
                    )
                    
                    logger.info(f"✅ AI message generation automatically triggered with task ID: {ai_task.id}")
                    
                    # Update file upload status to show AI generation is in progress
                    db_manager.update_file_upload(fileUploadId, {
                        'status': 'AI_GENERATION_IN_PROGRESS',
                        'processedWebsites': processedWebsites,
                        'failedWebsites': failedWebsites
                    })
                else:
                    logger.warning("No successfully scraped websites found for AI generation")
                    # Update status to show scraping completed but no websites for AI
                    db_manager.update_file_upload(fileUploadId, {
                        'status': 'SCRAPING_COMPLETED_NO_WEBSITES',
                        'processedWebsites': processedWebsites,
                        'failedWebsites': failedWebsites
                    })
                    
            except Exception as ai_error:
                logger.error(f"❌ Failed to automatically trigger AI message generation: {ai_error}")
                # Don't fail the scraping task if AI generation fails
                # Just log the error and continue
                db_manager.update_file_upload(fileUploadId, {
                    'status': 'SCRAPING_COMPLETED_AI_FAILED',
                    'processedWebsites': processedWebsites,
                    'failedWebsites': failedWebsites
                })
        else:
            # No websites were successfully scraped
            logger.warning("No websites were successfully scraped, cannot trigger AI generation")
            db_manager.update_file_upload(fileUploadId, {
                'status': 'SCRAPING_FAILED_ALL_WEBSITES',
                'processedWebsites': 0,
                'failedWebsites': totalWebsites
            })
        
        return {
            'status': 'success',
            'scraped_count': len(scraped_data),
            'totalWebsites': totalWebsites,
            'processedWebsites': processedWebsites,
            'failedWebsites': failedWebsites,
            'websites': [data['url'] for data in scraped_data]
        }
        
    except Exception as e:
        logger.error(f"Error in scraping task: {str(e)}")
        
        # Update job status to FAILED
        if job_id:
            try:
                db_manager = DatabaseManager()
                db_manager.update_scraping_job_status(job_id, "FAILED")
            except Exception as db_error:
                logger.error(f"Failed to update job status: {db_error}")
        
        # Update file upload status to FAILED
        try:
            db_manager = DatabaseManager()
            db_manager.update_file_upload(fileUploadId, {
                'status': 'SCRAPING_FAILED',
                'processingCompletedAt': datetime.now().isoformat()
            })
        except Exception as update_error:
            logger.error(f"Failed to update file upload status: {update_error}")
        
        # Return error result instead of raising exception to prevent serialization issues
        return {
            'status': 'error',
            'error': str(e),
            'totalWebsites': 0,
            'processedWebsites': 0,
            'failedWebsites': 0,
            'websites': []
        }

@celery_app.task(bind=True)
def scrape_websites_async_task(self, fileUploadId: str, userId: str, websites: List[str], job_id: str = None):
    """
    Async version of website scraping task
    """
    try:
        logger.info(f"Starting async scraping task for {len(websites)} websites")
        
        # Initialize database manager
        db_manager = DatabaseManager()
        
        # Update job status to RUNNING
        if job_id:
            db_manager.update_scraping_job_status(job_id, "RUNNING")
        
        # Run async scraping
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        try:
            result = loop.run_until_complete(
                scrape_websites_async(fileUploadId, userId, websites, job_id, self, db_manager)
            )
            return result
        finally:
            loop.close()
            
    except Exception as e:
        logger.error(f"Error in async scraping task: {str(e)}")
        
        # Update job status to FAILED
        if job_id:
            db_manager = DatabaseManager()
            db_manager.update_scraping_job_status(job_id, "FAILED")
        
        raise

async def scrape_websites_async(fileUploadId: str, userId: str, websites: List[str], job_id: str, task_instance, db_manager):
    """
    Async function to scrape websites
    """
    scraped_data = []
    totalWebsites = len(websites)
    processedWebsites = 0
    failedWebsites = 0
    
    async with aiohttp.ClientSession() as session:
        for i, website in enumerate(websites):
            try:
                # Use the same scraping logic but with aiohttp
                website_data = scrape_website_data(website)
                
                # Update existing website record with scraping data
                success = db_manager.update_website_with_scraping_data(
                    fileUploadId=fileUploadId,
                    url=website_data['url'],
                    title=website_data['title'],
                    companyName=website_data['companyName'],
                    industry=website_data['industry'],
                    businessType=website_data['businessType'],
                    contactFormUrl=website_data['contactFormUrl'],
                    has_contact_form=website_data['has_contact_form'],
                    aboutUsContent=website_data['aboutUsContent'],
                    scrapingStatus=website_data['scrapingStatus'],
                    error_message=website_data['error_message']
                )
                
                if success:
                    scraped_data.append(website_data)
                    processedWebsites += 1
                    logger.info(f"Successfully scraped and updated: {website}")
                    
                    # 🚀 IMMEDIATELY TRIGGER AI MESSAGE GENERATION for this website
                    try:
                        logger.info(f"Starting AI message generation for {website}")
                        
                        # Get the specific website record for AI generation
                        website_record = db_manager.get_website_by_url(website_data['url'])
                        
                        if website_record:
                            # Start AI message generation task for this individual website
                            # Use apply_async to avoid circular imports and get task ID
                            message_task = celery_app.send_task(
                                'celery_tasks.scraping_tasks.generate_messages_task',
                                args=[[website_record], "general", fileUploadId, userId],
                                kwargs={}
                            )
                            logger.info(f"AI message generation task started for {website}: {message_task.id}")
                            
                            # 🚀 IMMEDIATELY TRIGGER CONTACT FORM SUBMISSION if contact form exists
                            if website_data.get('has_contact_form') and website_data.get('contactFormUrl'):
                                try:
                                    logger.info(f"Starting contact form submission for {website}")
                                    
                                    # Start contact form submission task for this individual website
                                    submission_task = celery_app.send_task(
                                        'celery_tasks.form_submission_tasks.submit_contact_forms_task',
                                        args=[[website_record], "general", fileUploadId, userId],
                                        kwargs={}
                                    )
                                    logger.info(f"Contact form submission task started for {website}: {submission_task.id}")
                                    
                                except Exception as e:
                                    logger.error(f"Error starting contact form submission for {website}: {e}")
                            else:
                                logger.info(f"No contact form found for {website}, skipping submission")
                        else:
                            logger.warning(f"Website record not found for {website}")
                    except Exception as e:
                        logger.error(f"Error starting AI message generation for {website}: {e}")
                    
                else:
                    failedWebsites += 1
                    logger.error(f"Failed to update website data for: {website}")
                
                # Update progress
                progress = int((i + 1) / totalWebsites * 100)
                task_instance.update_state(
                    state='PROGRESS',
                    meta={
                        'current': i + 1,
                        'total': totalWebsites,
                        'progress': progress,
                        'processedWebsites': processedWebsites,
                        'failedWebsites': failedWebsites
                    }
                )
                
                # Small delay
                await asyncio.sleep(1)
                
            except Exception as e:
                failedWebsites += 1
                logger.error(f"Error scraping website {website}: {str(e)}")
                continue
    
    # Update job status to COMPLETED
    if job_id:
        db_manager.update_scraping_job(
            job_id=job_id,
            status="COMPLETED",
            totalWebsites=totalWebsites,
            processedWebsites=processedWebsites,
            failedWebsites=failedWebsites
        )
    
    return {
        'status': 'success',
        'scraped_count': len(scraped_data),
        'totalWebsites': totalWebsites,
        'processedWebsites': processedWebsites,
        'failedWebsites': failedWebsites,
        'websites': [data['url'] for data in scraped_data]
    }

@celery_app.task(bind=True)
def generate_messages_task(self, website_data: List[Dict], message_type: str = "general", fileUploadId: str = None, userId: str = None):
    """
    Generate AI messages for scraped websites
    """
    try:
        logger.info(f"Starting message generation for {len(website_data)} websites")
        logger.info(f"🔍 DEBUG: website_data type: {type(website_data)}")
        logger.info(f"🔍 DEBUG: website_data length: {len(website_data) if website_data else 'None'}")
        if website_data and len(website_data) > 0:
            logger.info(f"🔍 DEBUG: First website data sample: {website_data[0]}")
            logger.info(f"🔍 DEBUG: First website keys: {list(website_data[0].keys()) if website_data[0] else 'None'}")
        
        # Initialize database manager
        db_manager = DatabaseManager()
        
        generated_messages = []
        totalWebsites = len(website_data)
        processedWebsites = 0
        failedWebsites = 0
        
        # TESTING LIMIT: Only generate messages for first 2 successfully scraped websites
        max_messages_to_generate = MAX_AI_MESSAGES_PER_FILE if TESTING_MODE_ENABLED else totalWebsites
        
        logger.info(f"🔍 DEBUG: Starting to process {len(website_data)} websites")
        logger.info(f"🔍 DEBUG: Max messages to generate: {max_messages_to_generate}")
        logger.info(f"🔍 DEBUG: Testing mode enabled: {TESTING_MODE_ENABLED}")
        
        for i, website in enumerate(website_data):
            try:
                logger.info(f"🔍 DEBUG: Processing website {i+1}/{len(website_data)}: {website.get('websiteUrl')}")
                logger.info(f"🔍 DEBUG: Website scraping status: {repr(website.get('scrapingStatus'))}")
                logger.info(f"🔍 DEBUG: Current processed count: {processedWebsites}, limit: {max_messages_to_generate}")
                
                # Check if we've reached the testing limit
                if processedWebsites >= max_messages_to_generate:
                    logger.info(f"Testing limit reached ({max_messages_to_generate} messages). Skipping remaining websites.")
                    break
                
                # Only generate messages for successfully scraped websites
                if website.get('scrapingStatus') != 'COMPLETED':
                    logger.info(f"Skipping website {website.get('websiteUrl')} - scraping status: {website.get('scrapingStatus')}")
                    continue
                
                # Generate message based on website data
                logger.info(f"🔍 DEBUG: About to call generate_ai_message for website: {website.get('websiteUrl', 'Unknown URL')}")
                logger.info(f"🔍 DEBUG: Website data being passed: {website}")
                logger.info(f"🔍 DEBUG: Message type: {message_type}")
                
                message, confidence = generate_ai_message(website, message_type)
                
                logger.info(f"🔍 DEBUG: generate_ai_message returned - message: {type(message)}, confidence: {confidence}")
                if message:
                    logger.info(f"🔍 DEBUG: Message content preview: {message[:100]}...")
                else:
                    logger.info(f"🔍 DEBUG: Message is None or empty")
                
                # Check if message generation was successful
                if not message or message.strip() == "":
                    logger.warning(f"Empty message generated for {website.get('websiteUrl')}, skipping database update")
                    failedWebsites += 1
                    continue
                
                # Save generated message to database
                success = db_manager.update_website_message(
                    website_id=website.get('id'),
                    generatedMessage=message,
                    messageStatus="GENERATED"
                )
                
                if success:
                    generated_messages.append({
                        'website_id': website.get('id'),
                        'url': website.get('websiteUrl'),
                        'message': message
                    })
                    processedWebsites += 1
                    logger.info(f"Generated message for: {website.get('websiteUrl')} ({processedWebsites}/{max_messages_to_generate})")
                else:
                    failedWebsites += 1
                    logger.error(f"Failed to save message for: {website.get('websiteUrl')}")
                
                # Update progress
                progress = int((i + 1) / totalWebsites * 100)
                self.update_state(
                    state='PROGRESS',
                    meta={
                        'current': i + 1,
                        'total': totalWebsites,
                        'progress': progress,
                        'processedWebsites': processedWebsites,
                        'failedWebsites': failedWebsites,
                        'messages_generated': processedWebsites,
                        'max_messages': max_messages_to_generate
                    }
                )
                
                # Small delay
                time.sleep(0.5)
                
            except Exception as e:
                failedWebsites += 1
                logger.error(f"Error generating message for website {website.get('url')}: {str(e)}")
                continue
        
        # Final status update
        if processedWebsites > 0:
            # Update file upload status to show AI generation completed
            if fileUploadId:
                try:
                    db_manager.update_file_upload(fileUploadId, {
                        'status': 'AI_GENERATION_COMPLETED',
                        'processedWebsites': processedWebsites,
                        'failedWebsites': failedWebsites
                    })
                    logger.info(f"✅ File upload {fileUploadId} status updated to AI_GENERATION_COMPLETED")
                    
                    # 🚀 AUTOMATICALLY TRIGGER CONTACT FORM SUBMISSION after successful AI generation
                    try:
                        logger.info(f"🚀 Automatically triggering contact form submission for {processedWebsites} successfully generated websites")
                        
                        # Get the successfully generated websites for contact form submission
                        successful_websites = db_manager.get_websites_by_file_upload_id(fileUploadId)
                        successful_websites = [w for w in successful_websites if w.get('messageStatus') == 'GENERATED']
                        
                        if successful_websites:
                            # Trigger contact form submission automatically
                            contact_task = celery_app.send_task(
                                'celery_tasks.form_submission_tasks.submit_contact_forms_task',
                                args=[successful_websites, "general", fileUploadId, userId],
                                kwargs={}
                            )
                            
                            logger.info(f"✅ Contact form submission automatically triggered with task ID: {contact_task.id}")
                            
                            # Update file upload status to show contact form submission is in progress
                            db_manager.update_file_upload(fileUploadId, {
                                'status': 'CONTACT_FORM_SUBMISSION_IN_PROGRESS',
                                'processedWebsites': processedWebsites,
                                'failedWebsites': failedWebsites
                            })
                        else:
                            logger.warning("No successfully generated websites found for contact form submission")
                            # Update status to show AI generation completed but no websites for contact form submission
                            db_manager.update_file_upload(fileUploadId, {
                                'status': 'AI_GENERATION_COMPLETED_NO_CONTACT_FORMS',
                                'processedWebsites': processedWebsites,
                                'failedWebsites': failedWebsites
                            })
                            
                    except Exception as contact_error:
                        logger.error(f"❌ Failed to automatically trigger contact form submission: {contact_error}")
                        # Don't fail the AI generation task if contact form submission fails
                        # Just log the error and continue
                        db_manager.update_file_upload(fileUploadId, {
                            'status': 'AI_GENERATION_COMPLETED_CONTACT_FORM_FAILED',
                            'processedWebsites': processedWebsites,
                            'failedWebsites': failedWebsites
                        })
                        
                except Exception as update_error:
                    logger.error(f"❌ Failed to update file upload status: {update_error}")
                    # Don't fail the entire task for a status update error
        else:
            # No messages were generated
            if fileUploadId:
                try:
                    db_manager.update_file_upload(fileUploadId, {
                        'status': 'AI_GENERATION_FAILED_ALL_WEBSITES',
                        'processedWebsites': 0,
                        'failedWebsites': totalWebsites
                    })
                    logger.warning(f"⚠️ File upload {fileUploadId} status updated to AI_GENERATION_FAILED_ALL_WEBSITES")
                except Exception as update_error:
                    logger.error(f"❌ Failed to update file upload status: {update_error}")
        
        logger.info(f"AI message generation task completed. Generated {processedWebsites}/{totalWebsites} messages, Failed: {failedWebsites}")
        
        return {
            'status': 'success',
            'generated_count': len(generated_messages),
            'totalWebsites': totalWebsites,
            'processedWebsites': processedWebsites,
            'failedWebsites': failedWebsites,
            'messages_generated': processedWebsites,
            'max_messages': max_messages_to_generate,
            'testing_limit_applied': TESTING_MODE_ENABLED,
            'messages': generated_messages
        }
        
    except Exception as e:
        logger.error(f"Error in message generation task: {str(e)}")
        
        # Update file upload status to show AI generation failed
        if fileUploadId:
            try:
                db_manager = DatabaseManager()
                db_manager.update_file_upload(fileUploadId, {
                    'status': 'AI_GENERATION_FAILED',
                    'processingCompletedAt': datetime.now().isoformat()
                })
            except Exception as update_error:
                logger.error(f"Failed to update file upload status: {update_error}")
        
        # Return error result instead of raising exception to prevent serialization issues
        return {
            'status': 'error',
            'error': str(e),
            'totalWebsites': 0,
            'processedWebsites': 0,
            'failedWebsites': 0,
            'messages_generated': 0,
            'messages': []
        }

def generate_ai_message(website_data: Dict, message_type: str = "general") -> Tuple[str, float]:
    """
    Generate AI message using enhanced Gemini with predefined message integration
    """
    try:
        logger.info(f"🔍 DEBUG: generate_ai_message called with website_data type: {type(website_data)}")
        logger.info(f"🔍 DEBUG: website_data keys: {list(website_data.keys()) if website_data else 'None'}")
        logger.info(f"🔍 DEBUG: message_type: {message_type}")
        
        # Import AI message generator
        from ai.message_generator import GeminiMessageGenerator
        
        # Initialize database manager and AI generator
        logger.info(f"🔍 DEBUG: Initializing DatabaseManager...")
        db_manager = DatabaseManager()
        logger.info(f"🔍 DEBUG: DatabaseManager initialized successfully")
        
        logger.info(f"🔍 DEBUG: Initializing GeminiMessageGenerator...")
        ai_generator = GeminiMessageGenerator(db_manager=db_manager)
        logger.info(f"🔍 DEBUG: GeminiMessageGenerator initialized successfully")
        
        # Map database field names to AI generator expected field names
        mapped_website_data = {
            'company_name': website_data.get('companyName', ''),
            'industry': website_data.get('industry', ''),
            'business_type': website_data.get('businessType', ''),
            'about_us_content': website_data.get('aboutUsContent', ''),
            'website_url': website_data.get('websiteUrl', '')
        }
        
        logger.info(f"🔍 DEBUG: Mapped website data: {mapped_website_data}")
        
        # Generate message using the hybrid_message_generation method
        logger.info(f"🔍 DEBUG: About to call hybrid_message_generation...")
        logger.info(f"🔍 DEBUG: ai_generator type: {type(ai_generator)}")
        
        result = ai_generator.hybrid_message_generation(mapped_website_data, message_type)
        
        # Extract message and confidence from result
        if isinstance(result, dict):
            message = result.get('message', '')
            confidence = result.get('confidence_score', 0.0)
        else:
            # Fallback if result is not a dict
            message = str(result) if result else ''
            confidence = 0.0
        
        logger.info(f"🔍 DEBUG: hybrid_message_generation returned - message: {type(message)}, confidence: {confidence}")
        if message:
            logger.info(f"🔍 DEBUG: Message content preview: {message[:100]}...")
        else:
            logger.info(f"🔍 DEBUG: Message is None or empty")
        
        logger.info(f"Generated message for {website_data.get('companyName', 'Unknown')} with confidence {confidence:.2f}")
        
        return message, confidence
        
    except Exception as e:
        logger.error(f"Error generating AI message: {e}")
        
        # Check if it's a quota limit error
        if "quota" in str(e).lower() or "429" in str(e):
            logger.warning("Gemini API quota limit reached, using fallback message")
            # Fallback to basic message
            fallback_message = f"""
Dear {website_data.get('companyName', 'Team')},

I hope this message finds you well. I came across your {website_data.get('industry', 'business')} and was impressed by your work.

I believe there could be excellent opportunities for collaboration between our organizations. Would you be interested in a brief conversation to discuss how we might work together?

Best regards,
[Your Name]
            """.strip()
            return fallback_message, 0.3
        else:
            # For other errors, return empty message
            logger.error(f"AI generation failed with non-quota error: {e}")
            return "", 0.0 