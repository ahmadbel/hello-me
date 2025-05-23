"""
Modern UI Components Module
This module provides enhanced UI components with modern styling and animations.
"""

import tkinter as tk
from tkinter import ttk
import time
import threading

class ModernButton(tk.Button):
    """
    A modern button with hover effects and animations.
    """
    
    def __init__(self, parent, **kwargs):
        """
        Initialize the modern button.
        
        Args:
            parent: Parent widget
            **kwargs: Additional arguments to pass to the Button constructor
        """
        # Extract custom parameters
        self.hover_color = kwargs.pop('hover_color', None)
        self.active_color = kwargs.pop('active_color', None)
        self.corner_radius = kwargs.pop('corner_radius', 0)
        
        # Initialize the button
        super().__init__(parent, **kwargs)
        
        # Store original colors
        self.original_bg = self['bg']
        self.original_fg = self['fg']
        
        # Set default hover color if not provided
        if self.hover_color is None:
            # Try to create a slightly lighter version of the background color
            try:
                r, g, b = self.winfo_rgb(self.original_bg)
                r = min(65535, int(r * 1.2))
                g = min(65535, int(g * 1.2))
                b = min(65535, int(b * 1.2))
                self.hover_color = f'#{r//256:02x}{g//256:02x}{b//256:02x}'
            except:
                self.hover_color = self.original_bg
        
        # Set default active color if not provided
        if self.active_color is None:
            # Try to create a slightly darker version of the background color
            try:
                r, g, b = self.winfo_rgb(self.original_bg)
                r = int(r * 0.8)
                g = int(g * 0.8)
                b = int(b * 0.8)
                self.active_color = f'#{r//256:02x}{g//256:02x}{b//256:02x}'
            except:
                self.active_color = self.original_bg
        
        # Bind events for hover effects
        self.bind("<Enter>", self._on_enter)
        self.bind("<Leave>", self._on_leave)
        self.bind("<ButtonPress-1>", self._on_press)
        self.bind("<ButtonRelease-1>", self._on_release)
    
    def _on_enter(self, event):
        """Handle mouse enter event."""
        self.config(bg=self.hover_color)
    
    def _on_leave(self, event):
        """Handle mouse leave event."""
        self.config(bg=self.original_bg)
    
    def _on_press(self, event):
        """Handle mouse press event."""
        self.config(bg=self.active_color)
    
    def _on_release(self, event):
        """Handle mouse release event."""
        self.config(bg=self.hover_color)

class AnimatedProgressBar(ttk.Frame):
    """
    An animated progress bar with text overlay.
    """
    
    def __init__(self, parent, **kwargs):
        """
        Initialize the animated progress bar.
        
        Args:
            parent: Parent widget
            **kwargs: Additional arguments to pass to the Frame constructor
        """
        # Extract custom parameters
        self.width = kwargs.pop('width', 300)
        self.height = kwargs.pop('height', 20)
        self.value = kwargs.pop('value', 0)
        self.maximum = kwargs.pop('maximum', 100)
        self.text_format = kwargs.pop('text_format', '{value}%')
        self.animation_speed = kwargs.pop('animation_speed', 5)
        self.bar_color = kwargs.pop('bar_color', '#007ACC')
        self.text_color = kwargs.pop('text_color', '#FFFFFF')
        self.background_color = kwargs.pop('background_color', '#333333')
        
        # Initialize the frame
        super().__init__(parent, **kwargs)
        
        # Create canvas for drawing
        self.canvas = tk.Canvas(
            self,
            width=self.width,
            height=self.height,
            bg=self.background_color,
            highlightthickness=0
        )
        self.canvas.pack(fill=tk.BOTH, expand=True)
        
        # Create progress bar rectangle
        self.bar = self.canvas.create_rectangle(
            0, 0, 0, self.height,
            fill=self.bar_color,
            width=0
        )
        
        # Create text
        self.text = self.canvas.create_text(
            self.width // 2, self.height // 2,
            text=self._format_text(),
            fill=self.text_color,
            font=('Helvetica', 10, 'bold')
        )
        
        # Current animated value
        self.current_value = 0
        
        # Animation thread
        self.animation_thread = None
        self.animation_running = False
        
        # Initial update
        self.update_progress(self.value)
    
    def _format_text(self):
        """Format the progress text."""
        percentage = int((self.current_value / self.maximum) * 100)
        return self.text_format.format(value=percentage, max=self.maximum, current=self.current_value)
    
    def update_progress(self, value):
        """
        Update the progress bar value.
        
        Args:
            value: New progress value
        """
        # Ensure value is within bounds
        value = max(0, min(value, self.maximum))
        
        # Store the target value
        self.value = value
        
        # Start animation if not already running
        if not self.animation_running:
            self._start_animation()
    
    def _start_animation(self):
        """Start the progress animation."""
        # Stop any existing animation
        self.animation_running = False
        if self.animation_thread and self.animation_thread.is_alive():
            self.animation_thread.join()
        
        # Start new animation
        self.animation_running = True
        self.animation_thread = threading.Thread(target=self._animate)
        self.animation_thread.daemon = True
        self.animation_thread.start()
    
    def _animate(self):
        """Animate the progress bar."""
        while self.animation_running and self.current_value != self.value:
            # Calculate step
            if self.current_value < self.value:
                step = min(self.animation_speed, self.value - self.current_value)
                self.current_value += step
            else:
                step = min(self.animation_speed, self.current_value - self.value)
                self.current_value -= step
            
            # Update the bar
            width = int((self.current_value / self.maximum) * self.width)
            self.canvas.coords(self.bar, 0, 0, width, self.height)
            
            # Update the text
            self.canvas.itemconfig(self.text, text=self._format_text())
            
            # Check if we've reached the target
            if self.current_value == self.value:
                self.animation_running = False
                break
            
            # Sleep for a short time
            time.sleep(0.01)
    
    def stop_animation(self):
        """Stop the progress animation."""
        self.animation_running = False

class ToastNotification:
    """
    A toast notification that appears and disappears automatically.
    """
    
    def __init__(self, parent, message, duration=3000, background='#333333', foreground='#FFFFFF'):
        """
        Initialize the toast notification.
        
        Args:
            parent: Parent widget
            message (str): Notification message
            duration (int): Duration in milliseconds
            background (str): Background color
            foreground (str): Text color
        """
        self.parent = parent
        self.message = message
        self.duration = duration
        
        # Create a toplevel window
        self.window = tk.Toplevel(parent)
        self.window.overrideredirect(True)  # Remove window decorations
        
        # Position at the bottom of the parent window
        self.window.withdraw()  # Hide initially to calculate size
        
        # Create label with message
        self.label = tk.Label(
            self.window,
            text=message,
            background=background,
            foreground=foreground,
            font=('Helvetica', 12),
            padx=20,
            pady=10
        )
        self.label.pack()
        
        # Add rounded corners and shadow (if possible)
        try:
            self.window.attributes('-alpha', 0.9)  # Slight transparency
        except:
            pass
    
    def show(self):
        """Show the toast notification."""
        # Update the window size
        self.window.update_idletasks()
        
        # Calculate position (centered at the bottom of the parent)
        parent_x = self.parent.winfo_rootx()
        parent_y = self.parent.winfo_rooty()
        parent_width = self.parent.winfo_width()
        parent_height = self.parent.winfo_height()
        
        window_width = self.window.winfo_width()
        window_height = self.window.winfo_height()
        
        x = parent_x + (parent_width - window_width) // 2
        y = parent_y + parent_height - window_height - 20
        
        # Position the window
        self.window.geometry(f'+{x}+{y}')
        
        # Show with fade-in effect
        self.window.deiconify()
        
        # Schedule auto-close
        self.parent.after(self.duration, self.close)
    
    def close(self):
        """Close the toast notification."""
        self.window.destroy()

class ModernDialog(tk.Toplevel):
    """
    A modern dialog window with customizable buttons and animations.
    """
    
    def __init__(self, parent, title=None, **kwargs):
        """
        Initialize the modern dialog.
        
        Args:
            parent: Parent widget
            title (str): Dialog title
            **kwargs: Additional arguments to pass to the Toplevel constructor
        """
        super().__init__(parent, **kwargs)
        
        # Configure dialog
        self.title(title or "Dialog")
        self.transient(parent)
        self.resizable(False, False)
        self.protocol("WM_DELETE_WINDOW", self.cancel)
        
        # Apply modern styling
        self.configure(bg='#1E1E1E')
        
        # Create main frame
        self.main_frame = ttk.Frame(self, padding=20)
        self.main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Create content area
        self.content_frame = ttk.Frame(self.main_frame)
        self.content_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 20))
        
        # Create button area
        self.button_frame = ttk.Frame(self.main_frame)
        self.button_frame.pack(fill=tk.X)
        
        # Result variable
        self.result = None
        
        # Center the dialog
        self.withdraw()  # Hide initially
        self.update_idletasks()
        
        # Position relative to parent
        parent_x = parent.winfo_rootx()
        parent_y = parent.winfo_rooty()
        parent_width = parent.winfo_width()
        parent_height = parent.winfo_height()
        
        dialog_width = self.winfo_width()
        dialog_height = self.winfo_height()
        
        x = parent_x + (parent_width - dialog_width) // 2
        y = parent_y + (parent_height - dialog_height) // 3
        
        self.geometry(f'+{x}+{y}')
        
        # Make dialog modal
        self.grab_set()
        
        # Show dialog with animation
        self.deiconify()
    
    def add_button(self, text, command=None, default=False, style=None):
        """
        Add a button to the dialog.
        
        Args:
            text (str): Button text
            command: Button command
            default (bool): Whether this is the default button
            style (str): Button style
            
        Returns:
            ttk.Button: The created button
        """
        button = ttk.Button(
            self.button_frame,
            text=text,
            command=command or self.ok,
            style=style
        )
        button.pack(side=tk.RIGHT, padx=5)
        
        if default:
            self.bind("<Return>", lambda event: command() if command else self.ok())
            button.focus_set()
        
        return button
    
    def add_content(self, widget):
        """
        Add content to the dialog.
        
        Args:
            widget: Widget to add
            
        Returns:
            widget: The added widget
        """
        widget.pack(in_=self.content_frame, fill=tk.BOTH, expand=True)
        return widget
    
    def ok(self):
        """Handle OK button click."""
        self.result = True
        self.destroy()
    
    def cancel(self):
        """Handle Cancel button click."""
        self.result = False
        self.destroy()
    
    def show(self):
        """
        Show the dialog and wait for it to be closed.
        
        Returns:
            The dialog result
        """
        self.wait_window()
        return self.result

class ModernToolTip:
    """
    A modern tooltip with customizable appearance and animations.
    """
    
    def __init__(self, widget, text, delay=500, background='#333333', foreground='#FFFFFF'):
        """
        Initialize the tooltip.
        
        Args:
            widget: Widget to attach the tooltip to
            text (str): Tooltip text
            delay (int): Delay in milliseconds before showing the tooltip
            background (str): Background color
            foreground (str): Text color
        """
        self.widget = widget
        self.text = text
        self.delay = delay
        self.background = background
        self.foreground = foreground
        
        self.tooltip_window = None
        self.scheduled_id = None
        
        # Bind events
        self.widget.bind("<Enter>", self.schedule)
        self.widget.bind("<Leave>", self.hide)
        self.widget.bind("<ButtonPress>", self.hide)
    
    def schedule(self, event=None):
        """Schedule the tooltip to be shown."""
        self.hide()
        self.scheduled_id = self.widget.after(self.delay, self.show)
    
    def show(self):
        """Show the tooltip."""
        # Cancel any scheduled show
        if self.scheduled_id:
            self.widget.after_cancel(self.scheduled_id)
            self.scheduled_id = None
        
        # Create tooltip window
        self.tooltip_window = tk.Toplevel(self.widget)
        self.tooltip_window.overrideredirect(True)  # Remove window decorations
        
        # Create label with text
        label = tk.Label(
            self.tooltip_window,
            text=self.text,
            background=self.background,
            foreground=self.foreground,
            font=('Helvetica', 10),
            padx=10,
            pady=5
        )
        label.pack()
        
        # Position tooltip below the widget
        x = self.widget.winfo_rootx()
        y = self.widget.winfo_rooty() + self.widget.winfo_height() + 5
        
        self.tooltip_window.geometry(f'+{x}+{y}')
    
    def hide(self, event=None):
        """Hide the tooltip."""
        # Cancel any scheduled show
        if self.scheduled_id:
            self.widget.after_cancel(self.scheduled_id)
            self.scheduled_id = None
        
        # Destroy tooltip window if it exists
        if self.tooltip_window:
            self.tooltip_window.destroy()
            self.tooltip_window = None
