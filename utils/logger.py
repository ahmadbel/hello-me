"""
Logger Module
This module provides logging functionality for the application.
"""

import os
import logging
import datetime
import sys
from pathlib import Path

class Logger:
    """
    A class for managing application logging with improved flexibility.
    """
    
    # Log levels
    DEBUG = logging.DEBUG
    INFO = logging.INFO
    WARNING = logging.WARNING
    ERROR = logging.ERROR
    CRITICAL = logging.CRITICAL
    
    def __init__(self, log_dir=None, log_level=logging.INFO):
        """
        Initialize the logger.
        
        Args:
            log_dir (str): Directory for log files
            log_level: Logging level
        """
        if log_dir is None:
            # Use the default log directory
            current_dir = os.path.dirname(os.path.abspath(__file__))
            log_dir = os.path.join(current_dir, '..', 'logs')
        
        # Create log directory if it doesn't exist
        os.makedirs(log_dir, exist_ok=True)
        
        self.log_dir = log_dir
        self.log_level = log_level
        
        # Generate log filename with timestamp
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        self.log_file = os.path.join(log_dir, f"app_{timestamp}.log")
        
        # Configure logging
        self._configure_logging()
    
    def _configure_logging(self):
        """Configure the logging system."""
        # Create logger
        self.logger = logging.getLogger('AttendanceSystem')
        self.logger.setLevel(self.log_level)
        
        # Create file handler
        file_handler = logging.FileHandler(self.log_file)
        file_handler.setLevel(self.log_level)
        
        # Create console handler
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(self.log_level)
        
        # Create formatter
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        file_handler.setFormatter(formatter)
        console_handler.setFormatter(formatter)
        
        # Add handlers to logger
        self.logger.addHandler(file_handler)
        self.logger.addHandler(console_handler)
    
    def debug(self, message):
        """
        Log a debug message.
        
        Args:
            message (str): Message to log
        """
        self.logger.debug(message)
    
    def info(self, message):
        """
        Log an info message.
        
        Args:
            message (str): Message to log
        """
        self.logger.info(message)
    
    def warning(self, message):
        """
        Log a warning message.
        
        Args:
            message (str): Message to log
        """
        self.logger.warning(message)
    
    def error(self, message):
        """
        Log an error message.
        
        Args:
            message (str): Message to log
        """
        self.logger.error(message)
    
    def critical(self, message):
        """
        Log a critical message.
        
        Args:
            message (str): Message to log
        """
        self.logger.critical(message)
    
    def log(self, level, message):
        """
        Log a message with the specified level.
        
        Args:
            level: Logging level
            message (str): Message to log
        """
        self.logger.log(level, message)
    
    def get_log_file(self):
        """
        Get the path to the current log file.
        
        Returns:
            str: Path to the log file
        """
        return self.log_file
    
    def set_level(self, level):
        """
        Set the logging level.
        
        Args:
            level: New logging level
        """
        self.log_level = level
        self.logger.setLevel(level)
        
        for handler in self.logger.handlers:
            handler.setLevel(level)
    
    def get_level(self):
        """
        Get the current logging level.
        
        Returns:
            int: Current logging level
        """
        return self.log_level
