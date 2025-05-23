"""
Admin Interface Module
This module provides the admin interface for the Enhanced Attendance System.
"""

import os
import sys
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import threading
import datetime
import time
import cv2
import numpy as np
import pandas as pd
import logging

# Add parent directory to path
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(os.path.dirname(current_dir))
sys.path.append(parent_dir)

# Import modules
from core.data_management.config import ConfigManager
from core.data_management.database import DatabaseManager
from core.face_recognition.face_detector import FaceDetector
from core.face_recognition.face_recognizer import FaceRecognizer
from core.face_recognition.model_trainer import ModelTrainer
from utils.logger import Logger
from utils.ui_components import ModernUI, CameraFeed
from utils.theme_manager import ThemeManager

class AdminApp:
    """
    Admin interface for the Enhanced Attendance System.
    """
    
    def __init__(self, root):
        """
        Initialize the admin interface.
        
        Args:
            root: Tkinter root window
        """
        self.root = root
        self.logger = Logger()
        
        # Initialize configuration
        self.config = ConfigManager()
        
        # Initialize database
        self.db = DatabaseManager()
        
        # Initialize theme manager
        self.theme_manager = ThemeManager()
        
        # --- Robustly initialize all attributes --- 
        # Face capture variables (initialize early and unconditionally)
        self.capture_active = False
        self.capture_count = 0
        self.total_captures = 20  # Ensure this is defined
        self.last_capture_time = 0
        self.capture_delay = 0.5  # Ensure this is defined
        self.student_id_for_capture = None
        
        # Standard face size for consistent processing
        self.face_width = 100
        self.face_height = 100
        
        # Initialize UI elements to None first
        self.notebook = None
        self.id_var = None
        self.name_var = None
        self.register_btn = None
        self.capture_btn = None
        self.train_btn = None
        self.camera_feed = None
        self.status_var = None
        self.progress_var = None
        self.preview_canvas = None
        self.capture_count_var = None
        self.face_detected_var = None
        self.attendance_tree = None
        self.report_tree = None
        self.summary_text = None
        self.subject_var = None
        self.date_var = None
        self.report_subject_var = None
        self.from_date_var = None
        self.to_date_var = None
        self.min_face_var = None
        self.scale_var = None
        self.neighbors_var = None
        self.confidence_var = None
        self.duration_var = None
        self.cooldown_var = None
        self.sound_var = None
        
        # Initialize face recognition components (can fail)
        self.face_detector = None
        self.face_recognizer = None
        try:
            cascade_path = self.config.get_path("FaceRecognition", "CascadePath")
            model_path = self.config.get_path("FaceRecognition", "ModelPath")
            self.face_detector = FaceDetector(cascade_path)
            self.face_recognizer = FaceRecognizer(model_path)
            
            # Check if face module is available
            if not self.face_recognizer.is_face_module_available():
                self._show_opencv_contrib_warning()
        except Exception as e:
            self.logger.error(f"Error initializing face recognition: {e}")
            messagebox.showerror("Error", f"Failed to initialize face recognition: {e}\n\nPlease check that all required files are present.")
            # Continue initialization even if face recognition fails
        
        # Set up the interface
        self.setup_interface()
    
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
        """Set up the admin interface."""
        # Configure the root window
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)
        
        # Create main notebook
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill=tk.BOTH, expand=True)
        
        # Create tabs
        self.create_registration_tab()
        self.create_attendance_tab()
        self.create_reports_tab()
        self.create_settings_tab()
        
        # Add theme toggle button
        theme_frame = ttk.Frame(self.root, padding=5)
        theme_frame.pack(fill=tk.X)
        
        theme_btn = self.theme_manager.create_theme_toggle_button(
            theme_frame,
            callback=self.on_theme_change
        )
        theme_btn.pack(side=tk.RIGHT, padx=10, pady=5)
        
        # Apply initial theme
        self.theme_manager.apply_theme_to_widgets(self.root)
    
    def create_registration_tab(self):
        """Create the student registration tab."""
        # Create tab
        tab = ttk.Frame(self.notebook, padding=20)
        self.notebook.add(tab, text="Student Registration")
        
        # Create left frame for form
        left_frame = ttk.Frame(tab, padding=10)
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Create right frame for camera
        right_frame = ttk.Frame(tab, padding=10)
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        
        # Create form
        form_frame = ttk.LabelFrame(left_frame, text="Student Information", padding=10)
        form_frame.pack(fill=tk.BOTH, expand=True)
        
        # Student ID
        id_frame = ttk.Frame(form_frame)
        id_frame.pack(fill=tk.X, pady=5)
        
        id_label = ttk.Label(id_frame, text="Student ID:", width=15)
        id_label.pack(side=tk.LEFT)
        
        self.id_var = tk.StringVar()
        id_entry = ttk.Entry(id_frame, textvariable=self.id_var)
        id_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        # Student Name
        name_frame = ttk.Frame(form_frame)
        name_frame.pack(fill=tk.X, pady=5)
        
        name_label = ttk.Label(name_frame, text="Student Name:", width=15)
        name_label.pack(side=tk.LEFT)
        
        self.name_var = tk.StringVar()
        name_entry = ttk.Entry(name_frame, textvariable=self.name_var)
        name_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        # Buttons
        buttons_frame = ttk.Frame(form_frame)
        buttons_frame.pack(fill=tk.X, pady=10)
        
        self.register_btn = ttk.Button(
            buttons_frame,
            text="Register Student",
            command=self.register_student
        )
        self.register_btn.pack(side=tk.LEFT, padx=5)
        
        self.capture_btn = ttk.Button(
            buttons_frame,
            text="Capture Images",
            command=self.start_capture,
            state=tk.DISABLED
        )
        self.capture_btn.pack(side=tk.LEFT, padx=5)
        
        self.train_btn = ttk.Button(
            buttons_frame,
            text="Train Model",
            command=self.train_model
        )
        self.train_btn.pack(side=tk.LEFT, padx=5)
        
        # Create camera frame
        camera_frame = ttk.LabelFrame(right_frame, text="Camera", padding=10)
        camera_frame.pack(fill=tk.BOTH, expand=True)
        
        # Create camera feed
        self.camera_feed = CameraFeed(camera_frame, width=400, height=300)
        
        # Create status frame
        status_frame = ttk.Frame(camera_frame)
        status_frame.pack(fill=tk.X, pady=10)
        
        self.status_var = tk.StringVar(value="Ready")
        status_label = ttk.Label(status_frame, textvariable=self.status_var)
        status_label.pack(side=tk.LEFT)
        
        self.progress_var = tk.IntVar(value=0)
        progress_bar = ttk.Progressbar(
            status_frame,
            variable=self.progress_var,
            maximum=100,
            length=200
        )
        progress_bar.pack(side=tk.RIGHT)
        
        # Camera controls
        controls_frame = ttk.Frame(camera_frame)
        controls_frame.pack(fill=tk.X)
        
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
        
        # Face preview frame
        preview_frame = ttk.LabelFrame(right_frame, text="Face Preview", padding=10)
        preview_frame.pack(fill=tk.X, pady=10)
        
        # Create canvas for face preview
        self.preview_canvas = tk.Canvas(preview_frame, width=100, height=100, bg="black")
        self.preview_canvas.pack(side=tk.LEFT, padx=10)
        
        # Create capture info
        capture_info_frame = ttk.Frame(preview_frame)
        capture_info_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        self.capture_count_var = tk.StringVar(value=f"Captures: 0/{self.total_captures}")
        capture_count_label = ttk.Label(capture_info_frame, textvariable=self.capture_count_var)
        capture_count_label.pack(anchor=tk.W, pady=5)
        
        self.face_detected_var = tk.StringVar(value="Face detected: No")
        face_detected_label = ttk.Label(capture_info_frame, textvariable=self.face_detected_var)
        face_detected_label.pack(anchor=tk.W, pady=5)
    
    def create_attendance_tab(self):
        """Create the attendance management tab."""
        # Create tab
        tab = ttk.Frame(self.notebook, padding=20)
        self.notebook.add(tab, text="Attendance Management")
        
        # Create top frame for filters
        top_frame = ttk.Frame(tab, padding=10)
        top_frame.pack(fill=tk.X)
        
        # Subject filter
        subject_frame = ttk.Frame(top_frame)
        subject_frame.pack(side=tk.LEFT, padx=10)
        
        subject_label = ttk.Label(subject_frame, text="Subject:")
        subject_label.pack(side=tk.LEFT, padx=5)
        
        self.subject_var = tk.StringVar()
        subject_entry = ttk.Entry(subject_frame, textvariable=self.subject_var, width=20)
        subject_entry.pack(side=tk.LEFT)
        
        # Date filter
        date_frame = ttk.Frame(top_frame)
        date_frame.pack(side=tk.LEFT, padx=10)
        
        date_label = ttk.Label(date_frame, text="Date:")
        date_label.pack(side=tk.LEFT, padx=5)
        
        self.date_var = tk.StringVar(value=datetime.datetime.now().strftime("%Y-%m-%d"))
        date_entry = ttk.Entry(date_frame, textvariable=self.date_var, width=10)
        date_entry.pack(side=tk.LEFT)
        
        # Buttons
        buttons_frame = ttk.Frame(top_frame)
        buttons_frame.pack(side=tk.RIGHT, padx=10)
        
        load_btn = ttk.Button(
            buttons_frame,
            text="Load Attendance",
            command=self.load_attendance
        )
        load_btn.pack(side=tk.LEFT, padx=5)
        
        export_btn = ttk.Button(
            buttons_frame,
            text="Export CSV",
            command=self.export_attendance
        )
        export_btn.pack(side=tk.LEFT, padx=5)
        
        # Create attendance table
        table_frame = ttk.Frame(tab, padding=10)
        table_frame.pack(fill=tk.BOTH, expand=True)
        
        # Create treeview
        columns = ("id", "name", "time", "date")
        self.attendance_tree = ttk.Treeview(table_frame, columns=columns, show="headings")
        
        # Define headings
        self.attendance_tree.heading("id", text="Student ID")
        self.attendance_tree.heading("name", text="Name")
        self.attendance_tree.heading("time", text="Time")
        self.attendance_tree.heading("date", text="Date")
        
        # Define columns
        self.attendance_tree.column("id", width=100)
        self.attendance_tree.column("name", width=200)
        self.attendance_tree.column("time", width=100)
        self.attendance_tree.column("date", width=100)
        
        # Add scrollbars
        y_scrollbar = ttk.Scrollbar(table_frame, orient=tk.VERTICAL, command=self.attendance_tree.yview)
        self.attendance_tree.configure(yscrollcommand=y_scrollbar.set)
        
        x_scrollbar = ttk.Scrollbar(table_frame, orient=tk.HORIZONTAL, command=self.attendance_tree.xview)
        self.attendance_tree.configure(xscrollcommand=x_scrollbar.set)
        
        # Pack everything
        self.attendance_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        y_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        x_scrollbar.pack(side=tk.BOTTOM, fill=tk.X)
    
    def create_reports_tab(self):
        """Create the reports tab."""
        # Create tab
        tab = ttk.Frame(self.notebook, padding=20)
        self.notebook.add(tab, text="Reports")
        
        # Create filters frame
        filters_frame = ttk.Frame(tab, padding=10)
        filters_frame.pack(fill=tk.X)
        
        # Subject filter
        subject_frame = ttk.Frame(filters_frame)
        subject_frame.pack(side=tk.LEFT, padx=10)
        
        subject_label = ttk.Label(subject_frame, text="Subject:")
        subject_label.pack(side=tk.LEFT, padx=5)
        
        self.report_subject_var = tk.StringVar()
        subject_entry = ttk.Entry(subject_frame, textvariable=self.report_subject_var, width=20)
        subject_entry.pack(side=tk.LEFT)
        
        # Date range filter
        date_frame = ttk.Frame(filters_frame)
        date_frame.pack(side=tk.LEFT, padx=10)
        
        from_label = ttk.Label(date_frame, text="From:")
        from_label.pack(side=tk.LEFT, padx=5)
        
        self.from_date_var = tk.StringVar(value=(datetime.datetime.now() - datetime.timedelta(days=30)).strftime("%Y-%m-%d"))
        from_entry = ttk.Entry(date_frame, textvariable=self.from_date_var, width=10)
        from_entry.pack(side=tk.LEFT)
        
        to_label = ttk.Label(date_frame, text="To:")
        to_label.pack(side=tk.LEFT, padx=5)
        
        self.to_date_var = tk.StringVar(value=datetime.datetime.now().strftime("%Y-%m-%d"))
        to_entry = ttk.Entry(date_frame, textvariable=self.to_date_var, width=10)
        to_entry.pack(side=tk.LEFT)
        
        # Buttons
        buttons_frame = ttk.Frame(filters_frame)
        buttons_frame.pack(side=tk.RIGHT, padx=10)
        
        generate_btn = ttk.Button(
            buttons_frame,
            text="Generate Report",
            command=self.generate_report
        )
        generate_btn.pack(side=tk.LEFT, padx=5)
        
        export_btn = ttk.Button(
            buttons_frame,
            text="Export Report",
            command=self.export_report
        )
        export_btn.pack(side=tk.LEFT, padx=5)
        
        # Create report frame
        report_frame = ttk.Frame(tab, padding=10)
        report_frame.pack(fill=tk.BOTH, expand=True)
        
        # Create notebook for different report types
        report_notebook = ttk.Notebook(report_frame)
        report_notebook.pack(fill=tk.BOTH, expand=True)
        
        # Summary tab
        summary_tab = ttk.Frame(report_notebook, padding=10)
        report_notebook.add(summary_tab, text="Summary")
        
        # Create summary widgets
        summary_label = ttk.Label(summary_tab, text="Attendance Summary", font=("Helvetica", 14, "bold"))
        summary_label.pack(pady=10)
        
        self.summary_text = tk.Text(summary_tab, height=20, width=80)
        self.summary_text.pack(fill=tk.BOTH, expand=True)
        
        # Details tab
        details_tab = ttk.Frame(report_notebook, padding=10)
        report_notebook.add(details_tab, text="Details")
        
        # Create details widgets
        details_label = ttk.Label(details_tab, text="Attendance Details", font=("Helvetica", 14, "bold"))
        details_label.pack(pady=10)
        
        # Create treeview
        columns = ("id", "name", "date", "time", "subject")
        self.report_tree = ttk.Treeview(details_tab, columns=columns, show="headings")
        
        # Define headings
        self.report_tree.heading("id", text="Student ID")
        self.report_tree.heading("name", text="Name")
        self.report_tree.heading("date", text="Date")
        self.report_tree.heading("time", text="Time")
        self.report_tree.heading("subject", text="Subject")
        
        # Define columns
        self.report_tree.column("id", width=100)
        self.report_tree.column("name", width=200)
        self.report_tree.column("date", width=100)
        self.report_tree.column("time", width=100)
        self.report_tree.column("subject", width=150)
        
        # Add scrollbars
        y_scrollbar = ttk.Scrollbar(details_tab, orient=tk.VERTICAL, command=self.report_tree.yview)
        self.report_tree.configure(yscrollcommand=y_scrollbar.set)
        
        x_scrollbar = ttk.Scrollbar(details_tab, orient=tk.HORIZONTAL, command=self.report_tree.xview)
        self.report_tree.configure(xscrollcommand=x_scrollbar.set)
        
        # Pack everything
        self.report_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        y_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        x_scrollbar.pack(side=tk.BOTTOM, fill=tk.X)
    
    def create_settings_tab(self):
        """Create the settings tab."""
        # Create tab
        tab = ttk.Frame(self.notebook, padding=20)
        self.notebook.add(tab, text="Settings")
        
        # Create settings frame
        settings_frame = ttk.LabelFrame(tab, text="Application Settings", padding=10)
        settings_frame.pack(fill=tk.BOTH, expand=True)
        
        # Face recognition settings
        face_frame = ttk.LabelFrame(settings_frame, text="Face Recognition", padding=10)
        face_frame.pack(fill=tk.X, pady=10)
        
        # Min face size
        min_face_frame = ttk.Frame(face_frame)
        min_face_frame.pack(fill=tk.X, pady=5)
        
        min_face_label = ttk.Label(min_face_frame, text="Min Face Size:", width=20)
        min_face_label.pack(side=tk.LEFT)
        
        self.min_face_var = tk.StringVar(value=self.config.get_value("FaceRecognition", "MinFaceSize", "30"))
        min_face_entry = ttk.Entry(min_face_frame, textvariable=self.min_face_var, width=10)
        min_face_entry.pack(side=tk.LEFT)
        
        # Scale factor
        scale_frame = ttk.Frame(face_frame)
        scale_frame.pack(fill=tk.X, pady=5)
        
        scale_label = ttk.Label(scale_frame, text="Scale Factor:", width=20)
        scale_label.pack(side=tk.LEFT)
        
        self.scale_var = tk.StringVar(value=self.config.get_value("FaceRecognition", "ScaleFactor", "1.1"))
        scale_entry = ttk.Entry(scale_frame, textvariable=self.scale_var, width=10)
        scale_entry.pack(side=tk.LEFT)
        
        # Min neighbors
        neighbors_frame = ttk.Frame(face_frame)
        neighbors_frame.pack(fill=tk.X, pady=5)
        
        neighbors_label = ttk.Label(neighbors_frame, text="Min Neighbors:", width=20)
        neighbors_label.pack(side=tk.LEFT)
        
        self.neighbors_var = tk.StringVar(value=self.config.get_value("FaceRecognition", "MinNeighbors", "5"))
        neighbors_entry = ttk.Entry(neighbors_frame, textvariable=self.neighbors_var, width=10)
        neighbors_entry.pack(side=tk.LEFT)
        
        # Confidence threshold
        confidence_frame = ttk.Frame(face_frame)
        confidence_frame.pack(fill=tk.X, pady=5)
        
        confidence_label = ttk.Label(confidence_frame, text="Confidence Threshold:", width=20)
        confidence_label.pack(side=tk.LEFT)
        
        self.confidence_var = tk.StringVar(value=self.config.get_value("FaceRecognition", "ConfidenceThreshold", "80"))
        confidence_entry = ttk.Entry(confidence_frame, textvariable=self.confidence_var, width=10)
        confidence_entry.pack(side=tk.LEFT)
        
        # Alert settings
        alert_frame = ttk.LabelFrame(settings_frame, text="Alert System", padding=10)
        alert_frame.pack(fill=tk.X, pady=10)
        
        # Alert duration
        duration_frame = ttk.Frame(alert_frame)
        duration_frame.pack(fill=tk.X, pady=5)
        
        duration_label = ttk.Label(duration_frame, text="Alert Duration (s):", width=20)
        duration_label.pack(side=tk.LEFT)
        
        self.duration_var = tk.StringVar(value=self.config.get_value("AlertSystem", "AlertDuration", "30"))
        duration_entry = ttk.Entry(duration_frame, textvariable=self.duration_var, width=10)
        duration_entry.pack(side=tk.LEFT)
        
        # Alert cooldown
        cooldown_frame = ttk.Frame(alert_frame)
        cooldown_frame.pack(fill=tk.X, pady=5)
        
        cooldown_label = ttk.Label(cooldown_frame, text="Alert Cooldown (s):", width=20)
        cooldown_label.pack(side=tk.LEFT)
        
        self.cooldown_var = tk.StringVar(value=self.config.get_value("AlertSystem", "AlertCooldown", "10"))
        cooldown_entry = ttk.Entry(cooldown_frame, textvariable=self.cooldown_var, width=10)
        cooldown_entry.pack(side=tk.LEFT)
        
        # Sound enabled
        sound_frame = ttk.Frame(alert_frame)
        sound_frame.pack(fill=tk.X, pady=5)
        
        sound_label = ttk.Label(sound_frame, text="Sound Enabled:", width=20)
        sound_label.pack(side=tk.LEFT)
        
        self.sound_var = tk.BooleanVar(value=self.config.get_value("AlertSystem", "SoundEnabled", "True").lower() == "true")
        sound_check = ttk.Checkbutton(sound_frame, variable=self.sound_var)
        sound_check.pack(side=tk.LEFT)
        
        # Buttons
        buttons_frame = ttk.Frame(settings_frame)
        buttons_frame.pack(fill=tk.X, pady=10)
        
        save_btn = ttk.Button(
            buttons_frame,
            text="Save Settings",
            command=self.save_settings
        )
        save_btn.pack(side=tk.LEFT, padx=5)
        
        reset_btn = ttk.Button(
            buttons_frame,
            text="Reset to Defaults",
            command=self.reset_settings
        )
        reset_btn.pack(side=tk.LEFT, padx=5)
        
        # System information
        info_frame = ttk.LabelFrame(settings_frame, text="System Information", padding=10)
        info_frame.pack(fill=tk.X, pady=10)
        
        # OpenCV version
        opencv_frame = ttk.Frame(info_frame)
        opencv_frame.pack(fill=tk.X, pady=5)
        
        opencv_label = ttk.Label(opencv_frame, text="OpenCV Version:", width=20)
        opencv_label.pack(side=tk.LEFT)
        
        opencv_value = ttk.Label(opencv_frame, text=cv2.__version__)
        opencv_value.pack(side=tk.LEFT)
        
        # Face module status
        face_status_frame = ttk.Frame(info_frame)
        face_status_frame.pack(fill=tk.X, pady=5)
        
        face_status_label = ttk.Label(face_status_frame, text="Face Module Status:", width=20)
        face_status_label.pack(side=tk.LEFT)
        
        face_status = "Available" if hasattr(cv2, "face") else "Not Available (Install opencv-contrib-python)"
        face_status_value = ttk.Label(
            face_status_frame, 
            text=face_status,
            foreground="green" if hasattr(cv2, "face") else "red"
        )
        face_status_value.pack(side=tk.LEFT)
        
        # Model status
        model_frame = ttk.Frame(info_frame)
        model_frame.pack(fill=tk.X, pady=5)
        
        model_label = ttk.Label(model_frame, text="Recognition Model:", width=20)
        model_label.pack(side=tk.LEFT)
        
        model_status = "Loaded" if self.face_recognizer and self.face_recognizer.is_model_loaded() else "Not Loaded"
        model_value = ttk.Label(
            model_frame, 
            text=model_status,
            foreground="green" if self.face_recognizer and self.face_recognizer.is_model_loaded() else "red"
        )
        model_value.pack(side=tk.LEFT)
        
        # Database status
        db_frame = ttk.Frame(info_frame)
        db_frame.pack(fill=tk.X, pady=5)
        
        db_label = ttk.Label(db_frame, text="Database Status:", width=20)
        db_label.pack(side=tk.LEFT)
        
        db_status = "Connected" if self.db.is_connected() else "Not Connected"
        db_value = ttk.Label(
            db_frame, 
            text=db_status,
            foreground="green" if self.db.is_connected() else "red"
        )
        db_value.pack(side=tk.LEFT)
    
    def register_student(self):
        """Register a new student."""
        # Get student information
        student_id = self.id_var.get().strip()
        student_name = self.name_var.get().strip()
        
        # Validate input
        if not student_id:
            messagebox.showerror("Error", "Student ID is required")
            return
        
        if not student_name:
            messagebox.showerror("Error", "Student Name is required")
            return
        
        # Check if student already exists
        if self.db.student_exists(student_id):
            messagebox.showerror("Error", f"Student with ID {student_id} already exists")
            return
        
        # Add student to database
        if self.db.add_student(student_id, student_name):
            messagebox.showinfo("Success", f"Student {student_name} registered successfully")
            self.capture_btn.config(state=tk.NORMAL)
        else:
            messagebox.showerror("Error", "Failed to register student")
    
    def start_camera(self):
        """Start the camera feed."""
        if self.camera_feed.start():
            # Add face detection processor
            self.camera_feed.add_frame_processor(self.process_frame)
            self.status_var.set("Camera started")
        else:
            messagebox.showerror("Error", "Failed to start camera")
    
    def stop_camera(self):
        """Stop the camera feed."""
        self.camera_feed.stop()
        self.status_var.set("Camera stopped")
        
        # Reset face detection status
        self.face_detected_var.set("Face detected: No")
        
        # Clear preview
        self.preview_canvas.delete("all")
    
    def preprocess_face(self, face_img):
        """
        Preprocess a face image for consistent training.
        
        Args:
            face_img: Face image to preprocess
            
        Returns:
            numpy.ndarray: Preprocessed face image
        """
        try:
            # Convert to grayscale if needed
            if len(face_img.shape) > 2 and face_img.shape[2] > 1:
                gray_img = cv2.cvtColor(face_img, cv2.COLOR_BGR2GRAY)
            else:
                gray_img = face_img
            
            # Resize to standard size
            resized_img = cv2.resize(gray_img, (self.face_width, self.face_height))
            
            return resized_img
        except Exception as e:
            self.logger.error(f"Error preprocessing face: {e}")
            return None
    
    def process_frame(self, frame):
        """
        Process a frame from the camera feed.
        
        Args:
            frame: Frame to process
            
        Returns:
            Frame with faces detected
        """
        try:
            # Create a copy of the frame
            result_frame = frame.copy()
            
            # Check if face detector is initialized
            if self.face_detector is None:
                self.logger.warning("Face detector not initialized.")
                return frame
            
            # Detect faces
            faces = self.face_detector.detect_faces(frame)
            
            # Update face detection status
            if len(faces) > 0:
                self.face_detected_var.set("Face detected: Yes")
                
                # Get the largest face
                largest_face = max(faces, key=lambda face: face[2] * face[3])
                x, y, w, h = largest_face
                
                # Draw rectangle around face
                cv2.rectangle(result_frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
                
                # Update preview if capturing
                if self.capture_active:
                    # Extract face
                    face_img = frame[y:y+h, x:x+w]
                    
                    # Check if it's time for a new capture
                    current_time = time.time()
                    if current_time - self.last_capture_time >= self.capture_delay:
                        self.capture_face(face_img)
                        self.last_capture_time = current_time
                    
                    # Update preview
                    try:
                        # Preprocess for preview
                        processed_face = self.preprocess_face(face_img)
                        
                        if processed_face is not None:
                            # Convert to RGB for tkinter
                            preview_rgb = cv2.cvtColor(processed_face, cv2.COLOR_GRAY2RGB)
                            
                            # Convert to PhotoImage
                            from PIL import Image, ImageTk
                            img = Image.fromarray(preview_rgb)
                            photo = ImageTk.PhotoImage(image=img)
                            
                            # Update canvas
                            self.preview_canvas.delete("all")
                            self.preview_canvas.create_image(0, 0, image=photo, anchor=tk.NW)
                            self.preview_canvas.photo = photo  # Keep a reference
                    except Exception as e:
                        self.logger.error(f"Error updating preview: {e}")
            else:
                self.face_detected_var.set("Face detected: No")
            
            return result_frame
        except Exception as e:
            self.logger.error(f"Error processing frame: {e}")
            return frame
    
    def start_capture(self):
        """Start capturing images for face registration."""
        # Get student ID
        student_id = self.id_var.get().strip()
        
        if not student_id:
            messagebox.showerror("Error", "Student ID is required")
            return
        
        if not self.db.student_exists(student_id):
            messagebox.showerror("Error", f"Student with ID {student_id} does not exist")
            return
        
        if not self.camera_feed.is_running():
            messagebox.showerror("Error", "Camera is not running")
            return
        
        # Reset capture variables
        self.capture_active = True
        self.capture_count = 0
        self.progress_var.set(0)
        self.student_id_for_capture = student_id
        self.last_capture_time = time.time()
        
        # Update UI
        self.status_var.set("Capturing images... Please move your face slightly to capture different angles")
        self.capture_count_var.set(f"Captures: {self.capture_count}/{self.total_captures}")
        self.capture_btn.config(state=tk.DISABLED)
        
        # Create directory for student images
        images_dir = self.config.get_path("FaceRecognition", "ImagesDirectory")
        student_dir = os.path.join(images_dir, student_id)
        os.makedirs(student_dir, exist_ok=True)
    
    def capture_face(self, face_img):
        """
        Capture a face image.
        
        Args:
            face_img: Face image to capture
        """
        try:
            # Check if we've reached the limit
            if self.capture_count >= self.total_captures:
                self.finish_capture()
                return
            
            # Preprocess the face image for consistent training
            processed_face = self.preprocess_face(face_img)
            
            if processed_face is None:
                self.logger.warning("Failed to preprocess face image")
                return
            
            # Get image directory
            images_dir = self.config.get_path("FaceRecognition", "ImagesDirectory")
            student_dir = os.path.join(images_dir, self.student_id_for_capture)
            
            # Save face image
            filename = os.path.join(student_dir, f"{self.capture_count}.jpg")
            cv2.imwrite(filename, processed_face)
            
            # Update count and progress
            self.capture_count += 1
            self.progress_var.set(int((self.capture_count / self.total_captures) * 100))
            self.capture_count_var.set(f"Captures: {self.capture_count}/{self.total_captures}")
            
            # Check if we've reached the limit
            if self.capture_count >= self.total_captures:
                self.finish_capture()
        except Exception as e:
            self.logger.error(f"Error capturing face: {e}")
    
    def finish_capture(self):
        """Finish the face capture process."""
        # Reset capture state
        self.capture_active = False
        
        # Update UI
        self.status_var.set("Image capture complete")
        self.capture_btn.config(state=tk.NORMAL)
        
        # Show message
        messagebox.showinfo("Success", "Image capture complete. You can now train the model.")
    
    def train_model(self):
        """Train the face recognition model."""
        if not self.face_recognizer or not self.face_recognizer.is_face_module_available():
            messagebox.showerror(
                "Error", 
                "Face recognition module not available.\n\n"
                "Please install opencv-contrib-python:\n"
                "1. pip uninstall opencv-python\n"
                "2. pip install opencv-contrib-python"
            )
            return
        
        # Start training thread
        self.training_thread = threading.Thread(target=self.train_model_thread)
        self.training_thread.daemon = True
        self.training_thread.start()
    
    def train_model_thread(self):
        """Train the face recognition model in a separate thread."""
        try:
            # Update status
            self.status_var.set("Training model...")
            self.progress_var.set(0)
            
            # Get image directory
            images_dir = self.config.get_path("FaceRecognition", "ImagesDirectory")
            
            # Check if directory exists
            if not os.path.exists(images_dir):
                messagebox.showerror("Error", "Images directory does not exist")
                self.status_var.set("Error training model")
                return
            
            # Create model trainer
            cascade_path = self.config.get_path("FaceRecognition", "CascadePath")
            model_trainer = ModelTrainer(cascade_path)
            
            # Define progress callback
            def progress_callback(progress, message):
                self.status_var.set(message)
                self.progress_var.set(int(progress))
            
            # Define completion callback
            def completion_callback(success):
                if success:
                    self.status_var.set("Model training complete")
                    messagebox.showinfo("Success", "Model training complete")
                else:
                    self.status_var.set("Error training model")
                    messagebox.showerror("Error", "Failed to train model")
            
            # Get model path
            model_path = self.config.get_path("FaceRecognition", "ModelPath")
            
            # Train the model
            model_trainer.train_async(images_dir, model_path, progress_callback, completion_callback)
        except Exception as e:
            self.logger.error(f"Error training model: {e}")
            messagebox.showerror("Error", f"Failed to train model: {e}")
            self.status_var.set("Error training model")
    
    def load_attendance(self):
        """Load attendance data."""
        # Get subject and date
        subject = self.subject_var.get().strip()
        date = self.date_var.get().strip()
        
        if not subject:
            messagebox.showerror("Error", "Subject is required")
            return
        
        # Clear treeview
        for item in self.attendance_tree.get_children():
            self.attendance_tree.delete(item)
        
        # Get attendance data
        attendance = self.db.get_attendance(subject, date)
        
        if attendance.empty:
            messagebox.showinfo("Info", "No attendance records found")
            return
        
        # Add data to treeview
        for _, row in attendance.iterrows():
            self.attendance_tree.insert("", "end", values=(
                row["ID"],
                row["Name"],
                row["Time"],
                row["Date"]
            ))
    
    def export_attendance(self):
        """Export attendance data to CSV."""
        # Get subject and date
        subject = self.subject_var.get().strip()
        date = self.date_var.get().strip()
        
        if not subject:
            messagebox.showerror("Error", "Subject is required")
            return
        
        # Get attendance data
        attendance = self.db.get_attendance(subject, date)
        
        if attendance.empty:
            messagebox.showinfo("Info", "No attendance records found")
            return
        
        # Ask for save location
        filename = f"attendance_{subject}_{date}.csv".replace(" ", "_")
        filepath = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv")],
            initialfile=filename
        )
        
        if not filepath:
            return
        
        # Export to CSV
        try:
            attendance.to_csv(filepath, index=False)
            messagebox.showinfo("Success", f"Attendance data exported to {filepath}")
        except Exception as e:
            self.logger.error(f"Error exporting attendance: {e}")
            messagebox.showerror("Error", f"Failed to export attendance: {e}")
    
    def generate_report(self):
        """Generate attendance report."""
        # Get report parameters
        subject = self.report_subject_var.get().strip()
        from_date = self.from_date_var.get().strip()
        to_date = self.to_date_var.get().strip()
        
        if not subject:
            messagebox.showerror("Error", "Subject is required")
            return
        
        # Clear treeview
        for item in self.report_tree.get_children():
            self.report_tree.delete(item)
        
        # Clear summary text
        self.summary_text.delete(1.0, tk.END)
        
        # Get attendance data
        attendance = self.db.get_attendance_range(subject, from_date, to_date)
        
        if attendance.empty:
            messagebox.showinfo("Info", "No attendance records found")
            return
        
        # Add data to treeview
        for _, row in attendance.iterrows():
            self.report_tree.insert("", "end", values=(
                row["ID"],
                row["Name"],
                row["Date"],
                row["Time"],
                subject
            ))
        
        # Generate summary
        total_students = len(attendance["ID"].unique())
        total_days = len(attendance["Date"].unique())
        
        summary = f"Attendance Summary for {subject}\n"
        summary += f"Period: {from_date} to {to_date}\n\n"
        summary += f"Total Students: {total_students}\n"
        summary += f"Total Days: {total_days}\n\n"
        
        # Calculate attendance percentage for each student
        student_attendance = {}
        for student_id in attendance["ID"].unique():
            student_name = attendance[attendance["ID"] == student_id]["Name"].iloc[0]
            student_days = len(attendance[attendance["ID"] == student_id]["Date"].unique())
            percentage = (student_days / total_days) * 100 if total_days > 0 else 0
            student_attendance[student_id] = (student_name, student_days, percentage)
        
        # Add student attendance to summary
        summary += "Student Attendance:\n"
        summary += "-" * 60 + "\n"
        summary += f"{'ID':<10} {'Name':<30} {'Days':<10} {'Percentage':<10}\n"
        summary += "-" * 60 + "\n"
        
        for student_id, (name, days, percentage) in student_attendance.items():
            summary += f"{student_id:<10} {name:<30} {days:<10} {percentage:.2f}%\n"
        
        # Add summary to text widget
        self.summary_text.insert(tk.END, summary)
    
    def export_report(self):
        """Export attendance report."""
        # Get report parameters
        subject = self.report_subject_var.get().strip()
        from_date = self.from_date_var.get().strip()
        to_date = self.to_date_var.get().strip()
        
        if not subject:
            messagebox.showerror("Error", "Subject is required")
            return
        
        # Get attendance data
        attendance = self.db.get_attendance_range(subject, from_date, to_date)
        
        if attendance.empty:
            messagebox.showinfo("Info", "No attendance records found")
            return
        
        # Ask for save location
        filename = f"report_{subject}_{from_date}_to_{to_date}.csv".replace(" ", "_")
        filepath = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv")],
            initialfile=filename
        )
        
        if not filepath:
            return
        
        # Export to CSV
        try:
            attendance.to_csv(filepath, index=False)
            messagebox.showinfo("Success", f"Report exported to {filepath}")
        except Exception as e:
            self.logger.error(f"Error exporting report: {e}")
            messagebox.showerror("Error", f"Failed to export report: {e}")
    
    def save_settings(self):
        """Save settings."""
        try:
            # Face recognition settings
            self.config.set_value("FaceRecognition", "MinFaceSize", self.min_face_var.get())
            self.config.set_value("FaceRecognition", "ScaleFactor", self.scale_var.get())
            self.config.set_value("FaceRecognition", "MinNeighbors", self.neighbors_var.get())
            self.config.set_value("FaceRecognition", "ConfidenceThreshold", self.confidence_var.get())
            
            # Alert settings
            self.config.set_value("AlertSystem", "AlertDuration", self.duration_var.get())
            self.config.set_value("AlertSystem", "AlertCooldown", self.cooldown_var.get())
            self.config.set_value("AlertSystem", "SoundEnabled", str(self.sound_var.get()))
            
            messagebox.showinfo("Success", "Settings saved successfully")
        except Exception as e:
            self.logger.error(f"Error saving settings: {e}")
            messagebox.showerror("Error", f"Failed to save settings: {e}")
    
    def reset_settings(self):
        """Reset settings to defaults."""
        try:
            # Load default configuration
            default_config = self.config._load_default_config()
            
            # Update variables
            self.min_face_var.set(default_config["FaceRecognition"]["MinFaceSize"])
            self.scale_var.set(default_config["FaceRecognition"]["ScaleFactor"])
            self.neighbors_var.set(default_config["FaceRecognition"]["MinNeighbors"])
            self.confidence_var.set(default_config["FaceRecognition"]["ConfidenceThreshold"])
            
            self.duration_var.set(default_config["AlertSystem"]["AlertDuration"])
            self.cooldown_var.set(default_config["AlertSystem"]["AlertCooldown"])
            self.sound_var.set(default_config["AlertSystem"]["SoundEnabled"].lower() == "true")
            
            messagebox.showinfo("Success", "Settings reset to defaults")
        except Exception as e:
            self.logger.error(f"Error resetting settings: {e}")
            messagebox.showerror("Error", f"Failed to reset settings: {e}")
    
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
        # Stop camera if running
        if hasattr(self, "camera_feed") and self.camera_feed.is_running():
            self.camera_feed.stop()
        
        # Destroy window
        self.root.destroy()

# For testing
if __name__ == "__main__":
    root = tk.Tk()
    app = AdminApp(root)
    root.mainloop()
