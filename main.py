import os
import sys
import time
import requests
from bs4 import BeautifulSoup
from concurrent.futures import ThreadPoolExecutor, as_completed
import threading
from urllib.parse import urljoin, urlparse
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import customtkinter as ctk
from collections import defaultdict

# Set appearance mode and color theme
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

class FileDownloaderGUI:
    def __init__(self):
        self.root = ctk.CTk()
        self.root.title("KKManager Download Max Speed - AI Shoujo Full Mod")
        self.root.geometry("1000x700")
        self.root.minsize(800, 600)
        
        # Variables
        self.download_folder = tk.StringVar(value=os.path.join(os.getcwd(), "downloaded_files"))
        self.file_links = []
        self.folder_structure = {}
        self.selected_files = {}
        self.is_downloading = False
        self.is_scanning = False
        self.download_stats = {
            'downloaded_bytes': 0,
            'total_bytes': 0,
            'start_time': 0,
            'current_speed': 0
        }
        
        self.setup_ui()
        
    def setup_ui(self):
        # Main container
        main_frame = ctk.CTkFrame(self.root)
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Title
        title_label = ctk.CTkLabel(
            main_frame, 
            text="📥 File Downloader (Recursive)", 
            font=ctk.CTkFont(size=24, weight="bold")
        )
        title_label.pack(pady=(20, 30))
        
        # URL Input Section
        url_frame = ctk.CTkFrame(main_frame)
        url_frame.pack(fill="x", padx=20, pady=(0, 20))
        
        url_label = ctk.CTkLabel(url_frame, text="URL:", font=ctk.CTkFont(size=14, weight="bold"))
        url_label.pack(anchor="w", padx=20, pady=(15, 5))
        
        url_input_frame = ctk.CTkFrame(url_frame)
        url_input_frame.pack(fill="x", padx=20, pady=(0, 15))
        
        self.url_entry = ctk.CTkEntry(
            url_input_frame, 
            placeholder_text="Nhập URL thư mục cần tải (sẽ quét tất cả thư mục con)...",
            height=40,
            font=ctk.CTkFont(size=12)
        )
        self.url_entry.pack(side="left", fill="x", expand=True, padx=(10, 5), pady=10)
        
        self.load_btn = ctk.CTkButton(
            url_input_frame,
            text="🔍 Quét tất cả thư mục",
            command=self.load_file_list,
            height=40,
            width=150
        )
        self.load_btn.pack(side="right", padx=(5, 10), pady=10)
        
        # Download folder selection
        folder_frame = ctk.CTkFrame(main_frame)
        folder_frame.pack(fill="x", padx=20, pady=(0, 20))
        
        folder_label = ctk.CTkLabel(folder_frame, text="Thư mục lưu:", font=ctk.CTkFont(size=14, weight="bold"))
        folder_label.pack(anchor="w", padx=20, pady=(15, 5))
        
        folder_input_frame = ctk.CTkFrame(folder_frame)
        folder_input_frame.pack(fill="x", padx=20, pady=(0, 15))
        
        self.folder_entry = ctk.CTkEntry(
            folder_input_frame,
            textvariable=self.download_folder,
            height=40,
            font=ctk.CTkFont(size=12)
        )
        self.folder_entry.pack(side="left", fill="x", expand=True, padx=(10, 5), pady=10)
        
        folder_btn = ctk.CTkButton(
            folder_input_frame,
            text="📁 Chọn thư mục",
            command=self.select_folder,
            height=40,
            width=150
        )
        folder_btn.pack(side="right", padx=(5, 10), pady=10)
        
        # File list section
        list_frame = ctk.CTkFrame(main_frame)
        list_frame.pack(fill="both", expand=True, padx=20, pady=(0, 20))
        
        list_header_frame = ctk.CTkFrame(list_frame)
        list_header_frame.pack(fill="x", padx=20, pady=(20, 10))
        
        list_label = ctk.CTkLabel(list_header_frame, text="🌳 Cấu trúc thư mục & tệp:", font=ctk.CTkFont(size=14, weight="bold"))
        list_label.pack(side="left")
        
        self.select_all_btn = ctk.CTkButton(
            list_header_frame,
            text="✅ Chọn tất cả",
            command=self.select_all_files,
            height=30,
            width=120
        )
        self.select_all_btn.pack(side="right", padx=(10, 0))
        
        # Scrollable frame for file list
        self.file_list_frame = ctk.CTkScrollableFrame(list_frame, height=200)
        self.file_list_frame.pack(fill="both", expand=True, padx=20, pady=(0, 10))
        
        # Status label for scanning
        self.status_label = ctk.CTkLabel(
            list_frame,
            text="Sẵn sàng quét thư mục...",
            font=ctk.CTkFont(size=11),
            text_color="gray"
        )
        self.status_label.pack(padx=20, pady=(0, 20))
        
        # Progress section
        progress_frame = ctk.CTkFrame(main_frame)
        progress_frame.pack(fill="x", padx=20, pady=(0, 20))
        
        progress_label = ctk.CTkLabel(progress_frame, text="📊 Tiến trình tải:", font=ctk.CTkFont(size=14, weight="bold"))
        progress_label.pack(anchor="w", padx=20, pady=(15, 5))
        
        self.progress_bar = ctk.CTkProgressBar(progress_frame, height=20)
        self.progress_bar.pack(fill="x", padx=20, pady=(0, 10))
        self.progress_bar.set(0)
        
        self.progress_info = ctk.CTkLabel(
            progress_frame, 
            text="Sẵn sàng tải xuống",
            font=ctk.CTkFont(size=12)
        )
        self.progress_info.pack(padx=20, pady=(0, 15))
        
        # Download controls
        control_frame = ctk.CTkFrame(main_frame)
        control_frame.pack(fill="x", padx=20)
        
        self.download_btn = ctk.CTkButton(
            control_frame,
            text="⬇️ Tải xuống đã chọn",
            command=self.start_download,
            height=45,
            font=ctk.CTkFont(size=14, weight="bold")
        )
        self.download_btn.pack(side="left", padx=(20, 10), pady=20)
        
        self.download_all_btn = ctk.CTkButton(
            control_frame,
            text="📥 Tải tất cả",
            command=self.download_all,
            height=45,
            font=ctk.CTkFont(size=14, weight="bold")
        )
        self.download_all_btn.pack(side="left", padx=(0, 10), pady=20)
        
        self.stop_btn = ctk.CTkButton(
            control_frame,
            text="⏹️ Dừng",
            command=self.stop_download,
            height=45,
            state="disabled"
        )
        self.stop_btn.pack(side="right", padx=(10, 20), pady=20)
        
    def select_folder(self):
        folder = filedialog.askdirectory()
        if folder:
            self.download_folder.set(folder)
    
    def load_file_list(self):
        url = self.url_entry.get().strip()
        if not url:
            messagebox.showerror("Lỗi", "Vui lòng nhập URL!")
            return
        
        if self.is_scanning:
            return
        
        self.is_scanning = True
        self.load_btn.configure(text="🔄 Đang quét...", state="disabled")
        self.status_label.configure(text="Đang quét thư mục gốc...")
        
        def load_in_thread():
            try:
                self.file_links = []
                self.folder_structure = {}
                self.scan_directory_recursive(url, "")
                self.root.after(0, self.update_file_list)
            except Exception as e:
                self.root.after(0, lambda: messagebox.showerror("Lỗi", f"Không thể quét thư mục: {str(e)}"))
            finally:
                self.is_scanning = False
                self.root.after(0, lambda: self.load_btn.configure(text="🔍 Quét tất cả thư mục", state="normal"))
                self.root.after(0, lambda: self.status_label.configure(text=f"Hoàn tất! Tìm thấy {len(self.file_links)} tệp"))
        
        threading.Thread(target=load_in_thread, daemon=True).start()
    
    def scan_directory_recursive(self, url, relative_path, max_depth=10, current_depth=0):
        """Quét tất cả thư mục và tệp trong thư mục một cách đệ quy"""
        if current_depth > max_depth:
            return
        
        if not self.is_scanning:
            return
        
        try:
            # Update status
            display_path = relative_path if relative_path else "thư mục gốc"
            self.root.after(0, lambda: self.status_label.configure(text=f"Đang quét: {display_path}"))
            
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
            
            response = requests.get(url, headers=headers, timeout=30)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, "html.parser")
            
            folders = []
            files = []
            
            # Parse all links
            for a in soup.find_all("a", href=True):
                href = a["href"]
                
                # Skip parent directory links
                if href in ["../", "./"]:
                    continue
                
                full_url = urljoin(url, href)
                name = href.rstrip("/")
                
                if href.endswith("/"):  # It's a folder
                    folders.append({"name": name, "url": full_url, "relative_path": os.path.join(relative_path, name)})
                else:  # It's a file
                    # Check if it's a downloadable file
                    if any(href.lower().endswith(ext) for ext in [".zip", ".rar", ".exe", ".7z", ".tar", ".gz", ".bz2", ".pdf", ".txt", ".doc", ".docx", ".mp4", ".avi", ".mkv", ".mp3", ".wav"]):
                        file_info = {
                            "name": name,
                            "url": full_url,
                            "relative_path": relative_path,
                            "full_path": os.path.join(relative_path, name) if relative_path else name
                        }
                        files.append(file_info)
                        self.file_links.append(file_info)
            
            # Store folder structure
            if relative_path not in self.folder_structure:
                self.folder_structure[relative_path] = {"folders": [], "files": []}
            
            self.folder_structure[relative_path]["folders"] = folders
            self.folder_structure[relative_path]["files"] = files
            
            # Recursively scan subfolders
            for folder in folders:
                if self.is_scanning:
                    self.scan_directory_recursive(folder["url"], folder["relative_path"], max_depth, current_depth + 1)
                    
        except Exception as e:
            print(f"Lỗi khi quét {url}: {str(e)}")
    
    def update_file_list(self):
        # Clear existing widgets
        for widget in self.file_list_frame.winfo_children():
            widget.destroy()
        
        self.selected_files = {}
        
        if not self.file_links:
            no_files_label = ctk.CTkLabel(
                self.file_list_frame, 
                text="Không tìm thấy tệp nào để tải.",
                font=ctk.CTkFont(size=12)
            )
            no_files_label.pack(pady=20)
            return
        
        # Group files by folder for better organization
        files_by_folder = defaultdict(list)
        for i, file_info in enumerate(self.file_links):
            folder_path = file_info["relative_path"] or "/"
            files_by_folder[folder_path].append((i, file_info))
        
        # Display files organized by folder
        for folder_path in sorted(files_by_folder.keys()):
            if folder_path != "/":
                # Folder header
                folder_frame = ctk.CTkFrame(self.file_list_frame)
                folder_frame.pack(fill="x", padx=5, pady=(10, 2))
                
                folder_label = ctk.CTkLabel(
                    folder_frame,
                    text=f"📁 {folder_path}",
                    font=ctk.CTkFont(size=12, weight="bold"),
                    text_color="#4A90E2"
                )
                folder_label.pack(side="left", padx=10, pady=5)
            
            # Files in this folder
            for i, file_info in files_by_folder[folder_path]:
                file_frame = ctk.CTkFrame(self.file_list_frame)
                file_frame.pack(fill="x", padx=15 if folder_path != "/" else 5, pady=2)
                
                var = tk.BooleanVar()
                self.selected_files[i] = var
                
                display_name = file_info["name"]
                if len(display_name) > 50:
                    display_name = display_name[:47] + "..."
                
                checkbox = ctk.CTkCheckBox(
                    file_frame,
                    text=f"  📄 {display_name}",
                    variable=var,
                    font=ctk.CTkFont(size=11)
                )
                checkbox.pack(side="left", padx=10, pady=5)
    
    def select_all_files(self):
        all_selected = all(var.get() for var in self.selected_files.values())
        
        for var in self.selected_files.values():
            var.set(not all_selected)
        
        self.select_all_btn.configure(
            text="❌ Bỏ chọn tất cả" if not all_selected else "✅ Chọn tất cả"
        )
    
    def download_all(self):
        for var in self.selected_files.values():
            var.set(True)
        self.start_download()
    
    def start_download(self):
        selected_indices = [i for i, var in self.selected_files.items() if var.get()]
        
        if not selected_indices:
            messagebox.showwarning("Cảnh báo", "Vui lòng chọn ít nhất một tệp để tải!")
            return
        
        download_folder = self.download_folder.get()
        if not download_folder:
            messagebox.showerror("Lỗi", "Vui lòng chọn thư mục lưu!")
            return
        
        os.makedirs(download_folder, exist_ok=True)
        
        self.is_downloading = True
        self.download_btn.configure(state="disabled")
        self.download_all_btn.configure(state="disabled")
        self.stop_btn.configure(state="normal")
        
        selected_files = [self.file_links[i] for i in selected_indices]
        
        def download_in_thread():
            self.download_files(selected_files, download_folder)
        
        threading.Thread(target=download_in_thread, daemon=True).start()
    
    def download_files(self, files, download_folder):
        self.download_stats = {
            'downloaded_bytes': 0,
            'total_bytes': 0,
            'start_time': time.time(),
            'current_speed': 0
        }
        
        # Get total file sizes
        total_files = len(files)
        completed_files = 0
        
        def download_file(file_info):
            if not self.is_downloading:
                return
            
            try:
                url = file_info["url"]
                filename = file_info["name"]
                relative_path = file_info["relative_path"]
                
                # Create folder structure
                if relative_path:
                    local_folder = os.path.join(download_folder, relative_path)
                    os.makedirs(local_folder, exist_ok=True)
                    local_path = os.path.join(local_folder, filename)
                else:
                    local_path = os.path.join(download_folder, filename)
                
                response = requests.get(url, stream=True, timeout=30)
                response.raise_for_status()
                
                total_size = int(response.headers.get('content-length', 0))
                
                with open(local_path, 'wb') as file:
                    downloaded = 0
                    start_time = time.time()
                    
                    for chunk in response.iter_content(chunk_size=8192):
                        if not self.is_downloading:
                            return
                        
                        if chunk:
                            file.write(chunk)
                            downloaded += len(chunk)
                            self.download_stats['downloaded_bytes'] += len(chunk)
                            
                            # Calculate speed
                            elapsed_time = time.time() - self.download_stats['start_time']
                            if elapsed_time > 0:
                                self.download_stats['current_speed'] = self.download_stats['downloaded_bytes'] / elapsed_time
                            
                            # Update progress
                            if total_size > 0:
                                progress = downloaded / total_size
                                self.root.after(0, lambda p=progress, f=filename: self.update_progress(p, f))
                
                return True
            except Exception as e:
                self.root.after(0, lambda: messagebox.showerror("Lỗi", f"Lỗi tải {filename}: {str(e)}"))
                return False
        
        # Download files with thread pool
        with ThreadPoolExecutor(max_workers=3) as executor:
            future_to_file = {executor.submit(download_file, file_info): file_info for file_info in files}
            
            for future in as_completed(future_to_file):
                if not self.is_downloading:
                    break
                
                file_info = future_to_file[future]
                try:
                    success = future.result()
                    if success:
                        completed_files += 1
                        overall_progress = completed_files / total_files
                        self.root.after(0, lambda p=overall_progress: self.update_overall_progress(p))
                except Exception as e:
                    pass
        
        self.root.after(0, self.download_completed)
    
    def update_progress(self, progress, filename):
        speed_text = self.format_speed(self.download_stats['current_speed'])
        self.progress_info.configure(text=f"Đang tải: {filename} - {speed_text}")
    
    def update_overall_progress(self, progress):
        self.progress_bar.set(progress)
        speed_text = self.format_speed(self.download_stats['current_speed'])
        downloaded_mb = self.download_stats['downloaded_bytes'] / (1024 * 1024)
        self.progress_info.configure(text=f"Tiến trình: {progress:.1%} - Đã tải: {downloaded_mb:.1f} MB - {speed_text}")
    
    def format_speed(self, speed_bytes):
        if speed_bytes < 1024:
            return f"{speed_bytes:.1f} B/s"
        elif speed_bytes < 1024 * 1024:
            return f"{speed_bytes / 1024:.1f} KB/s"
        else:
            return f"{speed_bytes / (1024 * 1024):.1f} MB/s"
    
    def stop_download(self):
        self.is_downloading = False
        self.is_scanning = False
        self.download_btn.configure(state="normal")
        self.download_all_btn.configure(state="normal")
        self.stop_btn.configure(state="disabled")
        self.progress_info.configure(text="Đã dừng tải xuống")
    
    def download_completed(self):
        self.is_downloading = False
        self.download_btn.configure(state="normal")
        self.download_all_btn.configure(state="normal")
        self.stop_btn.configure(state="disabled")
        self.progress_bar.set(1)
        self.progress_info.configure(text="✅ Tải xuống hoàn tất!")
        messagebox.showinfo("Thành công", "Tải xuống hoàn tất!")
    
    def run(self):
        self.root.mainloop()

if __name__ == "__main__":
    app = FileDownloaderGUI()
    app.run()
