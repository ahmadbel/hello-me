"""
Scanner Interface Module
This module provides the scanner interface for the Enhanced Attendance System.
"""

import os
import sys
import tkinter as tk
from tkinter import ttk, messagebox
import threading
import datetime
import cv2
import numpy as np
import pandas as pd
import logging
import time

# Add parent directory to path
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(os.path.dirname(current_dir))
sys.path.append(parent_dir)

# Import modules
from core.data_management.config import ConfigManager
from core.data_management.database import DatabaseManager
from core.data_management.attendance_logger import AttendanceLogger
from core.data_management.alert_system import AlertSystem
from core.face_recognition.face_detector import FaceDetector
from core.face_recognition.face_recognizer import FaceRecognizer
from utils.logger import Logger
from utils.ui_components import ModernUI, CameraFeed
from utils.theme_manager import ThemeManager

class ScannerApp:
    """
    Scanner interface for the Enhanced Attendance System.
    """
    
    def __init__(self, root):
        """
        Initialize the scanner interface.
        
        Args:
            root: Tkinter root window
        """
        self.root = root
        self.logger = Logger()
        
        # Initialize configuration
        self.config = ConfigManager()
        
        # Initialize database
        self.db = DatabaseManager()
        
        # Initialize attendance logger with default subject
        self.attendance_logger = AttendanceLogger(self.db, self.config)
        
        # Set default subject for automatic scanning
        default_subject = self.config.get_value('General', 'DefaultSubject', 'General')
        self.attendance_logger.set_subject(default_subject)
        
        # Initialize theme manager
        self.theme_manager = ThemeManager()
        
        # Get paths
        cascade_path = self.config.get_path('FaceRecognition', 'CascadePath')
        model_path = self.config.get_path('FaceRecognition', 'ModelPath')
        
        # Initialize face recognition components
        try:
            self.face_detector = FaceDetector(cascade_path)
            self.face_recognizer = FaceRecognizer(model_path)
            
            # Check if face module is available
            if not self.face_recognizer.is_face_module_available():
                self._show_opencv_contrib_warning()
                
            # Initialize alert system
            self.alert_system = AlertSystem(self.config)
            
            # Set up the interface
            self.setup_interface()
            
            # Scanning state
            self.scanning = False
            self.scan_thread = None
            
            # Camera state
            self.camera_started = False
            
            # Auto-start scanning
            self.auto_start_enabled = True
            
        except Exception as e:
            self.logger.error(f"Error initializing scanner interface: {e}")
            messagebox.showerror("Error", f"Failed to initialize scanner interface: {e}\n\nPlease check that all required files are present.")
    
    def _show_opencv_contrib_warning(self):
        """Show a warning about missing OpenCV contrib modules."""
        messagebox.showwarning(
            "OpenCV Contrib Missing",
            "The OpenCV face recognition module is not available. Some features will be limited.\n\n"
            "For full functionality, please install opencv-contrib-python:\n"
            "1. pip uninstall opencv-python\n"
            "2. pip install opencv-contrib-python"
        )
    
    def setup_interface(self):
        """Set up the scanner interface."""
        # Configure the root window
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)
        
        # Create main frame
        self.main_frame = ttk.Frame(self.root, padding=20)
        self.main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Create top frame for controls
        top_frame = ttk.Frame(self.main_frame, padding=10)
        top_frame.pack(fill=tk.X)
        
        # Subject entry (now with default value and optional)
        subject_frame = ttk.Frame(top_frame)
        subject_frame.pack(side=tk.LEFT, padx=10)
        
        subject_label = ttk.Label(subject_frame, text="Subject (Optional):")
        subject_label.pack(side=tk.LEFT, padx=5)
        
        default_subject = self.config.get_value('General', 'DefaultSubject', 'General')
        self.subject_var = tk.StringVar(value=default_subject)
        subject_entry = ttk.Entry(subject_frame, textvariable=self.subject_var, width=20)
        subject_entry.pack(side=tk.LEFT)
        
        # Auto-start checkbox
        auto_frame = ttk.Frame(top_frame)
        auto_frame.pack(side=tk.LEFT, padx=10)
        
        self.auto_start_var = tk.BooleanVar(value=True)
        auto_check = ttk.Checkbutton(
            auto_frame, 
            text="Auto-start scanning", 
            variable=self.auto_start_var,
            command=self.toggle_auto_start
        )
        auto_check.pack(side=tk.LEFT)
        
        # Buttons
        buttons_frame = ttk.Frame(top_frame)
        buttons_frame.pack(side=tk.RIGHT, padx=10)
        
        self.start_btn = ttk.Button(
            buttons_frame,
            text="Start Scanning",
            command=self.start_scanning
        )
        self.start_btn.pack(side=tk.LEFT, padx=5)
        
        self.stop_btn = ttk.Button(
            buttons_frame,
            text="Stop Scanning",
            command=self.stop_scanning,
            state=tk.DISABLED
        )
        self.stop_btn.pack(side=tk.LEFT, padx=5)
        
        # Create middle frame for camera and alert
        middle_frame = ttk.Frame(self.main_frame, padding=10)
        middle_frame.pack(fill=tk.BOTH, expand=True)
        
        # Camera frame
        camera_frame = ttk.LabelFrame(middle_frame, text="Camera Feed", padding=10)
        camera_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Create camera feed
        self.camera_feed = CameraFeed(camera_frame, width=640, height=480)
        
        # Camera controls
        controls_frame = ttk.Frame(camera_frame)
        controls_frame.pack(fill=tk.X, pady=10)
        
        # Camera selection
        camera_select_frame = ttk.Frame(controls_frame)
        camera_select_frame.pack(side=tk.LEFT, padx=5)
        
        camera_label = ttk.Label(camera_select_frame, text="Camera:")
        camera_label.pack(side=tk.LEFT, padx=5)
        
        self.camera_index_var = tk.IntVar(value=0)
        camera_spinbox = ttk.Spinbox(
            camera_select_frame,
            from_=0,
            to=10,
            textvariable=self.camera_index_var,
            width=5
        )
        camera_spinbox.pack(side=tk.LEFT)
        
        # Camera buttons
        start_cam_btn = ttk.Button(
            controls_frame,
            text="Start Camera",
            command=self.start_camera
        )
        start_cam_btn.pack(side=tk.LEFT, padx=5)
        
        stop_cam_btn = ttk.Button(
            controls_frame,
            text="Stop Camera",
            command=self.stop_camera
        )
        stop_cam_btn.pack(side=tk.LEFT, padx=5)
        
        # Try different camera button
        try_diff_cam_btn = ttk.Button(
            controls_frame,
            text="Try Different Camera",
            command=self.try_different_camera
        )
        try_diff_cam_btn.pack(side=tk.LEFT, padx=5)
        
        # Alert frame
        alert_frame = ttk.LabelFrame(middle_frame, text="Security Alerts", padding=10)
        alert_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        
        # Create alert display
        self.alert_display = self.alert_system.create_alert_display(alert_frame)
        self.alert_display.pack(fill=tk.BOTH, expand=True)
        
        # Create bottom frame for recognition log
        bottom_frame = ttk.LabelFrame(self.main_frame, text="Recognition Log", padding=10)
        bottom_frame.pack(fill=tk.BOTH, expand=True)
        
        # Create treeview
        columns = ("time", "id", "name", "confidence", "status")
        self.log_tree = ttk.Treeview(bottom_frame, columns=columns, show="headings")
        
        # Define headings
        self.log_tree.heading("time", text="Time")
        self.log_tree.heading("id", text="Student ID")
        self.log_tree.heading("name", text="Name")
        self.log_tree.heading("confidence", text="Confidence")
        self.log_tree.heading("status", text="Status")
        
        # Define columns
        self.log_tree.column("time", width=100)
        self.log_tree.column("id", width=100)
        self.log_tree.column("name", width=200)
        self.log_tree.column("confidence", width=100)
        self.log_tree.column("status", width=100)
        
        # Add scrollbars
        y_scrollbar = ttk.Scrollbar(bottom_frame, orient=tk.VERTICAL, command=self.log_tree.yview)
        self.log_tree.configure(yscrollcommand=y_scrollbar.set)
        
        # Pack everything
        self.log_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        y_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Add theme toggle button
        theme_frame = ttk.Frame(self.root, padding=5)
        theme_frame.pack(fill=tk.X)
        
        theme_btn = self.theme_manager.create_theme_toggle_button(
            theme_frame,
            callback=self.on_theme_change
        )
        theme_btn.pack(side=tk.RIGHT, padx=10, pady=5)
        
        # Status bar
        self.status_var = tk.StringVar(value="Ready")
        status_bar = ttk.Label(self.root, textvariable=self.status_var, relief=tk.SUNKEN, anchor=tk.W)
        status_bar.pack(side=tk.BOTTOM, fill=tk.X)
        
        # Auto-start camera when interface is ready
        self.root.after(1000, self.auto_start_camera)
    
    def auto_start_camera(self):
        """Automatically start the camera when the interface is ready."""
        if not self.camera_started:
            self.start_camera()
            # If auto-start is enabled, start scanning after camera is initialized
            if self.auto_start_var.get():
                self.root.after(2000, self.start_scanning)
    
    def toggle_auto_start(self):
        """Toggle auto-start scanning."""
        self.auto_start_enabled = self.auto_start_var.get()
    
    def start_camera(self):
        """Start the camera feed."""
        # Get camera index
        camera_index = self.camera_index_var.get()
        
        # Update camera index in feed
        self.camera_feed.camera_index = camera_index
        
        if self.camera_feed.start():
            # Add face detection processor
            self.camera_feed.add_frame_processor(self.process_frame)
            self.status_var.set(f"Camera {camera_index} started")
            self.camera_started = True
        else:
            messagebox.showerror("Error", f"Failed to start camera {camera_index}. Try a different camera index.")
            self.camera_started = False
    
    def stop_camera(self):
        """Stop the camera feed."""
        self.camera_feed.stop()
        self.status_var.set("Camera stopped")
        self.camera_started = False
        
        # If scanning, stop it
        if self.scanning:
            self.stop_scanning()
    
    def try_different_camera(self):
        """Try a different camera."""
        # Stop current camera
        if self.camera_started:
            self.stop_camera()
        
        # Increment camera index
        current_index = self.camera_index_var.get()
        new_index = (current_index + 1) % 10  # Cycle through 0-9
        self.camera_index_var.set(new_index)
        
        # Start new camera
        self.start_camera()
    
    def process_frame(self, frame):
        """
        Process a frame from the camera feed.
        
        Args:
            frame: Frame to process
            
        Returns:
            Frame with faces detected
        """
        try:
            if frame is None:
                return np.zeros((480, 640, 3), dtype=np.uint8)  # Return black frame
                
            # Detect faces
            result_frame, faces = self.face_detector.detect_and_draw(frame)
            
            # If scanning, process each face
            if self.scanning and faces is not None and len(faces) > 0:
                for face_rect in faces:
                    x, y, w, h = face_rect
                    
                    # Ensure face region is valid
                    if x < 0 or y < 0 or x+w > frame.shape[1] or y+h > frame.shape[0]:
                        continue
                        
                    face_img = frame[y:y+h, x:x+w]
                    
                    # Skip empty or invalid face images
                    if face_img is None or face_img.size == 0:
                        continue
                    
                    # Recognize face if face module is available
                    if self.face_recognizer.is_face_module_available() and self.face_recognizer.is_model_loaded():
                        student_id, confidence = self.face_recognizer.recognize_face(face_img)
                        
                        # Get confidence threshold
                        threshold = float(self.config.get_value('FaceRecognition', 'ConfidenceThreshold', '80'))
                        
                        if student_id != -1 and confidence < 100 - threshold:
                            # Known student
                            student_name = self.db.get_student_name(str(student_id))
                            
                            # Mark attendance
                            subject = self.subject_var.get().strip()
                            if not subject:  # If subject is empty, use default
                                subject = self.config.get_value('General', 'DefaultSubject', 'General')
                                
                            self.attendance_logger.set_subject(subject)
                            self.db.mark_attendance(str(student_id), subject)
                            
                            # Add to log
                            self.add_to_log(str(student_id), student_name, confidence, "Recognized")
                            
                            # Draw green box and name
                            cv2.rectangle(result_frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
                            cv2.putText(
                                result_frame,
                                f"{student_name} ({confidence:.2f})",
                                (x, y - 10),
                                cv2.FONT_HERSHEY_SIMPLEX,
                                0.5,
                                (0, 255, 0),
                                2
                            )
                        else:
                            # Unknown person
                            self.add_to_log("Unknown", "Unknown", confidence, "Alert")
                            
                            # Trigger alert
                            self.alert_system.trigger_alert(frame, face_rect)
                            
                            # Draw red box
                            cv2.rectangle(result_frame, (x, y), (x + w, y + h), (0, 0, 255), 2)
                            cv2.putText(
                                result_frame,
                                "Unknown",
                                (x, y - 10),
                                cv2.FONT_HERSHEY_SIMPLEX,
                                0.5,
                                (0, 0, 255),
                                2
                            )
                    else:
                        # Face module not available or model not loaded
                        # Just draw yellow box
                        cv2.rectangle(result_frame, (x, y), (x + w, y + h), (0, 255, 255), 2)
                        cv2.putText(
                            result_frame,
                            "Face Detection Only",
                            (x, y - 10),
                            cv2.FONT_HERSHEY_SIMPLEX,
                            0.5,
                            (0, 255, 255),
                            2
                        )
            
            return result_frame
        except Exception as e:
            self.logger.error(f"Error processing frame: {e}")
            return frame
    
    def start_scanning(self):
        """Start automatic attendance scanning."""
        # Check if camera is running
        if not self.camera_feed.is_running():
            messagebox.showerror("Error", "Camera is not running. Please start the camera first.")
            return
        
        # Get subject (optional now)
        subject = self.subject_var.get().strip()
        if not subject:
            # Use default subject
            subject = self.config.get_value('General', 'DefaultSubject', 'General')
            self.subject_var.set(subject)
        
        # Update attendance logger subject
        self.attendance_logger.set_subject(subject)
        
        # Check if face recognition is available
        if not self.face_recognizer.is_face_module_available():
            result = messagebox.askquestion(
                "Limited Functionality",
                "Face recognition module is not available. Only face detection will work.\n\n"
                "Do you want to continue with limited functionality?",
                icon='warning'
            )
            if result != 'yes':
                return
        
        # Check if model is loaded
        if self.face_recognizer.is_face_module_available() and not self.face_recognizer.is_model_loaded():
            result = messagebox.askquestion(
                "No Face Recognition Model",
                "No face recognition model is loaded. Only face detection will work.\n\n"
                "Do you want to continue with limited functionality?",
                icon='warning'
            )
            if result != 'yes':
                return
        
        # Start scanning
        self.scanning = True
        self.start_btn.config(state=tk.DISABLED)
        self.stop_btn.config(state=tk.NORMAL)
        self.status_var.set(f"Scanning started - Subject: {subject}")
        
        # Clear log
        for item in self.log_tree.get_children():
            self.log_tree.delete(item)
    
    def stop_scanning(self):
        """Stop automatic attendance scanning."""
        self.scanning = False
        self.start_btn.config(state=tk.NORMAL)
        self.stop_btn.config(state=tk.DISABLED)
        self.status_var.set("Scanning stopped")
    
    def add_to_log(self, student_id, name, confidence, status):
        """
        Add a recognition event to the log.
        
        Args:
            student_id (str): Student ID
            name (str): Student name
            confidence (float): Recognition confidence
            status (str): Recognition status
        """
        # Get current time
        current_time = datetime.datetime.now().strftime("%H:%M:%S")
        
        # Add to treeview
        self.log_tree.insert(
            "",
            0,  # Insert at the top
            values=(current_time, student_id, name, f"{confidence:.2f}", status)
        )
        
        # Limit log size
        if len(self.log_tree.get_children()) > 100:
            # Remove oldest entry
            oldest = self.log_tree.get_children()[-1]
            self.log_tree.delete(oldest)
    
    def on_theme_change(self, theme_name):
        """
        Handle theme change.
        
        Args:
            theme_name (str): New theme name
        """
        # Update configuration
        self.config.set_value("General", "Theme", theme_name)
    
    def on_close(self):
        """Handle window close event."""
        # Stop scanning if running
        if self.scanning:
            self.stop_scanning()
        
        # Stop camera if running
        if self.camera_feed.is_running():
            self.camera_feed.stop()
        
        # Destroy window
        self.root.destroy()

# For testing
if __name__ == "__main__":
    root = tk.Tk()
    app = ScannerApp(root)
    root.mainloop()
