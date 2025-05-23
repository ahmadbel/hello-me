"""
Main Application Module
This module provides the main entry point for the Enhanced Attendance System.
"""

import os
import sys
import tkinter as tk
from tkinter import ttk
import threading
import datetime
import logging

# Add parent directory to path
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(current_dir)

# Import modules
from core.data_management.config import ConfigManager
from core.data_management.database import DatabaseManager
from ui.admin.admin_app import AdminApp
from ui.scanner.scanner_app import ScannerApp
from utils.logger import Logger
from utils.ui_components import ModernUI
from utils.theme_manager import ThemeManager

class MainApp:
    """
    Main application class for the Enhanced Attendance System.
    """
    
    def __init__(self, root):
        """
        Initialize the main application.
        
        Args:
            root: Tkinter root window
        """
        self.root = root
        self.logger = Logger()
        self.logger.info("Main application started")
        
        # Initialize configuration
        self.config = ConfigManager()
        self.config.ensure_directories_exist()
        
        # Initialize database
        self.db = DatabaseManager()
        
        # Initialize theme manager
        self.theme_manager = ThemeManager()
        
        # Set up the main window
        self.setup_main_window()
        
        # Create main content
        self.create_content()
    
    def setup_main_window(self):
        """Set up the main window."""
        # Configure the root window
        self.root.title(self.config.get_value('General', 'ApplicationName'))
        self.root.geometry("800x600")
        self.root.minsize(800, 600)
        
        # Apply theme
        theme_name = self.config.get_value('General', 'Theme', 'dark')
        self.theme_colors = self.theme_manager.apply_theme_to_widgets(self.root, theme_name)
        
        # Create main frame
        self.main_frame = ttk.Frame(self.root, padding=20)
        self.main_frame.pack(fill=tk.BOTH, expand=True)
    
    def create_content(self):
        """Create the main content."""
        # Create title
        title_label = ModernUI.create_title_label(
            self.main_frame,
            "Enhanced Attendance System",
            font_size=24
        )
        title_label.pack(pady=(0, 20))
        
        # Create description
        description = """
        Welcome to the Enhanced Attendance Management System with Face Recognition.
        
        This system provides two interfaces:
        - Admin Interface: For student registration and management
        - Scanner Interface: For automatic attendance tracking and security monitoring
        
        Please select an interface to continue.
        """
        
        desc_label = ttk.Label(
            self.main_frame,
            text=description,
            justify=tk.CENTER,
            wraplength=600
        )
        desc_label.pack(pady=(0, 30))
        
        # Create buttons frame
        buttons_frame = ttk.Frame(self.main_frame)
        buttons_frame.pack(pady=20)
        
        # Create admin button
        admin_btn = ttk.Button(
            buttons_frame,
            text="Admin Interface",
            command=self.launch_admin,
            width=20
        )
        admin_btn.grid(row=0, column=0, padx=20, pady=10)
        
        # Create scanner button
        scanner_btn = ttk.Button(
            buttons_frame,
            text="Scanner Interface",
            command=self.launch_scanner,
            width=20
        )
        scanner_btn.grid(row=0, column=1, padx=20, pady=10)
        
        # Add theme toggle button
        theme_btn = self.theme_manager.create_theme_toggle_button(
            self.main_frame,
            callback=self.on_theme_change
        )
        theme_btn.pack(pady=(30, 0))
        
        # Add version info
        version = self.config.get_value('General', 'Version', '1.0.0')
        version_label = ttk.Label(
            self.main_frame,
            text=f"Version {version}",
            font=('Helvetica', 8)
        )
        version_label.pack(side=tk.BOTTOM, pady=(20, 0))
    
    def on_theme_change(self, theme_name):
        """
        Handle theme change.
        
        Args:
            theme_name (str): New theme name
        """
        # Update configuration
        self.config.set_value('General', 'Theme', theme_name)
    
    def launch_admin(self):
        """Launch the admin interface."""
        self.logger.info("Launching admin interface")
        
        # Create a new window for the admin interface
        admin_window = tk.Toplevel(self.root)
        admin_window.title(self.config.get_value('UI', 'AdminTitle'))
        admin_window.geometry("1024x768")
        admin_window.minsize(1024, 768)
        
        # Apply theme
        theme_name = self.config.get_value('General', 'Theme', 'dark')
        self.theme_manager.apply_theme_to_widgets(admin_window, theme_name)
        
        # Create admin app
        admin_app = AdminApp(admin_window)
    
    def launch_scanner(self):
        """Launch the scanner interface."""
        self.logger.info("Launching scanner interface")
        
        # Create a new window for the scanner interface
        scanner_window = tk.Toplevel(self.root)
        scanner_window.title(self.config.get_value('UI', 'ScannerTitle'))
        scanner_window.geometry("1024x768")
        scanner_window.minsize(1024, 768)
        
        # Apply theme
        theme_name = self.config.get_value('General', 'Theme', 'dark')
        self.theme_manager.apply_theme_to_widgets(scanner_window, theme_name)
        
        # Create scanner app
        scanner_app = ScannerApp(scanner_window)

def main():
    """Main entry point for the application."""
    # Create root window
    root = tk.Tk()
    
    # Create main app
    app = MainApp(root)
    
    # Start main loop
    root.mainloop()

if __name__ == "__main__":
    main()
