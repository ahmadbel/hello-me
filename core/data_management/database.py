"""
Database Manager Module
This module provides functionality for managing student and attendance data.
"""

import os
import csv
import pandas as pd
import datetime
import json
from pathlib import Path

class DatabaseManager:
    """
    A class for managing student and attendance data with improved reliability.
    """
    
    def __init__(self, data_dir=None):
        """
        Initialize the database manager.
        
        Args:
            data_dir (str): Path to the data directory
        """
        if data_dir is None:
            # Use the default data directory
            current_dir = os.path.dirname(os.path.abspath(__file__))
            data_dir = os.path.join(current_dir, '..', '..', 'data')
        
        self.data_dir = data_dir
        self.students_dir = os.path.join(data_dir, 'students')
        self.attendance_dir = os.path.join(data_dir, 'attendance')
        
        # Create directories if they don't exist
        os.makedirs(self.students_dir, exist_ok=True)
        os.makedirs(self.attendance_dir, exist_ok=True)
        
        # Path to the student details file
        self.student_details_file = os.path.join(self.students_dir, 'student_details.csv')
        
        # Create student details file if it doesn't exist
        if not os.path.exists(self.student_details_file):
            with open(self.student_details_file, 'w', newline='') as f:
                writer = csv.writer(f)
                writer.writerow(['ID', 'Name', 'Registration_Date'])
        
        # Initialize connection status
        self._connected = self._check_connection()
    
    def _check_connection(self):
        """
        Check if the database is accessible.
        
        Returns:
            bool: True if database is accessible, False otherwise
        """
        try:
            # Check if data directories exist and are writable
            if not os.path.exists(self.data_dir):
                return False
            
            if not os.path.exists(self.students_dir) or not os.access(self.students_dir, os.W_OK):
                return False
                
            if not os.path.exists(self.attendance_dir) or not os.access(self.attendance_dir, os.W_OK):
                return False
            
            # Check if student details file is accessible
            if os.path.exists(self.student_details_file):
                # Try to read the file
                pd.read_csv(self.student_details_file)
            else:
                # Try to create the file
                with open(self.student_details_file, 'w', newline='') as f:
                    writer = csv.writer(f)
                    writer.writerow(['ID', 'Name', 'Registration_Date'])
            
            return True
        except Exception as e:
            print(f"Database connection check failed: {e}")
            return False
    
    def is_connected(self):
        """
        Check if the database is connected and accessible.
        
        Returns:
            bool: True if connected, False otherwise
        """
        # Refresh connection status
        self._connected = self._check_connection()
        return self._connected
    
    def add_student(self, student_id, name):
        """
        Add a new student to the database.
        
        Args:
            student_id (str): Student ID
            name (str): Student name
            
        Returns:
            bool: True if student was added successfully, False otherwise
        """
        try:
            # Check connection
            if not self.is_connected():
                print("Database is not connected")
                return False
                
            # Check if student already exists
            if self.student_exists(student_id):
                print(f"Student with ID {student_id} already exists")
                return False
            
            # Get current date
            registration_date = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            # Add student to the CSV file
            with open(self.student_details_file, 'a', newline='') as f:
                writer = csv.writer(f)
                writer.writerow([student_id, name, registration_date])
            
            return True
        except Exception as e:
            print(f"Error adding student: {e}")
            return False
    
    def student_exists(self, student_id):
        """
        Check if a student with the given ID exists.
        
        Args:
            student_id (str): Student ID to check
            
        Returns:
            bool: True if student exists, False otherwise
        """
        try:
            # Check connection
            if not self.is_connected():
                print("Database is not connected")
                return False
                
            # Read the student details file
            if not os.path.exists(self.student_details_file):
                return False
            
            df = pd.read_csv(self.student_details_file)
            
            # Check if the student ID exists
            return str(student_id) in df['ID'].astype(str).values
        except Exception as e:
            print(f"Error checking if student exists: {e}")
            return False
    
    def get_student_name(self, student_id):
        """
        Get the name of a student with the given ID.
        
        Args:
            student_id (str): Student ID
            
        Returns:
            str: Student name, or None if student doesn't exist
        """
        try:
            # Check connection
            if not self.is_connected():
                print("Database is not connected")
                return None
                
            # Read the student details file
            if not os.path.exists(self.student_details_file):
                return None
            
            df = pd.read_csv(self.student_details_file)
            
            # Find the student
            student = df[df['ID'].astype(str) == str(student_id)]
            
            if len(student) == 0:
                return None
            
            return student['Name'].values[0]
        except Exception as e:
            print(f"Error getting student name: {e}")
            return None
    
    def get_all_students(self):
        """
        Get a list of all students.
        
        Returns:
            pandas.DataFrame: DataFrame containing all student details
        """
        try:
            # Check connection
            if not self.is_connected():
                print("Database is not connected")
                return pd.DataFrame(columns=['ID', 'Name', 'Registration_Date'])
                
            # Read the student details file
            if not os.path.exists(self.student_details_file):
                return pd.DataFrame(columns=['ID', 'Name', 'Registration_Date'])
            
            return pd.read_csv(self.student_details_file)
        except Exception as e:
            print(f"Error getting all students: {e}")
            return pd.DataFrame(columns=['ID', 'Name', 'Registration_Date'])
    
    def mark_attendance(self, student_id, subject, status="Present"):
        """
        Mark attendance for a student.
        
        Args:
            student_id (str): Student ID
            subject (str): Subject name
            status (str): Attendance status (default: "Present")
            
        Returns:
            bool: True if attendance was marked successfully, False otherwise
        """
        try:
            # Check connection
            if not self.is_connected():
                print("Database is not connected")
                return False
                
            # Check if student exists
            if not self.student_exists(student_id):
                print(f"Student with ID {student_id} does not exist")
                return False
            
            # Get current date and time
            now = datetime.datetime.now()
            date = now.strftime("%Y-%m-%d")
            time = now.strftime("%H:%M:%S")
            
            # Create subject directory if it doesn't exist
            subject_dir = os.path.join(self.attendance_dir, subject)
            os.makedirs(subject_dir, exist_ok=True)
            
            # Path to the attendance file for today
            attendance_file = os.path.join(subject_dir, f"{date}.csv")
            
            # Create attendance file if it doesn't exist
            file_exists = os.path.exists(attendance_file)
            
            with open(attendance_file, 'a', newline='') as f:
                writer = csv.writer(f)
                
                # Write header if file doesn't exist
                if not file_exists:
                    writer.writerow(['ID', 'Name', 'Time', 'Status'])
                
                # Get student name
                name = self.get_student_name(student_id)
                
                # Write attendance record
                writer.writerow([student_id, name, time, status])
            
            return True
        except Exception as e:
            print(f"Error marking attendance: {e}")
            return False
    
    def get_attendance(self, subject, date=None):
        """
        Get attendance records for a subject on a specific date.
        
        Args:
            subject (str): Subject name
            date (str, optional): Date in YYYY-MM-DD format. If None, uses today's date.
            
        Returns:
            pandas.DataFrame: DataFrame containing attendance records
        """
        try:
            # Check connection
            if not self.is_connected():
                print("Database is not connected")
                return pd.DataFrame(columns=['ID', 'Name', 'Time', 'Status'])
                
            # Use today's date if not specified
            if date is None:
                date = datetime.datetime.now().strftime("%Y-%m-%d")
            
            # Path to the attendance file
            subject_dir = os.path.join(self.attendance_dir, subject)
            attendance_file = os.path.join(subject_dir, f"{date}.csv")
            
            # Check if the file exists
            if not os.path.exists(attendance_file):
                return pd.DataFrame(columns=['ID', 'Name', 'Time', 'Status'])
            
            # Read the attendance file
            return pd.read_csv(attendance_file)
        except Exception as e:
            print(f"Error getting attendance: {e}")
            return pd.DataFrame(columns=['ID', 'Name', 'Time', 'Status'])
    
    def get_attendance_range(self, subject, start_date=None, end_date=None):
        """
        Get attendance records for a subject over a date range.
        
        Args:
            subject (str): Subject name
            start_date (str, optional): Start date in YYYY-MM-DD format
            end_date (str, optional): End date in YYYY-MM-DD format
            
        Returns:
            pandas.DataFrame: DataFrame containing attendance records
        """
        try:
            # Check connection
            if not self.is_connected():
                print("Database is not connected")
                return pd.DataFrame(columns=['ID', 'Name', 'Date', 'Time', 'Status'])
                
            # Path to the subject directory
            subject_dir = os.path.join(self.attendance_dir, subject)
            
            # Check if the directory exists
            if not os.path.exists(subject_dir):
                return pd.DataFrame(columns=['ID', 'Name', 'Date', 'Time', 'Status'])
            
            # Get all attendance files
            attendance_files = [f for f in os.listdir(subject_dir) if f.endswith('.csv')]
            
            # Filter by date range if specified
            if start_date:
                attendance_files = [f for f in attendance_files if f.split('.')[0] >= start_date]
            if end_date:
                attendance_files = [f for f in attendance_files if f.split('.')[0] <= end_date]
            
            # Sort by date
            attendance_files.sort()
            
            # Initialize result DataFrame
            result = pd.DataFrame(columns=['ID', 'Name', 'Date', 'Time', 'Status'])
            
            # Process each attendance file
            for file in attendance_files:
                date = file.split('.')[0]
                file_path = os.path.join(subject_dir, file)
                
                # Read the attendance file
                try:
                    attendance = pd.read_csv(file_path)
                    
                    # Add date column
                    attendance['Date'] = date
                    
                    # Append to result
                    result = pd.concat([result, attendance])
                except Exception as e:
                    print(f"Error reading attendance file {file_path}: {e}")
                    continue
            
            return result
        except Exception as e:
            print(f"Error getting attendance range: {e}")
            return pd.DataFrame(columns=['ID', 'Name', 'Date', 'Time', 'Status'])
    
    def get_attendance_summary(self, subject, start_date=None, end_date=None):
        """
        Get a summary of attendance for a subject over a date range.
        
        Args:
            subject (str): Subject name
            start_date (str, optional): Start date in YYYY-MM-DD format
            end_date (str, optional): End date in YYYY-MM-DD format
            
        Returns:
            pandas.DataFrame: DataFrame containing attendance summary
        """
        try:
            # Check connection
            if not self.is_connected():
                print("Database is not connected")
                return pd.DataFrame()
                
            # Path to the subject directory
            subject_dir = os.path.join(self.attendance_dir, subject)
            
            # Check if the directory exists
            if not os.path.exists(subject_dir):
                return pd.DataFrame()
            
            # Get all attendance files
            attendance_files = [f for f in os.listdir(subject_dir) if f.endswith('.csv')]
            
            # Filter by date range if specified
            if start_date:
                attendance_files = [f for f in attendance_files if f.split('.')[0] >= start_date]
            if end_date:
                attendance_files = [f for f in attendance_files if f.split('.')[0] <= end_date]
            
            # Sort by date
            attendance_files.sort()
            
            # Initialize summary DataFrame
            all_students = self.get_all_students()
            summary = pd.DataFrame(index=all_students['ID'].astype(str))
            summary['Name'] = all_students['Name']
            
            # Process each attendance file
            for file in attendance_files:
                date = file.split('.')[0]
                file_path = os.path.join(subject_dir, file)
                
                # Read the attendance file
                attendance = pd.read_csv(file_path)
                
                # Create a pivot table for this date
                pivot = pd.pivot_table(
                    attendance, 
                    values='Status', 
                    index='ID', 
                    columns=None, 
                    aggfunc=lambda x: 'Present' if 'Present' in x.values else 'Absent'
                )
                
                # Add to summary
                summary[date] = 'Absent'
                for idx, row in pivot.iterrows():
                    if str(idx) in summary.index:
                        summary.at[str(idx), date] = row['Status']
            
            return summary
        except Exception as e:
            print(f"Error getting attendance summary: {e}")
            return pd.DataFrame()
    
    def export_attendance(self, subject, output_file, format='csv', start_date=None, end_date=None):
        """
        Export attendance records to a file.
        
        Args:
            subject (str): Subject name
            output_file (str): Path to the output file
            format (str): Output format ('csv' or 'json')
            start_date (str, optional): Start date in YYYY-MM-DD format
            end_date (str, optional): End date in YYYY-MM-DD format
            
        Returns:
            bool: True if export was successful, False otherwise
        """
        try:
            # Check connection
            if not self.is_connected():
                print("Database is not connected")
                return False
                
            # Get attendance summary
            summary = self.get_attendance_summary(subject, start_date, end_date)
            
            # Check if summary is empty
            if summary.empty:
                print(f"No attendance records found for subject {subject}")
                return False
            
            # Create directory if it doesn't exist
            os.makedirs(os.path.dirname(output_file), exist_ok=True)
            
            # Export in the specified format
            if format.lower() == 'csv':
                summary.to_csv(output_file)
            elif format.lower() == 'json':
                summary.to_json(output_file, orient='records')
            else:
                print(f"Unsupported format: {format}")
                return False
            
            return True
        except Exception as e:
            print(f"Error exporting attendance: {e}")
            return False
