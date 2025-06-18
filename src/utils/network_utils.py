"""
Network utilities for web scraping and downloading
"""

import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from config.settings import REQUEST_TIMEOUT, USER_AGENT


class NetworkManager:
    """Handle all network operations"""
    
    def __init__(self):
        self.headers = {'User-Agent': USER_AGENT}
        self.timeout = REQUEST_TIMEOUT
    
    def get_page_content(self, url):
        """Get page content with error handling"""
        try:
            response = requests.get(url, headers=self.headers, timeout=self.timeout)
            response.raise_for_status()
            return response.text
        except requests.RequestException as e:
            raise Exception(f"Failed to fetch {url}: {str(e)}")
    
    def parse_directory_links(self, html_content, base_url):
        """Parse HTML content to extract file and folder links"""
        soup = BeautifulSoup(html_content, "html.parser")
        folders = []
        files = []
        
        for a in soup.find_all("a", href=True):
            href = a["href"]
            
            # Skip parent directory links
            if href in ["../", "./"]:
                continue
            
            full_url = urljoin(base_url, href)
            name = href.rstrip("/")
            
            if href.endswith("/"):  # It's a folder
                folders.append({
                    "name": name,
                    "url": full_url
                })
            else:  # It's a file
                files.append({
                    "name": name, 
                    "url": full_url,
                    "href": href
                })
        
        return folders, files
    
    def get_file_size(self, url):
        """Get file size from URL headers"""
        try:
            response = requests.head(url, headers=self.headers, timeout=self.timeout)
            return int(response.headers.get('content-length', 0))
        except:
            return 0
    
    def download_file_stream(self, url, file_path, progress_callback=None):
        """Download file with streaming and progress callback"""
        try:
            response = requests.get(url, stream=True, headers=self.headers, timeout=30)
            response.raise_for_status()
            
            total_size = int(response.headers.get('content-length', 0))
            downloaded = 0
            
            with open(file_path, 'wb') as file:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        file.write(chunk)
                        downloaded += len(chunk)
                        
                        if progress_callback:
                            progress_callback(downloaded, total_size)
            
            return True
        except Exception as e:
            raise Exception(f"Download failed: {str(e)}")
