"""
Custom GUI components for the file downloader
"""

import tkinter as tk
import customtkinter as ctk
from config.settings import COLORS, FONTS, SCROLL_COLORS
from src.utils.file_utils import truncate_filename


class ScrollableFileList(ctk.CTkScrollableFrame):
    """Custom scrollable frame for file list"""
    
    def __init__(self, parent, **kwargs):
        super().__init__(
            parent,
            scrollbar_button_color=SCROLL_COLORS['button'],
            scrollbar_button_hover_color=SCROLL_COLORS['button_hover'],
            **kwargs
        )
        self.grid_columnconfigure(0, weight=1)
        self.selected_files = {}
        self.tree_widgets = {}
    
    def clear_list(self):
        """Clear all widgets from the list"""
        for widget in self.winfo_children():
            widget.destroy()
        self.selected_files = {}
        self.tree_widgets = {}
    
    def add_folder_header(self, folder_path, file_count, folder_count):
        """Add folder header to the list"""
        if folder_path and folder_path not in self.tree_widgets:
            folder_frame = ctk.CTkFrame(self)
            folder_frame.pack(fill="x", padx=5, pady=(5, 2), anchor="n")
            
            folder_label = ctk.CTkLabel(
                folder_frame,
                text=f"📁 {folder_path} ({file_count} tệp, {folder_count} thư mục con)",
                font=ctk.CTkFont(size=FONTS['normal'][1], weight="bold"),
                text_color=COLORS['primary']
            )
            folder_label.pack(side="left", padx=10, pady=5, anchor="w")
            
            self.tree_widgets[folder_path] = {
                "frame": folder_frame,
                "label": folder_label,
                "files": []
            }
    
    def add_file_item(self, file_info, file_index):
        """Add file item to the list"""
        folder_path = file_info.get("relative_path", "")
        
        # Create file frame
        file_frame = ctk.CTkFrame(self)
        file_frame.pack(fill="x", padx=15 if folder_path else 5, pady=1, anchor="n")
        
        # Create checkbox variable
        var = tk.BooleanVar()
        self.selected_files[file_index] = var
        
        # Truncate filename if too long
        display_name = truncate_filename(file_info["name"], 60)
        
        # Create checkbox
        checkbox = ctk.CTkCheckBox(
            file_frame,
            text=f"  📄 {display_name}",
            variable=var,
            font=ctk.CTkFont(size=FONTS['small'][1])
        )
        checkbox.pack(side="left", padx=10, pady=3, anchor="w")
        
        # Update folder info if exists
        if folder_path in self.tree_widgets:
            self.tree_widgets[folder_path]["files"].append(file_info)
        
        return var
    
    def update_folder_count(self, folder_path, file_count, folder_count):
        """Update folder file count"""
        if folder_path in self.tree_widgets:
            label = self.tree_widgets[folder_path]["label"]
            label.configure(text=f"📁 {folder_path} ({file_count} tệp, {folder_count} thư mục con)")
    
    def select_all_files(self, select=True):
        """Select or deselect all files"""
        for var in self.selected_files.values():
            var.set(select)
    
    def get_selected_indices(self):
        """Get indices of selected files"""
        return [i for i, var in self.selected_files.items() if var.get()]


class ProgressDisplay(ctk.CTkFrame):
    """Custom progress display component"""
    
    def __init__(self, parent, **kwargs):
        super().__init__(parent, **kwargs)
        
        # Progress label
        self.progress_label = ctk.CTkLabel(
            self, 
            text="📊 Tiến trình tải:", 
            font=ctk.CTkFont(size=FONTS['heading'][1], weight="bold")
        )
        self.progress_label.pack(anchor="w", padx=20, pady=(15, 5))
        
        # Progress bar
        self.progress_bar = ctk.CTkProgressBar(self, height=20)
        self.progress_bar.pack(fill="x", padx=20, pady=(0, 10))
        self.progress_bar.set(0)
        
        # Progress info
        self.progress_info = ctk.CTkLabel(
            self, 
            text="Sẵn sàng tải xuống",
            font=ctk.CTkFont(size=FONTS['normal'][1])
        )
        self.progress_info.pack(padx=20, pady=(0, 15))
    
    def update_progress(self, progress_data):
        """Update progress display"""
        if isinstance(progress_data, dict):
            overall_progress = progress_data.get('overall_progress', 0)
            current_file = progress_data.get('current_file', '')
            speed = progress_data.get('speed', '0 B/s')
            downloaded_mb = progress_data.get('downloaded_mb', 0)
            
            self.progress_bar.set(overall_progress)
            self.progress_info.configure(
                text=f"Tiến trình: {overall_progress:.1%} - Đang tải: {current_file} - {speed} - Đã tải: {downloaded_mb:.1f} MB"
            )
        else:
            self.progress_info.configure(text=str(progress_data))
    
    def reset(self):
        """Reset progress display"""
        self.progress_bar.set(0)
        self.progress_info.configure(text="Sẵn sàng tải xuống")


class StatusDisplay(ctk.CTkLabel):
    """Custom status display component"""
    
    def __init__(self, parent, **kwargs):
        super().__init__(
            parent,
            text="Sẵn sàng quét thư mục...",
            font=ctk.CTkFont(size=FONTS['tiny'][1]),
            text_color=COLORS['text_gray'],
            **kwargs
        )
    
    def update_status(self, status_type, message):
        """Update status with different types"""
        colors = {
            'ready': COLORS['text_gray'],
            'scanning': COLORS['primary'],
            'paused': COLORS['warning'],
            'error': COLORS['danger'],
            'success': COLORS['success'],
            'cancelled': COLORS['text_gray']
        }
        
        color = colors.get(status_type, COLORS['text_gray'])
        self.configure(text=message, text_color=color)


class ControlButtonGroup(ctk.CTkFrame):
    """Group of control buttons"""
    
    def __init__(self, parent, **kwargs):
        super().__init__(parent, **kwargs)
        self.buttons = {}
    
    def add_button(self, name, text, command, **kwargs):
        """Add button to the group"""
        button = ctk.CTkButton(
            self,
            text=text,
            command=command,
            **kwargs
        )
        self.buttons[name] = button
        return button
    
    def pack_button(self, name, **pack_kwargs):
        """Pack button with given options"""
        if name in self.buttons:
            self.buttons[name].pack(**pack_kwargs)
    
    def configure_button(self, name, **kwargs):
        """Configure button properties"""
        if name in self.buttons:
            self.buttons[name].configure(**kwargs)
    
    def get_button(self, name):
        """Get button by name"""
        return self.buttons.get(name)
