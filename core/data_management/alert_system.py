"""
Alert System Module
This module provides functionality for security alerts when unauthorized individuals are detected.
"""

import os
import time
import datetime
import threading
import cv2
import numpy as np
from PIL import Image, ImageTk
import tkinter as tk
from tkinter import ttk
import json
import threading

class AlertSystem:
    """
    A class for managing security alerts when unauthorized individuals are detected.
    """
    
    def __init__(self, config):
        """
        Initialize the alert system.
        
        Args:
            config: Configuration manager
        """
        self.config = config
        
        # Alert settings
        self.alert_active = False
        self.alert_time = None
        self.alert_duration = 30  # seconds
        self.alert_cooldown = 10  # seconds
        self.last_alert_time = 0
        
        # Alert images
        self.alert_images_dir = self.config.get_path('AlertSystem', 'AlertImagesDirectory', 'data/alerts')
        os.makedirs(self.alert_images_dir, exist_ok=True)
        
        # Alert sound
        self.sound_enabled = self.config.get_value('AlertSystem', 'SoundEnabled', 'True').lower() == 'true'
        
        # Initialize sound system if enabled
        if self.sound_enabled:
            try:
                # Use simpler sound approach to avoid pygame dependency
                self._initialize_sound()
            except Exception as e:
                print(f"Error initializing sound system: {e}")
                self.sound_enabled = False
    
    def _initialize_sound(self):
        """Initialize the sound system."""
        # We'll use a simpler approach without pygame
        # This will be a placeholder that doesn't actually play sounds
        # but allows the system to run without the pygame dependency
        self.sound_initialized = True
        print("Sound system initialized (placeholder)")
    
    def _play_alert_sound(self):
        """Play the alert sound."""
        if not self.sound_enabled or not hasattr(self, 'sound_initialized'):
            return
        
        # This is a placeholder that would normally play a sound
        print("ALERT SOUND PLAYING (placeholder)")
    
    def trigger_alert(self, frame, face_location):
        """
        Trigger a security alert.
        
        Args:
            frame: Frame containing the unauthorized individual
            face_location: Location of the face in the frame (x, y, w, h)
            
        Returns:
            bool: True if alert was triggered, False otherwise
        """
        current_time = time.time()
        
        # Check if we're in cooldown period
        if current_time - self.last_alert_time < self.alert_cooldown:
            return False
        
        # Set alert state
        self.alert_active = True
        self.alert_time = current_time
        self.last_alert_time = current_time
        
        # Save alert image
        self._save_alert_image(frame, face_location)
        
        # Play alert sound
        if self.sound_enabled:
            threading.Thread(target=self._play_alert_sound).start()
        
        # Start alert expiration thread
        threading.Thread(target=self._expire_alert).start()
        
        return True
    
    def _save_alert_image(self, frame, face_location):
        """
        Save an image of the alert.
        
        Args:
            frame: Frame containing the unauthorized individual
            face_location: Location of the face in the frame (x, y, w, h)
            
        Returns:
            str: Path to the saved image
        """
        # Create a copy of the frame
        alert_frame = frame.copy()
        
        # Draw a red box around the face
        x, y, w, h = face_location
        cv2.rectangle(alert_frame, (x, y), (x + w, y + h), (0, 0, 255), 2)
        
        # Add timestamp
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        cv2.putText(
            alert_frame,
            f"UNAUTHORIZED: {timestamp}",
            (10, 30),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.7,
            (0, 0, 255),
            2
        )
        
        # Generate filename with timestamp
        filename = f"alert_{int(time.time())}.jpg"
        filepath = os.path.join(self.alert_images_dir, filename)
        
        # Save the image
        cv2.imwrite(filepath, alert_frame)
        
        return filepath
    
    def _expire_alert(self):
        """Expire the alert after the specified duration."""
        time.sleep(self.alert_duration)
        
        # Check if this is still the active alert
        if self.alert_time and time.time() - self.alert_time >= self.alert_duration:
            self.alert_active = False
            self.alert_time = None
    
    def is_alert_active(self):
        """
        Check if an alert is currently active.
        
        Returns:
            bool: True if an alert is active, False otherwise
        """
        return self.alert_active
    
    def reset_alert(self):
        """Reset the alert state."""
        self.alert_active = False
        self.alert_time = None
    
    def get_recent_alerts(self, count=5):
        """
        Get recent alerts.
        
        Args:
            count (int): Number of recent alerts to retrieve
            
        Returns:
            list: List of recent alert image paths
        """
        # Get all alert images
        alert_images = []
        for filename in os.listdir(self.alert_images_dir):
            if filename.startswith("alert_") and filename.endswith(".jpg"):
                filepath = os.path.join(self.alert_images_dir, filename)
                alert_images.append((filepath, os.path.getmtime(filepath)))
        
        # Sort by modification time (newest first)
        alert_images.sort(key=lambda x: x[1], reverse=True)
        
        # Return the specified number of recent alerts
        return [filepath for filepath, _ in alert_images[:count]]
    
    def create_alert_display(self, parent):
        """
        Create a display for showing alerts.
        
        Args:
            parent: Parent widget
            
        Returns:
            ttk.Frame: The created frame
        """
        # Create frame
        frame = ttk.Frame(parent)
        
        # Create label for alert status
        self.alert_status_var = tk.StringVar(value="No active alerts")
        status_label = ttk.Label(
            frame,
            textvariable=self.alert_status_var,
            font=('Helvetica', 12, 'bold'),
            foreground='green'
        )
        status_label.pack(pady=(0, 10))
        
        # Create canvas for alert image
        self.alert_canvas = tk.Canvas(frame, width=320, height=240, bg='black')
        self.alert_canvas.pack(pady=(0, 10))
        
        # Add "No Alert" text
        self.alert_canvas.create_text(
            160, 120,
            text="No Active Alert",
            fill='white',
            font=('Helvetica', 14, 'bold')
        )
        
        # Create buttons
        buttons_frame = ttk.Frame(frame)
        buttons_frame.pack(fill=tk.X)
        
        reset_btn = ttk.Button(
            buttons_frame,
            text="Reset Alert",
            command=self.reset_alert
        )
        reset_btn.pack(side=tk.LEFT, padx=5)
        
        view_btn = ttk.Button(
            buttons_frame,
            text="View Recent Alerts",
            command=self._show_recent_alerts
        )
        view_btn.pack(side=tk.LEFT, padx=5)
        
        # Start update thread
        self.alert_display_active = True
        threading.Thread(target=self._update_alert_display).start()
        
        return frame
    
    def _update_alert_display(self):
        """Update the alert display."""
        while self.alert_display_active:
            try:
                if self.is_alert_active():
                    # Update status
                    self.alert_status_var.set("⚠️ ALERT: Unauthorized individual detected!")
                    
                    # Get most recent alert image
                    recent_alerts = self.get_recent_alerts(1)
                    if recent_alerts:
                        # Load and display image
                        img = Image.open(recent_alerts[0])
                        img = img.resize((320, 240), Image.LANCZOS)
                        photo = ImageTk.PhotoImage(img)
                        
                        # Update canvas
                        self.alert_canvas.delete("all")
                        self.alert_canvas.create_image(0, 0, image=photo, anchor=tk.NW)
                        self.alert_canvas.photo = photo  # Keep a reference
                else:
                    # Update status
                    self.alert_status_var.set("No active alerts")
                    
                    # Clear canvas
                    self.alert_canvas.delete("all")
                    self.alert_canvas.create_text(
                        160, 120,
                        text="No Active Alert",
                        fill='white',
                        font=('Helvetica', 14, 'bold')
                    )
            except Exception as e:
                print(f"Error updating alert display: {e}")
            
            # Sleep for a short time
            time.sleep(1.0)
    
    def _show_recent_alerts(self):
        """Show recent alerts in a new window."""
        # Get recent alerts
        recent_alerts = self.get_recent_alerts(5)
        
        if not recent_alerts:
            # No recent alerts
            return
        
        # Create new window
        alert_window = tk.Toplevel()
        alert_window.title("Recent Alerts")
        alert_window.geometry("800x600")
        
        # Create main frame
        main_frame = ttk.Frame(alert_window, padding=10)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Create title
        title_label = ttk.Label(
            main_frame,
            text="Recent Security Alerts",
            font=('Helvetica', 16, 'bold')
        )
        title_label.pack(pady=(0, 20))
        
        # Create grid for alert images
        grid_frame = ttk.Frame(main_frame)
        grid_frame.pack(fill=tk.BOTH, expand=True)
        
        # Add alert images to grid
        self.alert_photos = []  # Keep references to prevent garbage collection
        
        for i, alert_path in enumerate(recent_alerts):
            # Create frame for this alert
            alert_frame = ttk.Frame(grid_frame, padding=5)
            alert_frame.grid(row=i // 2, column=i % 2, padx=10, pady=10, sticky=tk.NSEW)
            
            try:
                # Load image
                img = Image.open(alert_path)
                img = img.resize((350, 250), Image.LANCZOS)
                photo = ImageTk.PhotoImage(img)
                self.alert_photos.append(photo)
                
                # Create image label
                img_label = ttk.Label(alert_frame, image=photo)
                img_label.pack(pady=(0, 5))
                
                # Add timestamp from filename
                filename = os.path.basename(alert_path)
                timestamp = filename.replace("alert_", "").replace(".jpg", "")
                try:
                    # Convert timestamp to readable format
                    dt = datetime.datetime.fromtimestamp(int(timestamp))
                    timestamp_str = dt.strftime("%Y-%m-%d %H:%M:%S")
                except:
                    timestamp_str = timestamp
                
                time_label = ttk.Label(
                    alert_frame,
                    text=f"Time: {timestamp_str}",
                    font=('Helvetica', 10)
                )
                time_label.pack()
            except Exception as e:
                print(f"Error loading alert image {alert_path}: {e}")
        
        # Configure grid
        for i in range(2):
            grid_frame.columnconfigure(i, weight=1)
        for i in range((len(recent_alerts) + 1) // 2):
            grid_frame.rowconfigure(i, weight=1)
        
        # Add close button
        close_btn = ttk.Button(
            main_frame,
            text="Close",
            command=alert_window.destroy
        )
        close_btn.pack(pady=10)
