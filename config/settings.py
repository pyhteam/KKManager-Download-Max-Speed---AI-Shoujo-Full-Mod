"""
Configuration settings for KK Manager Download
"""

import os
import customtkinter as ctk

# Application Settings
APP_NAME = "KKManager Download Max Speed - AI Shoujo Full Mod"
APP_VERSION = "2.0.0"
WINDOW_SIZE = "1000x700"
MIN_WINDOW_SIZE = (800, 600)

# Theme Settings
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

# Colors
COLORS = {
    'primary': "#4A90E2",
    'secondary': "#2B2B2B", 
    'hover': "#343638",
    'success': "#28a745",
    'warning': "#ffc107",
    'danger': "#dc3545",
    'text_gray': "gray"
}

# File Types to Download
SUPPORTED_FILE_TYPES = [
    # Archives
    ".zip", ".rar", ".exe", ".7z", ".tar", ".gz", ".bz2",
    # Documents
    ".pdf", ".txt", ".doc", ".docx", ".xlsx", ".pptx",
    # Videos
    ".mp4", ".avi", ".mkv", ".wmv", ".mov", ".flv",
    # Audio
    ".mp3", ".wav", ".flac", ".aac", ".ogg",
    # Images
    ".jpg", ".jpeg", ".png", ".gif", ".bmp", ".webp",
    # Code/Executable
    ".dll", ".bat", ".sh", ".py", ".js", ".css", ".html"
]

# Network Settings
REQUEST_TIMEOUT = 10  # seconds
MAX_CONCURRENT_DOWNLOADS = 3
CHUNK_SIZE = 8192
USER_AGENT = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'

# Scanning Settings
MAX_SCAN_DEPTH = 15
SCAN_SLEEP_TIME = 0.1  # seconds when paused

# Default Paths
DEFAULT_DOWNLOAD_FOLDER = os.path.join(os.getcwd(), "downloaded_files")

# UI Settings
SCROLL_COLORS = {
    'button': "#2B2B2B",
    'button_hover': "#343638"
}

FONTS = {
    'title': ("Arial", 24, "bold"),
    'heading': ("Arial", 14, "bold"),
    'normal': ("Arial", 12),
    'small': ("Arial", 10),
    'tiny': ("Arial", 11)
}
