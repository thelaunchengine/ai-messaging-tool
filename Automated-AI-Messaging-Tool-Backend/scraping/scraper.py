import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import time
import logging
from typing import Dict, List, Optional, Tuple
import random

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class WebsiteScraper:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
        
    def _get_random_user_agent(self):
        user_agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0.3 Safari/605.1.15',
            'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.96 Safari/537.36',
            'Mozilla/5.0 (iPhone; CPU iPhone OS 14_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0 Mobile/15A372 Safari/604.1',
        ]
        return random.choice(user_agents)
    
    def scrape_website(self, website_url: str) -> Dict:
        """
        Scrape a website for contact form and about us content using requests only
        
        Args:
            website_url: The website URL to scrape
            
        Returns:
            Dictionary containing scraping results
        """
        max_retries = 3
        for attempt in range(1, max_retries + 1):
            try:
                logger.info(f"[Attempt {attempt}] Starting to scrape: {website_url}")
                if not website_url.startswith(('http://', 'https://')):
                    website_url = 'https://' + website_url
                
                # Update user agent for each attempt
                self.session.headers.update({'User-Agent': self._get_random_user_agent()})
                
                # Make request
                response = self.session.get(website_url, timeout=15)
                response.raise_for_status()
                soup = BeautifulSoup(response.content, 'html.parser')
                
                # Extract data
                contact_form_url = self._find_contact_form(soup, website_url)
                about_us_content = self._extract_about_us_content(soup, website_url)
                company_info = self._extract_company_info(soup)
                
                result = {
                    'website_url': website_url,
                    'contact_form_url': contact_form_url,
                    'has_contact_form': contact_form_url is not None,
                    'about_us_content': about_us_content,
                    'company_name': company_info.get('name'),
                    'business_type': company_info.get('type'),
                    'industry': company_info.get('industry'),
                    'scraping_status': 'COMPLETED',
                    'error_message': None
                }
                logger.info(f"Successfully scraped {website_url}")
                return result
                
            except Exception as e:
                logger.error(f"[Attempt {attempt}] Error scraping {website_url}: {e}")
                if attempt < max_retries:
                    sleep_time = 2 ** attempt + random.uniform(0, 2)
                    logger.info(f"Retrying in {sleep_time:.1f} seconds...")
                    time.sleep(sleep_time)
                else:
                    return {
                        'website_url': website_url,
                        'contact_form_url': None,
                        'has_contact_form': False,
                        'about_us_content': None,
                        'company_name': None,
                        'business_type': None,
                        'industry': None,
                        'scraping_status': 'FAILED',
                        'error_message': str(e)
                    }
    
    def _find_contact_form(self, soup: BeautifulSoup, base_url: str) -> Optional[str]:
        """
        Find contact form URL on the website
        
        Args:
            soup: BeautifulSoup object of the page
            base_url: Base URL of the website
            
        Returns:
            Contact form URL if found, None otherwise
        """
        # Common contact form patterns
        contact_patterns = [
            'contact',
            'contact-us',
            'contactus',
            'get-in-touch',
            'reach-us',
            'connect',
            'support'
        ]
        
        # Look for links containing contact-related text
        for link in soup.find_all('a', href=True):
            href = link.get('href', '').lower()
            text = link.get_text().lower()
            
            # Skip about pages that might be misidentified as contact forms
            if any(word in href for word in ['about', 'about-us', 'aboutus', 'company', 'who-we-are', 'our-story']):
                continue
            if any(word in text for word in ['about', 'about us', 'company', 'who we are', 'our story']):
                continue
            
            # Check if link text or href contains contact patterns
            for pattern in contact_patterns:
                if pattern in href or pattern in text:
                    contact_url = urljoin(base_url, link['href'])
                    return contact_url
        
        # Look for forms on the current page
        forms = soup.find_all('form')
        for form in forms:
            form_action = form.get('action')
            if form_action:
                return urljoin(base_url, form_action)
        
        return None
    
    def _extract_about_us_content(self, soup: BeautifulSoup, base_url: str) -> Optional[str]:
        """
        Extract about us content from the website
        
        Args:
            soup: BeautifulSoup object of the page
            base_url: Base URL of the website
            
        Returns:
            About us content if found, None otherwise
        """
        # Look for about us content on the current page
        about_content = self._extract_content_from_page(soup)
        if about_content:
            return about_content
        
        # Look for about us links
        about_patterns = [
            'about',
            'about-us',
            'aboutus',
            'company',
            'our-story',
            'who-we-are'
        ]
        
        for link in soup.find_all('a', href=True):
            href = link.get('href', '').lower()
            text = link.get_text().lower()
            
            for pattern in about_patterns:
                if pattern in href or pattern in text:
                    about_url = urljoin(base_url, link['href'])
                    try:
                        about_response = self.session.get(about_url, timeout=10)
                        about_response.raise_for_status()
                        about_soup = BeautifulSoup(about_response.content, 'html.parser')
                        about_content = self._extract_content_from_page(about_soup)
                        if about_content:
                            return about_content
                    except Exception as e:
                        logger.warning(f"Failed to fetch about page {about_url}: {e}")
                        continue
        
        return None
    
    def _extract_content_from_page(self, soup: BeautifulSoup) -> Optional[str]:
        """
        Extract main content from a page
        
        Args:
            soup: BeautifulSoup object of the page
            
        Returns:
            Extracted content if found, None otherwise
        """
        # Remove script and style elements
        for script in soup(["script", "style"]):
            script.decompose()
        
        # Look for main content areas
        content_selectors = [
            'main',
            'article',
            '.content',
            '.main-content',
            '#content',
            '#main',
            '.about',
            '.about-us'
        ]
        
        for selector in content_selectors:
            content = soup.select_one(selector)
            if content:
                text = content.get_text(strip=True)
                if len(text) > 100:  # Ensure we have substantial content
                    return text[:2000]  # Limit to 2000 characters
        
        # Fallback to body content
        body = soup.find('body')
        if body:
            text = body.get_text(strip=True)
            if len(text) > 100:
                return text[:2000]
        
        return None
    
    def _extract_company_info(self, soup: BeautifulSoup) -> Dict:
        """
        Extract basic company information from the page
        
        Args:
            soup: BeautifulSoup object of the page
            
        Returns:
            Dictionary containing company information
        """
        company_info = {
            'name': None,
            'type': None,
            'industry': None
        }
        
        # Try to extract company name from title
        title = soup.find('title')
        if title:
            title_text = title.get_text(strip=True)
            # Remove common suffixes
            for suffix in [' - Home', ' | Home', ' - Welcome', ' | Welcome']:
                title_text = title_text.replace(suffix, '')
            company_info['name'] = title_text[:100]  # Limit length
        
        # Try to extract from h1
        h1 = soup.find('h1')
        if h1 and not company_info['name']:
            company_info['name'] = h1.get_text(strip=True)[:100]
        
        return company_info
    
    def close(self):
        """Clean up resources"""
        self.session.close() 