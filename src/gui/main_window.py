"""
Main GUI window for the file downloader application
"""

import os
import tkinter as tk
from tkinter import filedialog, messagebox
import customtkinter as ctk

from config.settings import *
from src.gui.components import *
from src.core.scanner import DirectoryScanner
from src.core.downloader import DownloadManager
from src.utils.file_utils import is_valid_url


class MainWindow:
    """Main application window"""
    
    def __init__(self):
        # Initialize main window
        self.root = ctk.CTk()
        self.root.title(APP_NAME)
        self.root.geometry(WINDOW_SIZE)
        self.root.minsize(*MIN_WINDOW_SIZE)
        
        # Initialize core components
        self.scanner = DirectoryScanner()
        self.downloader = DownloadManager()
        
        # Setup callbacks
        self._setup_callbacks()
        
        # GUI variables
        self.download_folder = tk.StringVar(value=DEFAULT_DOWNLOAD_FOLDER)
        
        # Build UI
        self._build_ui()
    
    def _setup_callbacks(self):
        """Setup callbacks for core components"""
        self.scanner.set_progress_callback(self._on_scan_progress)
        self.scanner.set_update_callback(self._on_scan_update)
        
        self.downloader.set_progress_callback(self._on_download_progress)
        self.downloader.set_error_callback(self._on_download_error)
        self.downloader.set_completion_callback(self._on_download_complete)
    
    def _build_ui(self):
        """Build the user interface"""
        # Main container
        main_frame = ctk.CTkFrame(self.root)
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Title
        title_label = ctk.CTkLabel(
            main_frame,
            text="📥 " + APP_NAME.split(" - ")[0],
            font=ctk.CTkFont(size=FONTS['title'][1], weight="bold")
        )
        title_label.pack(pady=(20, 30))
        
        # URL input section
        self._build_url_section(main_frame)
        
        # Folder selection section
        self._build_folder_section(main_frame)
        
        # File list section
        self._build_file_list_section(main_frame)
        
        # Progress section
        self._build_progress_section(main_frame)
        
        # Control buttons section
        self._build_control_section(main_frame)
    
    def _build_url_section(self, parent):
        """Build URL input section"""
        url_frame = ctk.CTkFrame(parent)
        url_frame.pack(fill="x", padx=20, pady=(0, 20))
        
        url_label = ctk.CTkLabel(
            url_frame, 
            text="URL:", 
            font=ctk.CTkFont(size=FONTS['heading'][1], weight="bold")
        )
        url_label.pack(anchor="w", padx=20, pady=(15, 5))
        
        # URL input frame
        url_input_frame = ctk.CTkFrame(url_frame)
        url_input_frame.pack(fill="x", padx=20, pady=(0, 15))
        
        self.url_entry = ctk.CTkEntry(
            url_input_frame,
            placeholder_text="Nhập URL thư mục cần tải (sẽ quét tất cả thư mục con)...",
            height=40,
            font=ctk.CTkFont(size=FONTS['normal'][1])
        )
        self.url_entry.pack(side="left", fill="x", expand=True, padx=(10, 5), pady=10)
        
        self.scan_btn = ctk.CTkButton(
            url_input_frame,
            text="🔍 Quét tất cả thư mục",
            command=self._start_scan,
            height=40,
            width=150
        )
        self.scan_btn.pack(side="right", padx=(5, 10), pady=10)
        
        # Scan control buttons
        self.scan_controls = ControlButtonGroup(url_frame)
        self.scan_controls.pack(fill="x", padx=20, pady=(0, 15))
        
        # Add scan control buttons
        self.scan_controls.add_button(
            "pause", "⏸️ Tạm dừng", self._pause_scan,
            height=35, width=120, state="disabled"
        )
        self.scan_controls.pack_button("pause", side="left", padx=(10, 5), pady=10)
        
        self.scan_controls.add_button(
            "resume", "▶️ Tiếp tục", self._resume_scan,
            height=35, width=120, state="disabled"
        )
        self.scan_controls.pack_button("resume", side="left", padx=(5, 5), pady=10)
        
        self.scan_controls.add_button(
            "cancel", "❌ Hủy", self._cancel_scan,
            height=35, width=120, state="disabled"
        )
        self.scan_controls.pack_button("cancel", side="left", padx=(5, 10), pady=10)
    
    def _build_folder_section(self, parent):
        """Build folder selection section"""
        folder_frame = ctk.CTkFrame(parent)
        folder_frame.pack(fill="x", padx=20, pady=(0, 20))
        
        folder_label = ctk.CTkLabel(
            folder_frame, 
            text="Thư mục lưu:", 
            font=ctk.CTkFont(size=FONTS['heading'][1], weight="bold")
        )
        folder_label.pack(anchor="w", padx=20, pady=(15, 5))
        
        folder_input_frame = ctk.CTkFrame(folder_frame)
        folder_input_frame.pack(fill="x", padx=20, pady=(0, 15))
        
        self.folder_entry = ctk.CTkEntry(
            folder_input_frame,
            textvariable=self.download_folder,
            height=40,
            font=ctk.CTkFont(size=FONTS['normal'][1])
        )
        self.folder_entry.pack(side="left", fill="x", expand=True, padx=(10, 5), pady=10)
        
        folder_btn = ctk.CTkButton(
            folder_input_frame,
            text="📁 Chọn thư mục",
            command=self._select_folder,
            height=40,
            width=150
        )
        folder_btn.pack(side="right", padx=(5, 10), pady=10)
    
    def _build_file_list_section(self, parent):
        """Build file list section"""
        list_frame = ctk.CTkFrame(parent)
        list_frame.pack(fill="both", expand=True, padx=20, pady=(0, 20))
        
        # Header
        list_header_frame = ctk.CTkFrame(list_frame)
        list_header_frame.pack(fill="x", padx=20, pady=(20, 10))
        
        list_label = ctk.CTkLabel(
            list_header_frame, 
            text="🌳 Cấu trúc thư mục & tệp:", 
            font=ctk.CTkFont(size=FONTS['heading'][1], weight="bold")
        )
        list_label.pack(side="left")
        
        self.select_all_btn = ctk.CTkButton(
            list_header_frame,
            text="✅ Chọn tất cả",
            command=self._toggle_select_all,
            height=30,
            width=120
        )
        self.select_all_btn.pack(side="right", padx=(10, 0))
        
        # File list
        self.file_list = ScrollableFileList(list_frame, height=250)
        self.file_list.pack(fill="both", expand=True, padx=20, pady=(0, 10))
        
        # Status
        self.status_display = StatusDisplay(list_frame)
        self.status_display.pack(padx=20, pady=(0, 20))
    
    def _build_progress_section(self, parent):
        """Build progress section"""
        self.progress_display = ProgressDisplay(parent)
        self.progress_display.pack(fill="x", padx=20, pady=(0, 20))
    
    def _build_control_section(self, parent):
        """Build control buttons section"""
        self.control_buttons = ControlButtonGroup(parent)
        self.control_buttons.pack(fill="x", padx=20)
        
        # Download buttons
        self.control_buttons.add_button(
            "download_selected", "⬇️ Tải xuống đã chọn", self._start_download,
            height=45, font=ctk.CTkFont(size=FONTS['heading'][1], weight="bold")
        )
        self.control_buttons.pack_button("download_selected", side="left", padx=(20, 10), pady=20)
        
        self.control_buttons.add_button(
            "download_all", "📥 Tải tất cả", self._download_all,
            height=45, font=ctk.CTkFont(size=FONTS['heading'][1], weight="bold")
        )
        self.control_buttons.pack_button("download_all", side="left", padx=(0, 10), pady=20)
        
        self.control_buttons.add_button(
            "stop", "⏹️ Dừng", self._stop_all,
            height=45, state="disabled"
        )
        self.control_buttons.pack_button("stop", side="right", padx=(10, 20), pady=20)
    
    # Event handlers
    def _start_scan(self):
        """Start scanning process"""
        url = self.url_entry.get().strip()
        if not url:
            messagebox.showerror("Lỗi", "Vui lòng nhập URL!")
            return
        
        if not is_valid_url(url):
            messagebox.showerror("Lỗi", "URL không hợp lệ!")
            return
        
        # Clear previous results
        self.file_list.clear_list()
        
        # Update button states
        self.scan_btn.configure(text="🔄 Đang quét...", state="disabled")
        self.scan_controls.configure_button("pause", state="normal")
        self.scan_controls.configure_button("cancel", state="normal")
        
        # Start scanning
        self.scanner.start_scan(url)
    
    def _pause_scan(self):
        """Pause scanning"""
        self.scanner.pause_scan()
        self.scan_controls.configure_button("pause", state="disabled")
        self.scan_controls.configure_button("resume", state="normal")
    
    def _resume_scan(self):
        """Resume scanning"""
        self.scanner.resume_scan()
        self.scan_controls.configure_button("pause", state="normal")
        self.scan_controls.configure_button("resume", state="disabled")
    
    def _cancel_scan(self):
        """Cancel scanning"""
        self.scanner.cancel_scan()
        self._reset_scan_buttons()
    
    def _reset_scan_buttons(self):
        """Reset scan button states"""
        self.scan_btn.configure(text="🔍 Quét tất cả thư mục", state="normal")
        self.scan_controls.configure_button("pause", state="disabled")
        self.scan_controls.configure_button("resume", state="disabled")
        self.scan_controls.configure_button("cancel", state="disabled")
    
    def _select_folder(self):
        """Select download folder"""
        folder = filedialog.askdirectory()
        if folder:
            self.download_folder.set(folder)
    
    def _toggle_select_all(self):
        """Toggle select all files"""
        selected_indices = self.file_list.get_selected_indices()
        all_selected = len(selected_indices) == len(self.file_list.selected_files)
        
        self.file_list.select_all_files(not all_selected)
        
        self.select_all_btn.configure(
            text="❌ Bỏ chọn tất cả" if not all_selected else "✅ Chọn tất cả"
        )
    
    def _download_all(self):
        """Download all files"""
        self.file_list.select_all_files(True)
        self._start_download()
    
    def _start_download(self):
        """Start downloading selected files"""
        selected_indices = self.file_list.get_selected_indices()
        
        if not selected_indices:
            messagebox.showwarning("Cảnh báo", "Vui lòng chọn ít nhất một tệp để tải!")
            return
        
        download_folder = self.download_folder.get()
        if not download_folder:
            messagebox.showerror("Lỗi", "Vui lòng chọn thư mục lưu!")
            return
        
        # Create download folder
        os.makedirs(download_folder, exist_ok=True)
        
        # Get selected files
        scan_results = self.scanner.get_scan_results()
        selected_files = [scan_results["file_links"][i] for i in selected_indices]
        
        # Update button states
        self.control_buttons.configure_button("download_selected", state="disabled")
        self.control_buttons.configure_button("download_all", state="disabled")
        self.control_buttons.configure_button("stop", state="normal")
        
        # Start download
        self.downloader.start_download(selected_files, download_folder)
    
    def _stop_all(self):
        """Stop all operations"""
        self.scanner.cancel_scan()
        self.downloader.stop_download()
        
        # Reset button states
        self._reset_scan_buttons()
        self.control_buttons.configure_button("download_selected", state="normal")
        self.control_buttons.configure_button("download_all", state="normal")
        self.control_buttons.configure_button("stop", state="disabled")
        
        self.progress_display.reset()
        self.status_display.update_status("cancelled", "Đã dừng tất cả hoạt động")
    
    # Callback handlers
    def _on_scan_progress(self, status_type, message):
        """Handle scan progress updates"""
        self.status_display.update_status(status_type, message)
        
        if status_type in ["error", "cancelled"]:
            self._reset_scan_buttons()
        elif status_type == "completed":
            self._reset_scan_buttons()
            scan_results = self.scanner.get_scan_results()
            self.status_display.update_status(
                "success", 
                f"✅ Hoàn tất! Tìm thấy {scan_results['total_files']} tệp từ {scan_results['total_folders']} thư mục"
            )
    
    def _on_scan_update(self, folder_path, folders, files):
        """Handle real-time scan updates"""
        # Add folder header if needed
        self.file_list.add_folder_header(folder_path, len(files), len(folders))
        
        # Add files to list
        scan_results = self.scanner.get_scan_results()
        start_index = len(scan_results["file_links"]) - len(files)
        
        for i, file_info in enumerate(files):
            file_index = start_index + i
            self.file_list.add_file_item(file_info, file_index)
        
        # Update folder count
        self.file_list.update_folder_count(folder_path, len(files), len(folders))
    
    def _on_download_progress(self, progress_data):
        """Handle download progress updates"""
        self.progress_display.update_progress(progress_data)
    
    def _on_download_error(self, error_message):
        """Handle download errors"""
        messagebox.showerror("Lỗi tải xuống", error_message)
    
    def _on_download_complete(self):
        """Handle download completion"""
        # Reset button states
        self.control_buttons.configure_button("download_selected", state="normal")
        self.control_buttons.configure_button("download_all", state="normal")
        self.control_buttons.configure_button("stop", state="disabled")
        
        # Update progress
        self.progress_display.update_progress("✅ Tải xuống hoàn tất!")
        messagebox.showinfo("Thành công", "Tải xuống hoàn tất!")
    
    def run(self):
        """Run the application"""
        self.root.mainloop()
