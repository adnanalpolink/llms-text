"""
Content extraction and web scraping utilities
"""

import requests
from bs4 import BeautifulSoup
import xml.etree.ElementTree as ET
from urllib.parse import urljoin, urlparse
import pandas as pd
from typing import List, Dict, Optional, Tuple
import re
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from config import (
    DEFAULT_HEADERS, REQUEST_TIMEOUT, MAX_RETRIES, 
    CATEGORY_KEYWORDS, MD_EXTENSIONS
)


class ContentExtractor:
    """Handles web content extraction and processing"""
    
    def __init__(self, use_js_rendering: bool = False):
        """
        Initialize content extractor
        
        Args:
            use_js_rendering: Whether to use Playwright for JavaScript rendering
        """
        self.use_js_rendering = use_js_rendering
        self.session = requests.Session()
        self.session.headers.update(DEFAULT_HEADERS)
        
        if use_js_rendering:
            try:
                from playwright.sync_api import sync_playwright
                self.playwright = sync_playwright().start()
                self.browser = self.playwright.chromium.launch(headless=True)
                self.js_enabled = True
            except ImportError:
                print("Playwright not available. Install with: pip install playwright")
                self.js_enabled = False
            except Exception as e:
                print(f"Failed to initialize Playwright: {e}")
                self.js_enabled = False
        else:
            self.js_enabled = False
    
    def __del__(self):
        """Cleanup resources"""
        if hasattr(self, 'browser') and self.browser:
            self.browser.close()
        if hasattr(self, 'playwright') and self.playwright:
            self.playwright.stop()
    
    def extract_urls_from_sitemap(self, sitemap_url: str) -> List[str]:
        """
        Extract URLs from sitemap, handling sitemap indexes
        
        Args:
            sitemap_url: URL of the sitemap
            
        Returns:
            List of extracted URLs
        """
        urls = []
        
        try:
            response = self.session.get(sitemap_url, timeout=REQUEST_TIMEOUT)
            response.raise_for_status()
            
            # Parse XML
            root = ET.fromstring(response.content)
            
            # Handle sitemap index
            sitemap_namespaces = {
                'sm': 'http://www.sitemaps.org/schemas/sitemap/0.9'
            }
            
            # Check if this is a sitemap index
            sitemaps = root.findall('.//sm:sitemap/sm:loc', sitemap_namespaces)
            if sitemaps:
                # This is a sitemap index, recursively process each sitemap
                for sitemap in sitemaps:
                    nested_urls = self.extract_urls_from_sitemap(sitemap.text)
                    urls.extend(nested_urls)
            else:
                # This is a regular sitemap, extract URLs
                url_elements = root.findall('.//sm:url/sm:loc', sitemap_namespaces)
                urls = [url.text for url in url_elements if url.text]
                
        except Exception as e:
            print(f"Error processing sitemap {sitemap_url}: {e}")
            
        return urls
    
    def extract_urls_from_csv(self, csv_file) -> List[str]:
        """
        Extract URLs from uploaded CSV file
        
        Args:
            csv_file: Uploaded CSV file object
            
        Returns:
            List of extracted URLs
        """
        try:
            df = pd.read_csv(csv_file)
            
            # Try to find URL column intelligently
            url_columns = ['url', 'link', 'href', 'page', 'address', 'site']
            url_column = None
            
            for col in df.columns:
                if col.lower() in url_columns:
                    url_column = col
                    break
            
            # If no obvious URL column, use first column
            if url_column is None:
                url_column = df.columns[0]
            
            urls = df[url_column].dropna().astype(str).tolist()
            
            # Filter out non-URL entries
            url_pattern = re.compile(r'https?://')
            urls = [url for url in urls if url_pattern.match(url)]
            
            return urls
            
        except Exception as e:
            print(f"Error processing CSV: {e}")
            return []
    
    def categorize_urls(self, urls: List[str]) -> Dict[str, List[str]]:
        """
        Categorize URLs based on keywords in the URL path
        
        Args:
            urls: List of URLs to categorize
            
        Returns:
            Dictionary with categories as keys and URL lists as values
        """
        categorized = {category: [] for category in CATEGORY_KEYWORDS.keys()}
        categorized["Other"] = []
        
        for url in urls:
            url_lower = url.lower()
            categorized_flag = False
            
            for category, keywords in CATEGORY_KEYWORDS.items():
                if any(keyword in url_lower for keyword in keywords):
                    categorized[category].append(url)
                    categorized_flag = True
                    break
            
            if not categorized_flag:
                categorized["Other"].append(url)
        
        # Remove empty categories
        return {k: v for k, v in categorized.items() if v}
    
    def fetch_page_content(self, url: str) -> Optional[BeautifulSoup]:
        """
        Fetch page content using requests or Playwright
        
        Args:
            url: URL to fetch
            
        Returns:
            BeautifulSoup object or None if failed
        """
        if self.js_enabled and self.use_js_rendering:
            return self._fetch_with_playwright(url)
        else:
            return self._fetch_with_requests(url)
    
    def _fetch_with_requests(self, url: str) -> Optional[BeautifulSoup]:
        """Fetch content using requests library"""
        for attempt in range(MAX_RETRIES):
            try:
                response = self.session.get(url, timeout=REQUEST_TIMEOUT)
                response.raise_for_status()
                return BeautifulSoup(response.content, 'html.parser')
            except Exception as e:
                if attempt == MAX_RETRIES - 1:
                    print(f"Failed to fetch {url}: {e}")
                else:
                    time.sleep(1)  # Brief delay before retry
        return None
    
    def _fetch_with_playwright(self, url: str) -> Optional[BeautifulSoup]:
        """Fetch content using Playwright for JavaScript rendering"""
        try:
            page = self.browser.new_page()
            page.goto(url, wait_until='networkidle', timeout=30000)
            content = page.content()
            page.close()
            return BeautifulSoup(content, 'html.parser')
        except Exception as e:
            print(f"Playwright failed for {url}: {e}")
            return None

    def extract_page_info(self, soup: BeautifulSoup, url: str) -> Tuple[str, str, str]:
        """
        Extract title, description, and main content from page

        Args:
            soup: BeautifulSoup object of the page
            url: Original URL for fallback title generation

        Returns:
            Tuple of (title, description, main_content)
        """
        # Extract title
        title_tag = soup.find('title')
        title = title_tag.get_text().strip() if title_tag else ""

        if not title:
            # Generate title from URL slug
            path = urlparse(url).path
            title = path.split('/')[-1] or path.split('/')[-2] or "Page"
            title = title.replace('-', ' ').replace('_', ' ').title()

        # Extract meta description
        meta_desc = soup.find('meta', attrs={'name': 'description'})
        description = ""
        if meta_desc and meta_desc.get('content'):
            description = meta_desc['content'].strip()

        # Extract main content (remove nav, footer, sidebar)
        main_content = ""

        # Remove unwanted elements
        for element in soup(['nav', 'footer', 'aside', 'header', 'script', 'style']):
            element.decompose()

        # Try to find main content area
        main_areas = soup.find_all(['main', 'article', 'div'],
                                  class_=re.compile(r'content|main|article|post', re.I))

        if main_areas:
            main_content = ' '.join([area.get_text() for area in main_areas])
        else:
            # Fallback to all paragraph text
            paragraphs = soup.find_all('p')
            main_content = ' '.join([p.get_text() for p in paragraphs])

        # Clean up content
        main_content = re.sub(r'\s+', ' ', main_content).strip()

        # If no description, use first paragraph
        if not description and main_content:
            sentences = main_content.split('.')
            if sentences and len(sentences[0].strip()) > 20:
                description = sentences[0].strip() + "."

        return title, description, main_content

    def find_md_link(self, url: str) -> Optional[str]:
        """
        Try to find corresponding markdown file for documentation URLs

        Args:
            url: Original URL to check

        Returns:
            Markdown file URL if found, None otherwise
        """
        base_url = url.rstrip('/')

        for extension in MD_EXTENSIONS:
            md_url = base_url + extension
            try:
                response = self.session.head(md_url, timeout=10)
                if response.status_code == 200:
                    return md_url
            except:
                continue

        return None

    def process_url(self, url: str, ai_client=None) -> Dict[str, str]:
        """
        Process a single URL to extract all information

        Args:
            url: URL to process
            ai_client: Optional OpenRouter client for AI descriptions

        Returns:
            Dictionary with url, title, description, md_link
        """
        result = {
            'url': url,
            'title': 'Page',
            'description': 'Resource information',
            'md_link': None
        }

        # Fetch page content
        soup = self.fetch_page_content(url)
        if not soup:
            return result

        # Extract basic info
        title, description, main_content = self.extract_page_info(soup, url)
        result['title'] = title

        # Generate description
        if ai_client and main_content:
            ai_description = ai_client.generate_description(main_content, title)
            result['description'] = ai_description
        elif description:
            result['description'] = description
        elif main_content:
            # Use first sentence as fallback
            sentences = main_content.split('.')
            if sentences and len(sentences[0].strip()) > 10:
                result['description'] = sentences[0].strip() + "."

        # Try to find markdown link for documentation
        if any(keyword in url.lower() for keyword in ['guide', 'doc', 'api', 'reference']):
            md_link = self.find_md_link(url)
            if md_link:
                result['md_link'] = md_link

        return result

    def process_urls_parallel(self, urls: List[str], ai_client=None,
                            progress_callback=None) -> Dict[str, List[Dict]]:
        """
        Process multiple URLs in parallel with progress tracking

        Args:
            urls: List of URLs to process
            ai_client: Optional OpenRouter client
            progress_callback: Optional callback function for progress updates

        Returns:
            Dictionary with categorized processed URLs
        """
        # Categorize URLs first
        categorized_urls = self.categorize_urls(urls)
        results = {}

        total_urls = len(urls)
        processed_count = 0

        for category, category_urls in categorized_urls.items():
            if progress_callback:
                progress_callback(f"Processing {len(category_urls)} URLs for {category}...")

            category_results = []

            # Process URLs in parallel batches
            with ThreadPoolExecutor(max_workers=5) as executor:
                future_to_url = {
                    executor.submit(self.process_url, url, ai_client): url
                    for url in category_urls
                }

                for future in as_completed(future_to_url):
                    try:
                        result = future.result()
                        category_results.append(result)
                        processed_count += 1

                        if progress_callback:
                            progress = processed_count / total_urls
                            progress_callback(f"Processed {processed_count}/{total_urls} URLs", progress)

                    except Exception as e:
                        url = future_to_url[future]
                        print(f"Error processing {url}: {e}")
                        processed_count += 1

            results[category] = category_results

        return results


class RobotsChecker:
    """Utility class for checking robots.txt crawler access"""

    @staticmethod
    def check_crawler_access(domain: str, crawlers: List[str]) -> Dict[str, any]:
        """
        Check if domain blocks specific crawlers in robots.txt

        Args:
            domain: Domain to check (e.g., 'example.com')
            crawlers: List of crawler user agents to check

        Returns:
            Dictionary with check results
        """
        result = {
            'domain': domain,
            'robots_url': f"https://{domain}/robots.txt",
            'accessible': True,
            'blocked_crawlers': [],
            'robots_content': '',
            'error': None
        }

        try:
            response = requests.get(result['robots_url'], timeout=10)

            if response.status_code == 404:
                result['error'] = "No robots.txt file found"
                return result

            if response.status_code != 200:
                result['error'] = f"HTTP {response.status_code} error"
                return result

            robots_content = response.text
            result['robots_content'] = robots_content

            # Parse robots.txt for crawler blocks
            lines = robots_content.split('\n')
            current_user_agent = None

            for line in lines:
                line = line.strip()
                if not line or line.startswith('#'):
                    continue

                if line.lower().startswith('user-agent:'):
                    current_user_agent = line.split(':', 1)[1].strip()
                elif line.lower().startswith('disallow:') and current_user_agent:
                    disallow_path = line.split(':', 1)[1].strip()

                    # Check if this affects our crawlers
                    if current_user_agent == '*' or current_user_agent in crawlers:
                        if disallow_path == '/':
                            # Complete block
                            if current_user_agent == '*':
                                result['blocked_crawlers'].extend(
                                    [c for c in crawlers if c not in result['blocked_crawlers']]
                                )
                            elif current_user_agent not in result['blocked_crawlers']:
                                result['blocked_crawlers'].append(current_user_agent)

            result['accessible'] = len(result['blocked_crawlers']) == 0

        except Exception as e:
            result['error'] = str(e)

        return result
