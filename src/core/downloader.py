"""
Core downloading functionality with progress tracking
"""

import time
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
from config.settings import MAX_CONCURRENT_DOWNLOADS
from src.utils.network_utils import NetworkManager
from src.utils.file_utils import create_safe_path, format_speed


class DownloadManager:
    """Handle file downloading with progress tracking"""
    
    def __init__(self):
        self.network_manager = NetworkManager()
        self.is_downloading = False
        self.download_stats = {
            'downloaded_bytes': 0,
            'total_bytes': 0,
            'start_time': 0,
            'current_speed': 0,
            'completed_files': 0,
            'total_files': 0
        }
        self.progress_callback = None
        self.error_callback = None
        self.completion_callback = None
    
    def set_progress_callback(self, callback):
        """Set callback for progress updates"""
        self.progress_callback = callback
    
    def set_error_callback(self, callback):
        """Set callback for error handling"""
        self.error_callback = callback
    
    def set_completion_callback(self, callback):
        """Set callback for completion"""
        self.completion_callback = callback
    
    def start_download(self, files, download_folder):
        """Start downloading files"""
        self.is_downloading = True
        self.download_stats = {
            'downloaded_bytes': 0,
            'total_bytes': 0,
            'start_time': time.time(),
            'current_speed': 0,
            'completed_files': 0,
            'total_files': len(files)
        }
        
        def download_thread():
            self._download_files(files, download_folder)
        
        threading.Thread(target=download_thread, daemon=True).start()
    
    def stop_download(self):
        """Stop downloading"""
        self.is_downloading = False
    
    def _download_files(self, files, download_folder):
        """Download files with thread pool"""
        def download_single_file(file_info):
            if not self.is_downloading:
                return False
            
            try:
                url = file_info["url"]
                filename = file_info["name"]
                relative_path = file_info["relative_path"]
                
                # Create safe file path
                local_path = create_safe_path(download_folder, relative_path, filename)
                
                # Progress callback for this file
                def file_progress(downloaded, total_size):
                    if not self.is_downloading:
                        return
                    
                    # Update stats
                    self.download_stats['downloaded_bytes'] += downloaded - getattr(file_progress, 'last_downloaded', 0)
                    file_progress.last_downloaded = downloaded
                    
                    # Calculate speed
                    elapsed_time = time.time() - self.download_stats['start_time']
                    if elapsed_time > 0:
                        self.download_stats['current_speed'] = self.download_stats['downloaded_bytes'] / elapsed_time
                    
                    # Update progress
                    if self.progress_callback:
                        progress_data = {
                            'current_file': filename,
                            'file_progress': downloaded / total_size if total_size > 0 else 0,
                            'overall_progress': self.download_stats['completed_files'] / self.download_stats['total_files'],
                            'speed': format_speed(self.download_stats['current_speed']),
                            'downloaded_mb': self.download_stats['downloaded_bytes'] / (1024 * 1024)
                        }
                        self.progress_callback(progress_data)
                
                # Download file
                self.network_manager.download_file_stream(url, local_path, file_progress)
                return True
                
            except Exception as e:
                if self.error_callback:
                    self.error_callback(f"Lỗi tải {filename}: {str(e)}")
                return False
        
        # Download with thread pool
        with ThreadPoolExecutor(max_workers=MAX_CONCURRENT_DOWNLOADS) as executor:
            future_to_file = {
                executor.submit(download_single_file, file_info): file_info 
                for file_info in files
            }
            
            for future in as_completed(future_to_file):
                if not self.is_downloading:
                    break
                
                file_info = future_to_file[future]
                try:
                    success = future.result()
                    if success:
                        self.download_stats['completed_files'] += 1
                        
                        # Update overall progress
                        if self.progress_callback:
                            overall_progress = self.download_stats['completed_files'] / self.download_stats['total_files']
                            progress_data = {
                                'current_file': file_info["name"],
                                'file_progress': 1.0,
                                'overall_progress': overall_progress,
                                'speed': format_speed(self.download_stats['current_speed']),
                                'downloaded_mb': self.download_stats['downloaded_bytes'] / (1024 * 1024)
                            }
                            self.progress_callback(progress_data)
                            
                except Exception as e:
                    if self.error_callback:
                        self.error_callback(f"Lỗi xử lý {file_info['name']}: {str(e)}")
        
        # Download completed
        if self.completion_callback:
            self.completion_callback()
    
    def get_download_stats(self):
        """Get current download statistics"""
        return self.download_stats.copy()
