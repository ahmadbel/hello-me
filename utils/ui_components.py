"""
UI Utilities Module
This module provides UI components for the Enhanced Attendance System.
"""

import tkinter as tk
from tkinter import ttk
import cv2
import numpy as np
import threading
import time
import logging
from PIL import Image, ImageTk

class ModernUI:
    """
    A class providing modern UI components.
    """
    
    @staticmethod
    def create_title_label(parent, text, font_size=18):
        """
        Create a title label.
        
        Args:
            parent: Parent widget
            text (str): Label text
            font_size (int): Font size
            
        Returns:
            tk.Label: The created label
        """
        # Try to get background color, with fallback
        try:
            bg_color = parent['bg']
        except:
            try:
                bg_color = parent.winfo_toplevel()['bg']
            except:
                bg_color = '#1E1E1E'  # Default dark background
        
        label = tk.Label(
            parent,
            text=text,
            font=('Helvetica', font_size, 'bold'),
            fg='#FFFFFF',
            bg=bg_color
        )
        
        return label
    
    @staticmethod
    def create_section_label(parent, text, font_size=14):
        """
        Create a section label.
        
        Args:
            parent: Parent widget
            text (str): Label text
            font_size (int): Font size
            
        Returns:
            tk.Label: The created label
        """
        # Try to get background color, with fallback
        try:
            bg_color = parent['bg']
        except:
            try:
                bg_color = parent.winfo_toplevel()['bg']
            except:
                bg_color = '#1E1E1E'  # Default dark background
        
        label = tk.Label(
            parent,
            text=text,
            font=('Helvetica', font_size, 'bold'),
            fg='#4A6FE3',
            bg=bg_color
        )
        
        return label
    
    @staticmethod
    def create_info_label(parent, text, font_size=10):
        """
        Create an info label.
        
        Args:
            parent: Parent widget
            text (str): Label text
            font_size (int): Font size
            
        Returns:
            tk.Label: The created label
        """
        # Try to get background color, with fallback
        try:
            bg_color = parent['bg']
        except:
            try:
                bg_color = parent.winfo_toplevel()['bg']
            except:
                bg_color = '#1E1E1E'  # Default dark background
        
        label = tk.Label(
            parent,
            text=text,
            font=('Helvetica', font_size, 'italic'),
            fg='#888888',
            bg=bg_color
        )
        
        return label
    
    @staticmethod
    def create_button(parent, text, command, width=15):
        """
        Create a modern button.
        
        Args:
            parent: Parent widget
            text (str): Button text
            command: Button command
            width (int): Button width
            
        Returns:
            ttk.Button: The created button
        """
        button = ttk.Button(
            parent,
            text=text,
            command=command,
            width=width
        )
        
        return button
    
    @staticmethod
    def create_entry(parent, textvariable, width=20):
        """
        Create a modern entry.
        
        Args:
            parent: Parent widget
            textvariable: Tkinter variable
            width (int): Entry width
            
        Returns:
            ttk.Entry: The created entry
        """
        entry = ttk.Entry(
            parent,
            textvariable=textvariable,
            width=width
        )
        
        return entry
    
    @staticmethod
    def create_checkbox(parent, text, variable):
        """
        Create a modern checkbox.
        
        Args:
            parent: Parent widget
            text (str): Checkbox text
            variable: Tkinter variable
            
        Returns:
            ttk.Checkbutton: The created checkbox
        """
        checkbox = ttk.Checkbutton(
            parent,
            text=text,
            variable=variable
        )
        
        return checkbox
    
    @staticmethod
    def create_radio_button(parent, text, variable, value):
        """
        Create a modern radio button.
        
        Args:
            parent: Parent widget
            text (str): Radio button text
            variable: Tkinter variable
            value: Radio button value
            
        Returns:
            ttk.Radiobutton: The created radio button
        """
        radio_button = ttk.Radiobutton(
            parent,
            text=text,
            variable=variable,
            value=value
        )
        
        return radio_button
    
    @staticmethod
    def create_combobox(parent, textvariable, values, width=20):
        """
        Create a modern combobox.
        
        Args:
            parent: Parent widget
            textvariable: Tkinter variable
            values (list): Combobox values
            width (int): Combobox width
            
        Returns:
            ttk.Combobox: The created combobox
        """
        combobox = ttk.Combobox(
            parent,
            textvariable=textvariable,
            values=values,
            width=width
        )
        
        return combobox
    
    @staticmethod
    def create_spinbox(parent, from_, to, textvariable, width=10):
        """
        Create a modern spinbox.
        
        Args:
            parent: Parent widget
            from_ (int): Minimum value
            to (int): Maximum value
            textvariable: Tkinter variable
            width (int): Spinbox width
            
        Returns:
            ttk.Spinbox: The created spinbox
        """
        spinbox = ttk.Spinbox(
            parent,
            from_=from_,
            to=to,
            textvariable=textvariable,
            width=width
        )
        
        return spinbox
    
    @staticmethod
    def create_scale(parent, from_, to, variable, orient=tk.HORIZONTAL):
        """
        Create a modern scale.
        
        Args:
            parent: Parent widget
            from_ (int): Minimum value
            to (int): Maximum value
            variable: Tkinter variable
            orient: Scale orientation
            
        Returns:
            ttk.Scale: The created scale
        """
        scale = ttk.Scale(
            parent,
            from_=from_,
            to=to,
            variable=variable,
            orient=orient
        )
        
        return scale
    
    @staticmethod
    def create_progress_bar(parent, variable, maximum=100, length=200):
        """
        Create a modern progress bar.
        
        Args:
            parent: Parent widget
            variable: Tkinter variable
            maximum (int): Maximum value
            length (int): Progress bar length
            
        Returns:
            ttk.Progressbar: The created progress bar
        """
        progress_bar = ttk.Progressbar(
            parent,
            variable=variable,
            maximum=maximum,
            length=length
        )
        
        return progress_bar
    
    @staticmethod
    def create_separator(parent, orient=tk.HORIZONTAL):
        """
        Create a separator.
        
        Args:
            parent: Parent widget
            orient: Separator orientation
            
        Returns:
            ttk.Separator: The created separator
        """
        separator = ttk.Separator(
            parent,
            orient=orient
        )
        
        return separator
    
    @staticmethod
    def create_scrolled_text(parent, width=40, height=10):
        """
        Create a scrolled text widget.
        
        Args:
            parent: Parent widget
            width (int): Text width
            height (int): Text height
            
        Returns:
            tuple: (frame, text) where frame is the container and text is the text widget
        """
        frame = ttk.Frame(parent)
        
        text = tk.Text(
            frame,
            width=width,
            height=height
        )
        
        scrollbar = ttk.Scrollbar(
            frame,
            orient=tk.VERTICAL,
            command=text.yview
        )
        
        text.configure(yscrollcommand=scrollbar.set)
        
        text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        return frame, text
    
    @staticmethod
    def create_scrolled_listbox(parent, width=40, height=10):
        """
        Create a scrolled listbox.
        
        Args:
            parent: Parent widget
            width (int): Listbox width
            height (int): Listbox height
            
        Returns:
            tuple: (frame, listbox) where frame is the container and listbox is the listbox widget
        """
        frame = ttk.Frame(parent)
        
        listbox = tk.Listbox(
            frame,
            width=width,
            height=height
        )
        
        scrollbar = ttk.Scrollbar(
            frame,
            orient=tk.VERTICAL,
            command=listbox.yview
        )
        
        listbox.configure(yscrollcommand=scrollbar.set)
        
        listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        return frame, listbox
    
    @staticmethod
    def create_treeview(parent, columns, headings, column_widths=None):
        """
        Create a treeview.
        
        Args:
            parent: Parent widget
            columns (list): Column IDs
            headings (list): Column headings
            column_widths (list, optional): Column widths
            
        Returns:
            tuple: (frame, treeview) where frame is the container and treeview is the treeview widget
        """
        frame = ttk.Frame(parent)
        
        treeview = ttk.Treeview(
            frame,
            columns=columns,
            show="headings"
        )
        
        # Set headings
        for i, heading in enumerate(headings):
            treeview.heading(columns[i], text=heading)
        
        # Set column widths
        if column_widths:
            for i, width in enumerate(column_widths):
                treeview.column(columns[i], width=width)
        
        # Add scrollbars
        y_scrollbar = ttk.Scrollbar(
            frame,
            orient=tk.VERTICAL,
            command=treeview.yview
        )
        
        x_scrollbar = ttk.Scrollbar(
            frame,
            orient=tk.HORIZONTAL,
            command=treeview.xview
        )
        
        treeview.configure(yscrollcommand=y_scrollbar.set, xscrollcommand=x_scrollbar.set)
        
        # Pack everything
        treeview.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        y_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        x_scrollbar.pack(side=tk.BOTTOM, fill=tk.X)
        
        return frame, treeview

class CameraFeed:
    """
    A class for displaying camera feed in a Tkinter application.
    """
    
    def __init__(self, parent, width=640, height=480, camera_index=0):
        """
        Initialize the camera feed.
        
        Args:
            parent: Parent widget
            width (int): Display width
            height (int): Display height
            camera_index (int): Camera index
        """
        self.parent = parent
        self.width = width
        self.height = height
        self.camera_index = camera_index
        
        # Set up logger
        self.logger = logging.getLogger("AttendanceSystem")
        
        # Create canvas for displaying the camera feed
        self.canvas = tk.Canvas(parent, width=width, height=height, bg="black")
        self.canvas.pack(fill=tk.BOTH, expand=True)
        
        # Initialize variables
        self.cap = None
        self.running = False
        self.thread = None
        self.frame_processors = []
        self.last_frame = None
        self.retry_count = 0
        self.max_retries = 3
        self.retry_delay = 2  # seconds
        self.last_retry_time = 0
        self.stop_event = threading.Event()
        
        # Create status label
        self.status_var = tk.StringVar(value="Camera not started")
        self.status_label = ttk.Label(parent, textvariable=self.status_var)
        self.status_label.pack(pady=5)
        
        # Bind cleanup to parent window destruction
        if hasattr(parent, 'winfo_toplevel'):
            parent.winfo_toplevel().bind("<Destroy>", self._on_destroy, add="+")
    
    def _on_destroy(self, event):
        """Handle window destruction event."""
        # Only handle if our parent or its toplevel is being destroyed
        widget = event.widget
        if widget == self.parent or widget == self.parent.winfo_toplevel():
            self.stop()
    
    def start(self):
        """
        Start the camera feed.
        
        Returns:
            bool: True if camera started successfully, False otherwise
        """
        if self.running:
            return True
        
        # Reset stop event
        self.stop_event.clear()
        
        try:
            # Try to open the camera
            self.cap = cv2.VideoCapture(self.camera_index, cv2.CAP_DSHOW)  # Use DirectShow on Windows
            
            # Check if camera opened successfully
            if not self.cap.isOpened():
                self.logger.error(f"Failed to open camera {self.camera_index}")
                self.status_var.set(f"Error: Failed to open camera {self.camera_index}")
                return False
            
            # Set camera properties
            self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, self.width)
            self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, self.height)
            
            # Start the camera thread
            self.running = True
            self.thread = threading.Thread(target=self.update)
            self.thread.daemon = True
            self.thread.start()
            
            self.status_var.set("Camera started")
            self.retry_count = 0
            return True
        except Exception as e:
            self.logger.error(f"Error starting camera: {e}")
            self.status_var.set(f"Error: {e}")
            return False
    
    def stop(self):
        """Stop the camera feed."""
        # Signal thread to stop
        self.stop_event.set()
        self.running = False
        
        # Wait for thread to finish
        if self.thread and self.thread.is_alive():
            self.thread.join(timeout=1.0)
        
        # Release the camera
        if self.cap:
            self.cap.release()
            self.cap = None
        
        # Clear the canvas - use try/except to handle cases where canvas might be destroyed
        try:
            self.canvas.delete("all")
            self.status_var.set("Camera stopped")
        except Exception:
            pass  # Canvas might be destroyed already
    
    def update(self):
        """Update the camera feed."""
        try:
            while self.running and not self.stop_event.is_set():
                # Check if camera is still open
                if not self.cap or not self.cap.isOpened():
                    self.handle_camera_error("Camera disconnected")
                    break
                
                # Read a frame
                ret, frame = self.cap.read()
                
                if not ret:
                    # Try to handle frame grab error
                    current_time = time.time()
                    if current_time - self.last_retry_time > self.retry_delay:
                        self.last_retry_time = current_time
                        self.retry_count += 1
                        
                        if self.retry_count <= self.max_retries:
                            self.logger.warning(f"Failed to grab frame, retrying ({self.retry_count}/{self.max_retries})...")
                            
                            # Update status safely
                            try:
                                self.status_var.set(f"Retrying ({self.retry_count}/{self.max_retries})...")
                            except Exception:
                                pass
                            
                            # Try to reinitialize the camera
                            if self.cap:
                                self.cap.release()
                            
                            time.sleep(0.5)  # Short delay before retry
                            
                            self.cap = cv2.VideoCapture(self.camera_index, cv2.CAP_DSHOW)
                            continue
                        else:
                            self.handle_camera_error("Failed to grab frame after multiple retries")
                            break
                    
                    # Skip this frame and try again
                    time.sleep(0.1)
                    continue
                
                # Reset retry count on successful frame grab
                self.retry_count = 0
                
                # Store the last successful frame
                self.last_frame = frame.copy()
                
                # Process the frame
                processed_frame = self.process_frame(frame)
                
                # Convert to RGB for tkinter
                rgb_frame = cv2.cvtColor(processed_frame, cv2.COLOR_BGR2RGB)
                
                # Resize to fit canvas if needed
                if rgb_frame.shape[1] != self.width or rgb_frame.shape[0] != self.height:
                    rgb_frame = cv2.resize(rgb_frame, (self.width, self.height))
                
                # Update canvas safely
                try:
                    # Convert to PhotoImage
                    img = Image.fromarray(rgb_frame)
                    photo = ImageTk.PhotoImage(image=img)
                    
                    # Update canvas
                    self.canvas.delete("all")
                    self.canvas.create_image(0, 0, image=photo, anchor=tk.NW)
                    self.canvas.photo = photo  # Keep a reference
                except Exception:
                    # Canvas might be destroyed or invalid
                    break
                
                # Short sleep to reduce CPU usage
                time.sleep(0.03)
        except Exception as e:
            self.logger.error(f"Error in camera update loop: {e}")
            self.handle_camera_error(f"Error: {e}")
        finally:
            # Ensure camera is released
            if self.cap:
                self.cap.release()
                self.cap = None
            
            # Update status safely
            if self.running:
                try:
                    self.parent.after(0, lambda: self.status_var.set("Camera disconnected"))
                except Exception:
                    pass  # Parent might be destroyed
                self.running = False
    
    def handle_camera_error(self, message):
        """
        Handle camera error.
        
        Args:
            message (str): Error message
        """
        self.logger.error(message)
        try:
            self.parent.after(0, lambda: self.status_var.set(message))
        except Exception:
            pass  # Parent might be destroyed
        self.running = False
    
    def process_frame(self, frame):
        """
        Process a frame using registered processors.
        
        Args:
            frame: Frame to process
            
        Returns:
            Processed frame
        """
        processed_frame = frame.copy()
        
        # Apply all frame processors
        for processor in self.frame_processors:
            try:
                processed_frame = processor(processed_frame)
            except Exception as e:
                self.logger.error(f"Error in frame processor: {e}")
        
        return processed_frame
    
    def add_frame_processor(self, processor):
        """
        Add a frame processor.
        
        Args:
            processor: Function that takes a frame and returns a processed frame
        """
        self.frame_processors.append(processor)
    
    def remove_frame_processor(self, processor):
        """
        Remove a frame processor.
        
        Args:
            processor: Processor to remove
        """
        if processor in self.frame_processors:
            self.frame_processors.remove(processor)
    
    def is_running(self):
        """
        Check if camera is running.
        
        Returns:
            bool: True if camera is running, False otherwise
        """
        return self.running
    
    def get_last_frame(self):
        """
        Get the last captured frame.
        
        Returns:
            Last captured frame, or None if no frame has been captured
        """
        return self.last_frame
