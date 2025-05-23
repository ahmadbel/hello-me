"""
Icon Manager Module
This module provides functionality for loading and managing application icons.
"""

import os
import tkinter as tk
from PIL import Image, ImageTk

class IconManager:
    """
    A class for managing application icons with support for different themes.
    """
    
    def __init__(self, icons_dir=None):
        """
        Initialize the icon manager.
        
        Args:
            icons_dir (str): Path to the icons directory
        """
        if icons_dir is None:
            # Use the default icons directory
            current_dir = os.path.dirname(os.path.abspath(__file__))
            icons_dir = os.path.join(current_dir, '..', 'resources', 'icons')
        
        self.icons_dir = icons_dir
        self.icon_cache = {}  # Cache for loaded icons
        
        # Create icons directory if it doesn't exist
        os.makedirs(self.icons_dir, exist_ok=True)
        
        # Define default icon names and their file paths
        self.default_icons = {
            # Admin icons
            'admin': 'admin.png',
            'dashboard': 'dashboard.png',
            'register': 'register.png',
            'students': 'students.png',
            'reports': 'reports.png',
            'settings': 'settings.png',
            'train': 'train.png',
            'export': 'export.png',
            
            # Scanner icons
            'scanner': 'scanner.png',
            'start': 'start.png',
            'stop': 'stop.png',
            'alert': 'alert.png',
            'recognized': 'recognized.png',
            'unknown': 'unknown.png',
            
            # Common icons
            'user': 'user.png',
            'camera': 'camera.png',
            'save': 'save.png',
            'edit': 'edit.png',
            'delete': 'delete.png',
            'search': 'search.png',
            'refresh': 'refresh.png',
            'calendar': 'calendar.png',
            'clock': 'clock.png',
            'info': 'info.png',
            'warning': 'warning.png',
            'error': 'error.png',
            'success': 'success.png',
            'dark_mode': 'dark_mode.png',
            'light_mode': 'light_mode.png'
        }
        
        # Generate placeholder icons for any missing icons
        self._generate_placeholder_icons()
    
    def _generate_placeholder_icons(self):
        """Generate placeholder icons for any missing icons."""
        for icon_name, file_name in self.default_icons.items():
            icon_path = os.path.join(self.icons_dir, file_name)
            
            if not os.path.exists(icon_path):
                # Create a simple placeholder icon
                self._create_placeholder_icon(icon_name, icon_path)
    
    def _create_placeholder_icon(self, icon_name, icon_path):
        """
        Create a simple placeholder icon.
        
        Args:
            icon_name (str): Name of the icon
            icon_path (str): Path where the icon should be saved
        """
        try:
            # Create a simple colored square with the first letter of the icon name
            size = 64
            img = Image.new('RGBA', (size, size), (0, 120, 212, 255))  # Blue background
            
            # Save the image
            img.save(icon_path)
            
            print(f"Created placeholder icon for {icon_name} at {icon_path}")
        except Exception as e:
            print(f"Error creating placeholder icon for {icon_name}: {e}")
    
    def get_icon_path(self, icon_name, theme='dark'):
        """
        Get the path to an icon.
        
        Args:
            icon_name (str): Name of the icon
            theme (str): Theme name ('dark' or 'light')
            
        Returns:
            str: Path to the icon, or None if not found
        """
        if icon_name not in self.default_icons:
            return None
        
        # Check for theme-specific icon first
        theme_file_name = f"{theme}_{self.default_icons[icon_name]}"
        theme_icon_path = os.path.join(self.icons_dir, theme_file_name)
        
        if os.path.exists(theme_icon_path):
            return theme_icon_path
        
        # Fall back to default icon
        default_icon_path = os.path.join(self.icons_dir, self.default_icons[icon_name])
        
        if os.path.exists(default_icon_path):
            return default_icon_path
        
        return None
    
    def load_icon(self, icon_name, size=(24, 24), theme='dark'):
        """
        Load an icon as a PhotoImage.
        
        Args:
            icon_name (str): Name of the icon
            size (tuple): Size to resize the icon to
            theme (str): Theme name ('dark' or 'light')
            
        Returns:
            ImageTk.PhotoImage: The loaded icon, or None if not found
        """
        # Create a cache key
        cache_key = f"{icon_name}_{size[0]}x{size[1]}_{theme}"
        
        # Check if the icon is already in the cache
        if cache_key in self.icon_cache:
            return self.icon_cache[cache_key]
        
        # Get the icon path
        icon_path = self.get_icon_path(icon_name, theme)
        
        if icon_path is None:
            return None
        
        try:
            # Load and resize the icon
            img = Image.open(icon_path)
            img = img.resize(size, Image.LANCZOS)
            
            # Convert to PhotoImage
            photo_img = ImageTk.PhotoImage(img)
            
            # Cache the icon
            self.icon_cache[cache_key] = photo_img
            
            return photo_img
        except Exception as e:
            print(f"Error loading icon {icon_name}: {e}")
            return None
    
    def create_icon_button(self, parent, icon_name, command=None, text=None, theme='dark', size=(24, 24), **kwargs):
        """
        Create a button with an icon.
        
        Args:
            parent: Parent widget
            icon_name (str): Name of the icon
            command: Button command
            text (str): Button text (optional)
            theme (str): Theme name ('dark' or 'light')
            size (tuple): Size to resize the icon to
            **kwargs: Additional arguments to pass to the Button constructor
            
        Returns:
            tk.Button: The created button
        """
        # Load the icon
        icon = self.load_icon(icon_name, size, theme)
        
        # Create the button
        button = tk.Button(parent, image=icon, command=command, compound=tk.LEFT, **kwargs)
        
        # Store a reference to the icon to prevent garbage collection
        button.icon = icon
        
        # Add text if provided
        if text:
            button.config(text=text, compound=tk.LEFT, padx=5)
        
        return button
    
    def set_icon_for_button(self, button, icon_name, theme='dark', size=(24, 24)):
        """
        Set an icon for an existing button.
        
        Args:
            button: Button widget
            icon_name (str): Name of the icon
            theme (str): Theme name ('dark' or 'light')
            size (tuple): Size to resize the icon to
            
        Returns:
            bool: True if the icon was set successfully, False otherwise
        """
        # Load the icon
        icon = self.load_icon(icon_name, size, theme)
        
        if icon is None:
            return False
        
        # Set the icon
        button.config(image=icon)
        
        # Store a reference to the icon to prevent garbage collection
        button.icon = icon
        
        return True
    
    def create_icon_label(self, parent, icon_name, text=None, theme='dark', size=(24, 24), **kwargs):
        """
        Create a label with an icon.
        
        Args:
            parent: Parent widget
            icon_name (str): Name of the icon
            text (str): Label text (optional)
            theme (str): Theme name ('dark' or 'light')
            size (tuple): Size to resize the icon to
            **kwargs: Additional arguments to pass to the Label constructor
            
        Returns:
            tk.Label: The created label
        """
        # Load the icon
        icon = self.load_icon(icon_name, size, theme)
        
        # Create the label
        label = tk.Label(parent, image=icon, **kwargs)
        
        # Store a reference to the icon to prevent garbage collection
        label.icon = icon
        
        # Add text if provided
        if text:
            label.config(text=text, compound=tk.LEFT, padx=5)
        
        return label
