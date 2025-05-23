"""
Model Trainer Module
This module provides functionality for training face recognition models.
"""

import os
import cv2
import numpy as np
import logging
import glob
from PIL import Image

class ModelTrainer:
    """
    A class for training face recognition models.
    """
    
    def __init__(self, face_recognizer, config=None):
        """
        Initialize the model trainer.
        
        Args:
            face_recognizer: Face recognizer instance
            config: Configuration manager instance (optional, will be required from face_recognizer if not provided)
        """
        self.face_recognizer = face_recognizer
        self.config = config
        self.logger = logging.getLogger("AttendanceSystem")
        
        # If config is not provided, try to get it from the face_recognizer
        if self.config is None:
            try:
                if hasattr(face_recognizer, 'config'):
                    self.config = face_recognizer.config
                    self.logger.info("Using config from face_recognizer")
                else:
                    from core.data_management.config import ConfigManager
                    self.config = ConfigManager()
                    self.logger.info("Created new ConfigManager instance")
            except Exception as e:
                self.logger.error(f"Error initializing config in ModelTrainer: {e}")
                raise ValueError("Config is required for ModelTrainer")
    
    def train_model(self, data_dir=None):
        """
        Train the face recognition model.
        
        Args:
            data_dir (str, optional): Directory containing face images. If None, uses default.
            
        Returns:
            tuple: (success, message) where success is a boolean and message is a status message
        """
        try:
            # Get data directory
            if data_dir is None:
                data_dir = self.config.get_path('FaceRecognition', 'DataDir')
            
            # Check if directory exists
            if not os.path.exists(data_dir):
                self.logger.error(f"Data directory not found: {data_dir}")
                return False, f"Data directory not found: {data_dir}"
            
            # Get all subdirectories (one per student)
            student_dirs = [d for d in os.listdir(data_dir) if os.path.isdir(os.path.join(data_dir, d))]
            
            if not student_dirs:
                self.logger.error("No student directories found")
                return False, "No student directories found. Please register students first."
            
            # Collect faces and IDs
            faces = []
            ids = []
            
            for student_dir in student_dirs:
                try:
                    # Get student ID from directory name
                    student_id = int(student_dir)
                    
                    # Get all image files
                    image_paths = []
                    for ext in ['jpg', 'jpeg', 'png']:
                        image_paths.extend(glob.glob(os.path.join(data_dir, student_dir, f'*.{ext}')))
                    
                    if not image_paths:
                        self.logger.warning(f"No images found for student {student_id}")
                        continue
                    
                    # Process each image
                    for image_path in image_paths:
                        try:
                            # Read image
                            img = cv2.imread(image_path)
                            
                            # Convert to grayscale
                            if img is None:
                                self.logger.warning(f"Failed to read image: {image_path}")
                                continue
                                
                            if len(img.shape) > 2:
                                gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
                            else:
                                gray = img
                            
                            # Resize to standard size
                            resized = cv2.resize(gray, (100, 100))
                            
                            # Add to training data
                            faces.append(resized)
                            ids.append(student_id)
                        except Exception as e:
                            self.logger.warning(f"Error processing image {image_path}: {e}")
                except Exception as e:
                    self.logger.warning(f"Error processing student directory {student_dir}: {e}")
            
            # Check if we have any faces
            if not faces:
                self.logger.error("No faces found in the directory")
                return False, "No faces found. Please capture face images for students first."
            
            # Convert to numpy arrays with consistent types
            faces_array = np.array(faces, dtype=np.uint8)
            ids_array = np.array(ids, dtype=np.int32)
            
            # Train the model
            success = self.face_recognizer.train(faces_array, ids_array)
            
            if success:
                self.logger.info(f"Model trained successfully with {len(faces)} images from {len(set(ids))} students")
                return True, f"Model trained successfully with {len(faces)} images from {len(set(ids))} students"
            else:
                self.logger.error("Failed to train model")
                return False, "Failed to train model. Please check the logs for details."
        except Exception as e:
            self.logger.error(f"Error training model: {e}")
            return False, f"Error training model: {e}"
    
    def validate_training_data(self, data_dir=None):
        """
        Validate training data.
        
        Args:
            data_dir (str, optional): Directory containing face images. If None, uses default.
            
        Returns:
            tuple: (valid, message, stats) where valid is a boolean, message is a status message,
                  and stats is a dictionary with statistics
        """
        try:
            # Get data directory
            if data_dir is None:
                data_dir = self.config.get_path('FaceRecognition', 'DataDir')
            
            # Check if directory exists
            if not os.path.exists(data_dir):
                return False, f"Data directory not found: {data_dir}", {}
            
            # Get all subdirectories (one per student)
            student_dirs = [d for d in os.listdir(data_dir) if os.path.isdir(os.path.join(data_dir, d))]
            
            if not student_dirs:
                return False, "No student directories found. Please register students first.", {}
            
            # Collect statistics
            stats = {
                "total_students": len(student_dirs),
                "total_images": 0,
                "valid_images": 0,
                "invalid_images": 0,
                "students_with_images": 0,
                "students_without_images": 0,
                "students": {}
            }
            
            for student_dir in student_dirs:
                try:
                    # Get student ID from directory name
                    student_id = student_dir
                    
                    # Get all image files
                    image_paths = []
                    for ext in ['jpg', 'jpeg', 'png']:
                        image_paths.extend(glob.glob(os.path.join(data_dir, student_dir, f'*.{ext}')))
                    
                    # Add student stats
                    stats["students"][student_id] = {
                        "total_images": len(image_paths),
                        "valid_images": 0,
                        "invalid_images": 0
                    }
                    
                    stats["total_images"] += len(image_paths)
                    
                    if not image_paths:
                        stats["students_without_images"] += 1
                        continue
                    
                    stats["students_with_images"] += 1
                    
                    # Process each image
                    for image_path in image_paths:
                        try:
                            # Read image
                            img = cv2.imread(image_path)
                            
                            if img is None:
                                stats["invalid_images"] += 1
                                stats["students"][student_id]["invalid_images"] += 1
                                continue
                            
                            # Image is valid
                            stats["valid_images"] += 1
                            stats["students"][student_id]["valid_images"] += 1
                        except Exception:
                            stats["invalid_images"] += 1
                            stats["students"][student_id]["invalid_images"] += 1
                except Exception:
                    # Skip invalid student directories
                    pass
            
            # Check if we have any valid images
            if stats["valid_images"] == 0:
                return False, "No valid face images found. Please capture face images for students first.", stats
            
            return True, f"Found {stats['valid_images']} valid images from {stats['students_with_images']} students", stats
        except Exception as e:
            self.logger.error(f"Error validating training data: {e}")
            return False, f"Error validating training data: {e}", {}
    
    def get_training_summary(self, data_dir=None):
        """
        Get a summary of training data.
        
        Args:
            data_dir (str, optional): Directory containing face images. If None, uses default.
            
        Returns:
            str: Summary text
        """
        valid, message, stats = self.validate_training_data(data_dir)
        
        if not valid:
            return message
        
        summary = f"Training Data Summary:\n\n"
        summary += f"Total students: {stats['total_students']}\n"
        summary += f"Students with images: {stats['students_with_images']}\n"
        summary += f"Students without images: {stats['students_without_images']}\n"
        summary += f"Total images: {stats['total_images']}\n"
        summary += f"Valid images: {stats['valid_images']}\n"
        summary += f"Invalid images: {stats['invalid_images']}\n\n"
        
        summary += "Student Details:\n"
        for student_id, student_stats in stats["students"].items():
            if student_stats["total_images"] > 0:
                summary += f"- Student {student_id}: {student_stats['valid_images']} valid images\n"
        
        return summary
