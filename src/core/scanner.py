"""
Core scanning functionality for directory traversal
"""

import os
import time
import threading
from config.settings import SUPPORTED_FILE_TYPES, MAX_SCAN_DEPTH, SCAN_SLEEP_TIME
from src.utils.network_utils import NetworkManager
from src.utils.file_utils import is_supported_file


class DirectoryScanner:
    """Handle recursive directory scanning"""
    
    def __init__(self):
        self.network_manager = NetworkManager()
        self.is_scanning = False
        self.scan_paused = False
        self.file_links = []
        self.folder_structure = {}
        self.progress_callback = None
        self.update_callback = None
    
    def set_progress_callback(self, callback):
        """Set callback for progress updates"""
        self.progress_callback = callback
    
    def set_update_callback(self, callback):
        """Set callback for real-time updates"""
        self.update_callback = callback
    
    def start_scan(self, url):
        """Start scanning process"""
        self.is_scanning = True
        self.scan_paused = False
        self.file_links = []
        self.folder_structure = {}
        
        def scan_thread():
            try:
                self._scan_recursive(url, "", 0)
            except Exception as e:
                if self.progress_callback:
                    self.progress_callback("error", str(e))
        
        threading.Thread(target=scan_thread, daemon=True).start()
    
    def pause_scan(self):
        """Pause scanning"""
        self.scan_paused = True
        if self.progress_callback:
            self.progress_callback("paused", "Quét đã tạm dừng")
    
    def resume_scan(self):
        """Resume scanning"""
        self.scan_paused = False
        if self.progress_callback:
            self.progress_callback("resumed", "Đang tiếp tục quét")
    
    def cancel_scan(self):
        """Cancel scanning"""
        self.is_scanning = False
        self.scan_paused = False
        if self.progress_callback:
            self.progress_callback("cancelled", "Đã hủy quét")
    
    def _scan_recursive(self, url, relative_path, depth):
        """Recursive scanning implementation"""
        if depth > MAX_SCAN_DEPTH or not self.is_scanning:
            return
        
        # Wait if paused
        while self.scan_paused and self.is_scanning:
            time.sleep(SCAN_SLEEP_TIME)
        
        if not self.is_scanning:
            return
        
        try:
            # Update progress
            display_path = relative_path if relative_path else "thư mục gốc"
            if self.progress_callback:
                self.progress_callback("scanning", f"Đang quét: {display_path} (Độ sâu: {depth})")
            
            # Get page content
            html_content = self.network_manager.get_page_content(url)
            folders, all_files = self.network_manager.parse_directory_links(html_content, url)
            
            # Filter supported files
            files = []
            for file_info in all_files:
                if is_supported_file(file_info["href"], SUPPORTED_FILE_TYPES):
                    file_info.update({
                        "relative_path": relative_path,
                        "full_path": os.path.join(relative_path, file_info["name"]) if relative_path else file_info["name"]
                    })
                    files.append(file_info)
                    self.file_links.append(file_info)
            
            # Store structure
            self.folder_structure[relative_path] = {
                "folders": folders,
                "files": files
            }
            
            # Update UI in real-time
            if self.update_callback and (files or folders):
                self.update_callback(relative_path, folders, files)
            
            # Continue scanning subfolders
            for folder in folders:
                if self.is_scanning:
                    new_relative_path = os.path.join(relative_path, folder["name"]) if relative_path else folder["name"]
                    self._scan_recursive(
                        folder["url"],
                        new_relative_path,
                        depth + 1
                    )
        
        except Exception as e:
            print(f"Lỗi khi quét {url}: {str(e)}")
            if self.progress_callback:
                self.progress_callback("error", f"Lỗi quét {relative_path}: {str(e)}")
    
    def get_scan_results(self):
        """Get current scan results"""
        return {
            "file_links": self.file_links,
            "folder_structure": self.folder_structure,
            "total_files": len(self.file_links),
            "total_folders": len(self.folder_structure)
        }
