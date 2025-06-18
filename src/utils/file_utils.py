"""
Utility functions for file operations and formatting
"""

import os
from urllib.parse import urljoin, urlparse


def format_speed(speed_bytes):
    """Format download speed in human readable format"""
    if speed_bytes < 1024:
        return f"{speed_bytes:.1f} B/s"
    elif speed_bytes < 1024 * 1024:
        return f"{speed_bytes / 1024:.1f} KB/s"
    else:
        return f"{speed_bytes / (1024 * 1024):.1f} MB/s"


def format_size(size_bytes):
    """Format file size in human readable format"""
    if size_bytes < 1024:
        return f"{size_bytes} B"
    elif size_bytes < 1024 * 1024:
        return f"{size_bytes / 1024:.1f} KB"
    elif size_bytes < 1024 * 1024 * 1024:
        return f"{size_bytes / (1024 * 1024):.1f} MB"
    else:
        return f"{size_bytes / (1024 * 1024 * 1024):.1f} GB"


def truncate_filename(filename, max_length=60):
    """Truncate filename if too long"""
    if len(filename) > max_length:
        return filename[:max_length-3] + "..."
    return filename


def create_safe_path(download_folder, relative_path, filename):
    """Create safe file path with folder structure"""
    if relative_path:
        local_folder = os.path.join(download_folder, relative_path)
        os.makedirs(local_folder, exist_ok=True)
        return os.path.join(local_folder, filename)
    else:
        return os.path.join(download_folder, filename)


def is_valid_url(url):
    """Check if URL is valid"""
    try:
        result = urlparse(url)
        return all([result.scheme, result.netloc])
    except:
        return False


def join_url(base_url, href):
    """Safely join URLs"""
    return urljoin(base_url, href)


def sanitize_filename(filename):
    """Remove/replace invalid characters from filename"""
    invalid_chars = '<>:"/\\|?*'
    for char in invalid_chars:
        filename = filename.replace(char, '_')
    return filename


def get_file_extension(filename):
    """Get file extension from filename"""
    return os.path.splitext(filename)[1].lower()


def is_supported_file(filename, supported_types):
    """Check if file is supported for download"""
    extension = get_file_extension(filename)
    return extension in supported_types
