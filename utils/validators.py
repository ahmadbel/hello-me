"""
Validators Module
This module provides validation functions for user input.
"""

import re
import os

def validate_student_id(student_id):
    """
    Validate a student ID.
    
    Args:
        student_id (str): Student ID to validate
        
    Returns:
        bool: True if the ID is valid, False otherwise
    """
    # Check if the ID is not empty
    if not student_id:
        return False
    
    # Check if the ID contains only digits
    if not student_id.isdigit():
        return False
    
    # Check if the ID has a reasonable length (adjust as needed)
    if len(student_id) < 3 or len(student_id) > 10:
        return False
    
    return True

def validate_name(name):
    """
    Validate a name.
    
    Args:
        name (str): Name to validate
        
    Returns:
        bool: True if the name is valid, False otherwise
    """
    # Check if the name is not empty
    if not name:
        return False
    
    # Check if the name has a reasonable length
    if len(name) < 2 or len(name) > 50:
        return False
    
    # Check if the name contains only letters, spaces, and common name characters
    if not re.match(r'^[A-Za-z\s\'\-\.]+$', name):
        return False
    
    return True

def validate_subject(subject):
    """
    Validate a subject name.
    
    Args:
        subject (str): Subject name to validate
        
    Returns:
        bool: True if the subject name is valid, False otherwise
    """
    # Check if the subject is not empty
    if not subject:
        return False
    
    # Check if the subject has a reasonable length
    if len(subject) < 2 or len(subject) > 50:
        return False
    
    # Check if the subject contains only letters, numbers, spaces, and common characters
    if not re.match(r'^[A-Za-z0-9\s\'\-\.]+$', subject):
        return False
    
    return True

def validate_date(date_str):
    """
    Validate a date string in YYYY-MM-DD format.
    
    Args:
        date_str (str): Date string to validate
        
    Returns:
        bool: True if the date is valid, False otherwise
    """
    # Check if the date is not empty
    if not date_str:
        return False
    
    # Check if the date matches the YYYY-MM-DD format
    if not re.match(r'^\d{4}-\d{2}-\d{2}$', date_str):
        return False
    
    # Check if the date is valid
    try:
        import datetime
        year, month, day = map(int, date_str.split('-'))
        datetime.date(year, month, day)
        return True
    except ValueError:
        return False

def validate_file_path(file_path, must_exist=True, file_type=None):
    """
    Validate a file path.
    
    Args:
        file_path (str): File path to validate
        must_exist (bool): Whether the file must exist
        file_type (str, optional): Expected file extension (e.g., '.csv')
        
    Returns:
        bool: True if the file path is valid, False otherwise
    """
    # Check if the file path is not empty
    if not file_path:
        return False
    
    # Check if the file exists if required
    if must_exist and not os.path.exists(file_path):
        return False
    
    # Check if the file has the expected extension
    if file_type and not file_path.lower().endswith(file_type.lower()):
        return False
    
    return True

def validate_directory_path(dir_path, must_exist=True, create_if_missing=False):
    """
    Validate a directory path.
    
    Args:
        dir_path (str): Directory path to validate
        must_exist (bool): Whether the directory must exist
        create_if_missing (bool): Whether to create the directory if it doesn't exist
        
    Returns:
        bool: True if the directory path is valid, False otherwise
    """
    # Check if the directory path is not empty
    if not dir_path:
        return False
    
    # Check if the directory exists
    if os.path.exists(dir_path):
        # Check if it's a directory
        if not os.path.isdir(dir_path):
            return False
    else:
        # Directory doesn't exist
        if must_exist:
            # Create the directory if requested
            if create_if_missing:
                try:
                    os.makedirs(dir_path, exist_ok=True)
                except Exception:
                    return False
            else:
                return False
    
    return True

def validate_email(email):
    """
    Validate an email address.
    
    Args:
        email (str): Email address to validate
        
    Returns:
        bool: True if the email is valid, False otherwise
    """
    # Check if the email is not empty
    if not email:
        return False
    
    # Check if the email matches a basic email pattern
    if not re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', email):
        return False
    
    return True

def validate_phone(phone):
    """
    Validate a phone number.
    
    Args:
        phone (str): Phone number to validate
        
    Returns:
        bool: True if the phone number is valid, False otherwise
    """
    # Check if the phone number is not empty
    if not phone:
        return False
    
    # Remove common separators
    phone = re.sub(r'[\s\-\(\)\.]+', '', phone)
    
    # Check if the phone number contains only digits
    if not phone.isdigit():
        return False
    
    # Check if the phone number has a reasonable length
    if len(phone) < 7 or len(phone) > 15:
        return False
    
    return True

def sanitize_input(input_str):
    """
    Sanitize user input to prevent security issues.
    
    Args:
        input_str (str): Input string to sanitize
        
    Returns:
        str: Sanitized input string
    """
    if not input_str:
        return ""
    
    # Remove potentially dangerous characters
    sanitized = re.sub(r'[<>\'\"&;]', '', input_str)
    
    # Trim whitespace
    sanitized = sanitized.strip()
    
    return sanitized
