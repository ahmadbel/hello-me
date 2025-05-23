"""
Configuration Manager Module
This module provides configuration management for the Enhanced Attendance System.
"""

import os
import json
import logging

class ConfigManager:
    """
    A class for managing configuration settings.
    """
    
    def __init__(self, config_file=None):
        """
        Initialize the configuration manager.
        
        Args:
            config_file (str, optional): Path to configuration file. If None, uses default.
        """
        self.logger = logging.getLogger("AttendanceSystem")
        
        # Set default config file path
        if config_file is None:
            # Get the directory of this file
            current_dir = os.path.dirname(os.path.abspath(__file__))
            parent_dir = os.path.dirname(os.path.dirname(current_dir))
            self.config_file = os.path.join(parent_dir, "config.json")
        else:
            self.config_file = config_file
        
        # Load configuration
        self.config = self._load_config()
    
    def ensure_directories_exist(self):
        """
        Ensure all required directories exist.
        Creates directories if they don't exist.
        """
        # Get the base directory
        current_dir = os.path.dirname(os.path.abspath(__file__))
        parent_dir = os.path.dirname(os.path.dirname(current_dir))
        
        # Define required directories
        required_dirs = [
            os.path.join(parent_dir, "data"),
            os.path.join(parent_dir, "data", "images"),
            os.path.join(parent_dir, "data", "models"),
            os.path.join(parent_dir, "data", "attendance"),
            os.path.join(parent_dir, "data", "students"),
            os.path.join(parent_dir, "data", "haarcascades"),
            os.path.join(parent_dir, "reports")
        ]
        
        # Create directories if they don't exist
        for directory in required_dirs:
            try:
                if not os.path.exists(directory):
                    os.makedirs(directory, exist_ok=True)
                    self.logger.info(f"Created directory: {directory}")
            except Exception as e:
                self.logger.error(f"Error creating directory {directory}: {e}")
    
    def _load_default_config(self):
        """
        Load default configuration.
        
        Returns:
            dict: Default configuration
        """
        return {
            "General": {
                "Theme": "light",
                "DefaultSubject": "General",
                "ApplicationName": "Enhanced Attendance System",
                "Version": "1.0.0"
            },
            "FaceRecognition": {
                "CascadePath": self._get_default_cascade_path(),
                "ModelPath": self._get_default_model_path(),
                "DataDir": self._get_default_data_dir(),
                "MinFaceSize": "30",
                "ScaleFactor": "1.1",
                "MinNeighbors": "5",
                "ConfidenceThreshold": "80"
            },
            "AlertSystem": {
                "AlertDuration": "5",
                "AlertCooldown": "10",
                "SoundEnabled": "True"
            },
            "UI": {
                "AdminTitle": "Admin Interface - Enhanced Attendance System",
                "ScannerTitle": "Scanner Interface - Enhanced Attendance System"
            }
        }
    
    def _get_default_cascade_path(self):
        """
        Get default cascade path.
        
        Returns:
            str: Default cascade path
        """
        # Get the directory of this file
        current_dir = os.path.dirname(os.path.abspath(__file__))
        parent_dir = os.path.dirname(os.path.dirname(current_dir))
        
        # Check multiple possible locations
        possible_paths = [
            os.path.join(parent_dir, "data", "haarcascades", "haarcascade_frontalface_default.xml"),
            os.path.join(parent_dir, "haarcascade_frontalface_default.xml"),
            os.path.join(os.path.dirname(os.path.abspath(__file__)), "haarcascade_frontalface_default.xml")
        ]
        
        # Try to find OpenCV's built-in cascade file
        try:
            import cv2
            opencv_path = os.path.join(os.path.dirname(cv2.__file__), 'data', 'haarcascade_frontalface_default.xml')
            possible_paths.append(opencv_path)
        except:
            pass
        
        # Return the first path that exists
        for path in possible_paths:
            if os.path.exists(path):
                return path
        
        # If no path exists, return the first one and log a warning
        self.logger.warning(f"Default cascade file not found. Using {possible_paths[0]}")
        return possible_paths[0]
    
    def _get_default_model_path(self):
        """
        Get default model path.
        
        Returns:
            str: Default model path
        """
        # Get the directory of this file
        current_dir = os.path.dirname(os.path.abspath(__file__))
        parent_dir = os.path.dirname(os.path.dirname(current_dir))
        
        return os.path.join(parent_dir, "data", "models", "face_recognition_model.yml")
    
    def _get_default_data_dir(self):
        """
        Get default data directory.
        
        Returns:
            str: Default data directory
        """
        # Get the directory of this file
        current_dir = os.path.dirname(os.path.abspath(__file__))
        parent_dir = os.path.dirname(os.path.dirname(current_dir))
        
        return os.path.join(parent_dir, "data", "images")
    
    def _load_config(self):
        """
        Load configuration from file.
        
        Returns:
            dict: Configuration
        """
        # Check if config file exists
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, "r") as f:
                    config = json.load(f)
                
                # Merge with default config to ensure all keys exist
                default_config = self._load_default_config()
                self._merge_configs(default_config, config)
                
                return default_config
            except Exception as e:
                self.logger.error(f"Error loading configuration: {e}")
                return self._load_default_config()
        else:
            # Create default config
            config = self._load_default_config()
            
            try:
                # Create directory if it doesn't exist
                os.makedirs(os.path.dirname(self.config_file), exist_ok=True)
                
                # Save default config
                with open(self.config_file, "w") as f:
                    json.dump(config, f, indent=4)
            except Exception as e:
                self.logger.error(f"Error saving default configuration: {e}")
            
            return config
    
    def _merge_configs(self, target, source):
        """
        Merge source config into target config.
        
        Args:
            target (dict): Target configuration
            source (dict): Source configuration
        """
        for key, value in source.items():
            if key in target and isinstance(target[key], dict) and isinstance(value, dict):
                self._merge_configs(target[key], value)
            else:
                target[key] = value
    
    def save_config(self):
        """
        Save configuration to file.
        
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            # Create directory if it doesn't exist
            os.makedirs(os.path.dirname(self.config_file), exist_ok=True)
            
            # Save config
            with open(self.config_file, "w") as f:
                json.dump(self.config, f, indent=4)
            
            return True
        except Exception as e:
            self.logger.error(f"Error saving configuration: {e}")
            return False
    
    def get_value(self, section, key, default=None):
        """
        Get configuration value.
        
        Args:
            section (str): Configuration section
            key (str): Configuration key
            default (str, optional): Default value if not found
            
        Returns:
            str: Configuration value
        """
        try:
            return self.config[section][key]
        except KeyError:
            if default is not None:
                return default
            
            # If no default provided, add the key with empty value
            if section not in self.config:
                self.config[section] = {}
            
            self.config[section][key] = ""
            return ""
    
    def set_value(self, section, key, value):
        """
        Set configuration value.
        
        Args:
            section (str): Configuration section
            key (str): Configuration key
            value (str): Configuration value
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            # Create section if it doesn't exist
            if section not in self.config:
                self.config[section] = {}
            
            # Set value
            self.config[section][key] = value
            
            # Save config
            return self.save_config()
        except Exception as e:
            self.logger.error(f"Error setting configuration value: {e}")
            return False
    
    def get_path(self, section, key):
        """
        Get path from configuration.
        
        Args:
            section (str): Configuration section
            key (str): Configuration key
            
        Returns:
            str: Path
        """
        path = self.get_value(section, key)
        
        # If path is empty or doesn't exist, use default
        if not path or not os.path.exists(path):
            # Get default path based on key
            if key == "CascadePath":
                path = self._get_default_cascade_path()
            elif key == "ModelPath":
                path = self._get_default_model_path()
            elif key == "DataDir":
                path = self._get_default_data_dir()
            
            # Update config with default path
            self.set_value(section, key, path)
        
        return path
