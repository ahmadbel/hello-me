"""
Theme Manager Module
This module provides functionality for managing application themes.
"""

import tkinter as tk
from tkinter import ttk
import os
import json

class ThemeManager:
    """
    A class for managing application themes with improved contrast and accessibility.
    """
    
    def __init__(self):
        """Initialize the theme manager."""
        self.current_theme = "light"
        self.themes = {
            "light": {
                "bg": "#F5F5F5",
                "fg": "#333333",
                "button_bg": "#E0E0E0",
                "button_fg": "#333333",
                "button_active_bg": "#CCCCCC",
                "button_active_fg": "#000000",
                "entry_bg": "#FFFFFF",
                "entry_fg": "#333333",
                "highlight_bg": "#4A6FE3",
                "highlight_fg": "#FFFFFF",
                "border": "#CCCCCC"
            },
            "dark": {
                "bg": "#2D2D2D",
                "fg": "#E0E0E0",
                "button_bg": "#444444",
                "button_fg": "#FFFFFF",  # Ensure high contrast for button text
                "button_active_bg": "#555555",
                "button_active_fg": "#FFFFFF",  # Ensure high contrast for active button text
                "entry_bg": "#3D3D3D",
                "entry_fg": "#FFFFFF",
                "highlight_bg": "#5D8AF3",
                "highlight_fg": "#FFFFFF",
                "border": "#555555"
            }
        }
    
    def get_theme(self, theme_name=None):
        """
        Get a theme by name.
        
        Args:
            theme_name (str, optional): Theme name. If None, returns current theme.
            
        Returns:
            dict: Theme colors
        """
        if theme_name is None:
            theme_name = self.current_theme
        
        return self.themes.get(theme_name, self.themes["light"])
    
    def set_theme(self, theme_name):
        """
        Set the current theme.
        
        Args:
            theme_name (str): Theme name
            
        Returns:
            bool: True if theme was set successfully, False otherwise
        """
        if theme_name in self.themes:
            self.current_theme = theme_name
            return True
        return False
    
    def toggle_theme(self):
        """
        Toggle between light and dark themes.
        
        Returns:
            str: New theme name
        """
        if self.current_theme == "light":
            self.current_theme = "dark"
        else:
            self.current_theme = "light"
        
        return self.current_theme
    
    def apply_theme(self, widget, theme=None):
        """
        Apply the current theme to a widget.
        
        Args:
            widget: Widget to apply theme to
            theme (dict, optional): Theme to apply. If None, uses current theme.
        """
        if theme is None:
            theme = self.get_theme()
        
        try:
            # Apply theme to widget if it's a standard tk widget (not ttk)
            if not str(widget).startswith('.!t'):
                try:
                    widget.configure(bg=theme["bg"])
                except Exception:
                    pass
                    
                try:
                    widget.configure(fg=theme["fg"])
                except Exception:
                    pass
            
            # Apply theme to children
            for child in widget.winfo_children():
                self.apply_theme_to_widget(child, theme)
        except Exception as e:
            print(f"Error applying theme: {e}")
    
    def apply_theme_to_widget(self, widget, theme=None):
        """
        Apply a theme to a specific widget based on its type.
        
        Args:
            widget: Widget to apply theme to
            theme (dict, optional): Theme to apply. If None, uses current theme.
        """
        if theme is None:
            theme = self.get_theme()
        
        try:
            widget_type = widget.winfo_class()
            
            # Skip ttk widgets - they're handled by the style system
            if widget_type.startswith('T'):
                pass
            
            # Handle standard tk widgets
            elif widget_type in ("Frame", "Labelframe"):
                try:
                    widget.configure(bg=theme["bg"])
                except Exception:
                    pass
            
            elif widget_type == "Label":
                try:
                    widget.configure(bg=theme["bg"], fg=theme["fg"])
                except Exception:
                    pass
            
            elif widget_type == "Button":
                try:
                    widget.configure(
                        bg=theme["button_bg"],
                        fg=theme["button_fg"],
                        activebackground=theme["button_active_bg"],
                        activeforeground=theme["button_active_fg"]
                    )
                except Exception:
                    pass
            
            elif widget_type == "Entry":
                try:
                    widget.configure(
                        bg=theme["entry_bg"],
                        fg=theme["entry_fg"],
                        insertbackground=theme["fg"]
                    )
                except Exception:
                    pass
            
            elif widget_type == "Text":
                try:
                    widget.configure(
                        bg=theme["entry_bg"],
                        fg=theme["entry_fg"],
                        insertbackground=theme["fg"]
                    )
                except Exception:
                    pass
            
            elif widget_type == "Canvas":
                try:
                    widget.configure(bg=theme["bg"])
                except Exception:
                    pass
            
            elif widget_type == "Listbox":
                try:
                    widget.configure(
                        bg=theme["entry_bg"],
                        fg=theme["entry_fg"],
                        selectbackground=theme["highlight_bg"],
                        selectforeground=theme["highlight_fg"]
                    )
                except Exception:
                    pass
            
            elif widget_type == "Checkbutton":
                try:
                    widget.configure(
                        bg=theme["bg"],
                        fg=theme["fg"],
                        activebackground=theme["bg"],
                        activeforeground=theme["highlight_fg"],
                        selectcolor=theme["entry_bg"]
                    )
                except Exception:
                    pass
            
            # Apply theme to children
            for child in widget.winfo_children():
                self.apply_theme_to_widget(child, theme)
        
        except Exception:
            # Silently ignore errors for widgets that might have been destroyed
            pass
    
    def apply_theme_to_ttk(self, root, theme=None):
        """
        Apply the current theme to ttk widgets.
        
        Args:
            root: Root window
            theme (dict, optional): Theme to apply. If None, uses current theme.
        """
        if theme is None:
            theme = self.get_theme()
        
        try:
            # Create ttk style
            style = ttk.Style(root)
            
            # Configure ttk theme
            style.configure("TFrame", background=theme["bg"])
            style.configure("TLabelframe", background=theme["bg"])
            style.configure("TLabelframe.Label", background=theme["bg"], foreground=theme["fg"])
            
            style.configure("TLabel", background=theme["bg"], foreground=theme["fg"])
            
            # Ensure high contrast for buttons in both themes
            style.configure("TButton", 
                        background=theme["button_bg"], 
                        foreground=theme["button_fg"])
            
            style.map("TButton",
                    background=[("active", theme["button_active_bg"])],
                    foreground=[("active", theme["button_active_fg"])])
            
            style.configure("TEntry", 
                        fieldbackground=theme["entry_bg"], 
                        foreground=theme["entry_fg"])
            
            style.configure("TCheckbutton", 
                        background=theme["bg"], 
                        foreground=theme["fg"])
            
            style.configure("TRadiobutton", 
                        background=theme["bg"], 
                        foreground=theme["fg"])
            
            style.configure("TCombobox", 
                        fieldbackground=theme["entry_bg"], 
                        foreground=theme["entry_fg"])
            
            style.configure("TSpinbox", 
                        fieldbackground=theme["entry_bg"], 
                        foreground=theme["entry_fg"])
            
            style.configure("TNotebook", 
                        background=theme["bg"])
            
            style.configure("TNotebook.Tab", 
                        background=theme["button_bg"], 
                        foreground=theme["button_fg"])
            
            style.map("TNotebook.Tab",
                    background=[("selected", theme["highlight_bg"])],
                    foreground=[("selected", theme["highlight_fg"])])
            
            style.configure("Treeview", 
                        background=theme["entry_bg"], 
                        foreground=theme["entry_fg"],
                        fieldbackground=theme["entry_bg"])
            
            style.map("Treeview",
                    background=[("selected", theme["highlight_bg"])],
                    foreground=[("selected", theme["highlight_fg"])])
            
            style.configure("Horizontal.TProgressbar", 
                        background=theme["highlight_bg"])
            
            style.configure("Vertical.TProgressbar", 
                        background=theme["highlight_bg"])
        except Exception as e:
            print(f"Error applying ttk theme: {e}")
    
    def apply_theme_to_widgets(self, root, theme_name=None):
        """
        Apply the current theme to all widgets.
        
        Args:
            root: Root window
            theme_name (str, optional): Theme name to apply. If None, uses current theme.
            
        Returns:
            dict: Applied theme colors
        """
        # Set theme if specified
        if theme_name is not None:
            self.set_theme(theme_name)
        
        # Get theme colors
        theme = self.get_theme()
        
        try:
            # Apply theme to ttk widgets
            self.apply_theme_to_ttk(root, theme)
            
            # Apply theme to regular widgets
            self.apply_theme(root, theme)
        except Exception as e:
            print(f"Error applying theme to widgets: {e}")
        
        # Return theme colors for reference
        return theme
    
    def create_theme_toggle_button(self, parent, callback=None):
        """
        Create a button to toggle between light and dark themes.
        
        Args:
            parent: Parent widget
            callback (function, optional): Function to call when theme changes
            
        Returns:
            ttk.Button: Theme toggle button
        """
        def toggle_theme_callback():
            try:
                new_theme = self.toggle_theme()
                self.apply_theme_to_widgets(parent.winfo_toplevel())
                
                if callback:
                    callback(new_theme)
            except Exception as e:
                print(f"Error in theme toggle: {e}")
        
        button = ttk.Button(
            parent,
            text="Toggle Theme",
            command=toggle_theme_callback
        )
        
        return button
    
    def save_theme_preference(self, filepath, theme_name=None):
        """
        Save theme preference to a file.
        
        Args:
            filepath (str): Path to the file
            theme_name (str, optional): Theme name to save. If None, uses current theme.
            
        Returns:
            bool: True if preference was saved successfully, False otherwise
        """
        if theme_name is None:
            theme_name = self.current_theme
        
        try:
            # Ensure directory exists
            os.makedirs(os.path.dirname(filepath), exist_ok=True)
            
            with open(filepath, 'w') as f:
                json.dump({"theme": theme_name}, f)
            return True
        except Exception as e:
            print(f"Error saving theme preference: {e}")
            return False
    
    def load_theme_preference(self, filepath):
        """
        Load theme preference from a file.
        
        Args:
            filepath (str): Path to the file
            
        Returns:
            str: Loaded theme name, or None if loading failed
        """
        try:
            if os.path.exists(filepath):
                with open(filepath, 'r') as f:
                    data = json.load(f)
                    theme_name = data.get("theme")
                    
                    if theme_name in self.themes:
                        self.current_theme = theme_name
                        return theme_name
            
            return None
        except Exception as e:
            print(f"Error loading theme preference: {e}")
            return None
