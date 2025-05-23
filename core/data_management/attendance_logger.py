"""
Attendance Logger Module
This module provides functionality for logging and managing attendance records.
"""

import os
import csv
import pandas as pd
import datetime
import json
from pathlib import Path
import threading
import time

class AttendanceLogger:
    """
    A class for logging and managing attendance records with improved reliability.
    """
    
    def __init__(self, database_manager, config_manager):
        """
        Initialize the attendance logger.
        
        Args:
            database_manager: Database manager instance
            config_manager: Configuration manager instance
        """
        self.db = database_manager
        self.config = config_manager
        self.current_subject = None
        self.logging_active = False
        self.logging_thread = None
        self.attendance_buffer = []
        self.buffer_lock = threading.Lock()
    
    def set_subject(self, subject):
        """
        Set the current subject for attendance logging.
        
        Args:
            subject (str): Subject name
            
        Returns:
            bool: True if subject was set successfully, False otherwise
        """
        try:
            # Create subject directory if it doesn't exist
            attendance_dir = self.config.get_path('Database', 'AttendanceDirectory')
            subject_dir = os.path.join(attendance_dir, subject)
            os.makedirs(subject_dir, exist_ok=True)
            
            self.current_subject = subject
            return True
        except Exception as e:
            print(f"Error setting subject: {e}")
            return False
    
    def log_attendance(self, student_id, status="Present"):
        """
        Log attendance for a student.
        
        Args:
            student_id (str): Student ID
            status (str): Attendance status (default: "Present")
            
        Returns:
            bool: True if attendance was logged successfully, False otherwise
        """
        if not self.current_subject:
            print("Error: No subject set for attendance logging")
            return False
        
        return self.db.mark_attendance(student_id, self.current_subject, status)
    
    def log_attendance_batch(self, attendance_records):
        """
        Log attendance for multiple students at once.
        
        Args:
            attendance_records (list): List of (student_id, status) tuples
            
        Returns:
            int: Number of records successfully logged
        """
        if not self.current_subject:
            print("Error: No subject set for attendance logging")
            return 0
        
        success_count = 0
        for student_id, status in attendance_records:
            if self.db.mark_attendance(student_id, self.current_subject, status):
                success_count += 1
        
        return success_count
    
    def start_continuous_logging(self, callback=None):
        """
        Start continuous attendance logging in a separate thread.
        
        Args:
            callback (function, optional): Function to call when attendance is logged
            
        Returns:
            bool: True if logging was started successfully, False otherwise
        """
        if self.logging_active:
            print("Continuous logging is already active")
            return False
        
        if not self.current_subject:
            print("Error: No subject set for attendance logging")
            return False
        
        def logging_thread():
            self.logging_active = True
            print(f"Started continuous attendance logging for {self.current_subject}")
            
            while self.logging_active:
                # Process any records in the buffer
                with self.buffer_lock:
                    records_to_process = self.attendance_buffer.copy()
                    self.attendance_buffer = []
                
                if records_to_process:
                    success_count = self.log_attendance_batch(records_to_process)
                    
                    if callback:
                        callback(success_count, len(records_to_process))
                
                # Sleep for a short time
                time.sleep(1)
        
        self.logging_thread = threading.Thread(target=logging_thread)
        self.logging_thread.daemon = True
        self.logging_thread.start()
        
        return True
    
    def stop_continuous_logging(self):
        """
        Stop continuous attendance logging.
        
        Returns:
            bool: True if logging was stopped successfully, False otherwise
        """
        if not self.logging_active:
            print("Continuous logging is not active")
            return False
        
        self.logging_active = False
        
        if self.logging_thread:
            self.logging_thread.join(timeout=5)
            self.logging_thread = None
        
        return True
    
    def add_to_buffer(self, student_id, status="Present"):
        """
        Add an attendance record to the buffer for continuous logging.
        
        Args:
            student_id (str): Student ID
            status (str): Attendance status (default: "Present")
            
        Returns:
            bool: True if record was added to buffer successfully, False otherwise
        """
        try:
            with self.buffer_lock:
                self.attendance_buffer.append((student_id, status))
            return True
        except Exception as e:
            print(f"Error adding to attendance buffer: {e}")
            return False
    
    def get_attendance_report(self, date=None):
        """
        Get an attendance report for the current subject on a specific date.
        
        Args:
            date (str, optional): Date in YYYY-MM-DD format. If None, uses today's date.
            
        Returns:
            pandas.DataFrame: DataFrame containing attendance records
        """
        if not self.current_subject:
            print("Error: No subject set for attendance reporting")
            return pd.DataFrame()
        
        return self.db.get_attendance(self.current_subject, date)
    
    def get_attendance_summary(self, start_date=None, end_date=None):
        """
        Get an attendance summary for the current subject over a date range.
        
        Args:
            start_date (str, optional): Start date in YYYY-MM-DD format
            end_date (str, optional): End date in YYYY-MM-DD format
            
        Returns:
            pandas.DataFrame: DataFrame containing attendance summary
        """
        if not self.current_subject:
            print("Error: No subject set for attendance reporting")
            return pd.DataFrame()
        
        return self.db.get_attendance_summary(self.current_subject, start_date, end_date)
    
    def export_attendance_report(self, output_file, format='csv', start_date=None, end_date=None):
        """
        Export an attendance report for the current subject.
        
        Args:
            output_file (str): Path to the output file
            format (str): Output format ('csv' or 'json')
            start_date (str, optional): Start date in YYYY-MM-DD format
            end_date (str, optional): End date in YYYY-MM-DD format
            
        Returns:
            bool: True if export was successful, False otherwise
        """
        if not self.current_subject:
            print("Error: No subject set for attendance reporting")
            return False
        
        return self.db.export_attendance(self.current_subject, output_file, format, start_date, end_date)
