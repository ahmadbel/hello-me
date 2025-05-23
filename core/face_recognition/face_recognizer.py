"""
Face Recognizer Module
This module provides face recognition functionality.
"""

import os
import cv2
import numpy as np
import logging

class FaceRecognizer:
    """
    A class for face recognition.
    """
    
    def __init__(self, model_path, config=None):
        """
        Initialize the face recognizer.
        
        Args:
            model_path (str): Path to the face recognition model
            config (ConfigManager, optional): Configuration manager instance
        """
        self.model_path = model_path
        self.config = config
        self.logger = logging.getLogger("AttendanceSystem")
        self.recognizer = None
        self.face_module_available = False
        self.model_loaded = False
        
        # Try to initialize face recognizer
        try:
            # Check if OpenCV face module is available
            if hasattr(cv2, 'face'):
                self.recognizer = cv2.face.LBPHFaceRecognizer_create()
                self.face_module_available = True
                
                # Try to load model if it exists
                if os.path.exists(model_path):
                    try:
                        self.recognizer.read(model_path)
                        self.model_loaded = True
                        self.logger.info(f"Face recognition model loaded from {model_path}")
                    except Exception as e:
                        self.logger.warning(f"Failed to load face recognition model: {e}")
                else:
                    self.logger.warning(f"Face recognition model not found at {model_path}")
            else:
                self.logger.warning("OpenCV face module not available. Face recognition will not work.")
        except Exception as e:
            self.logger.error(f"Error initializing face recognizer: {e}")
    
    def is_face_module_available(self):
        """
        Check if OpenCV face module is available.
        
        Returns:
            bool: True if available, False otherwise
        """
        return self.face_module_available
    
    def is_model_loaded(self):
        """
        Check if face recognition model is loaded.
        
        Returns:
            bool: True if loaded, False otherwise
        """
        return self.model_loaded
    
    def train(self, faces, ids):
        """
        Train the face recognition model.
        
        Args:
            faces (list): List of face images
            ids (list): List of corresponding IDs
            
        Returns:
            bool: True if successful, False otherwise
        """
        if not self.face_module_available:
            self.logger.error("OpenCV face module not available. Cannot train model.")
            return False
        
        try:
            # Ensure faces and ids are numpy arrays with correct types
            faces_array = np.array(faces, dtype=np.uint8)
            ids_array = np.array(ids, dtype=np.int32)
            
            # Train the model
            self.recognizer.train(faces_array, ids_array)
            
            # Save the model
            directory = os.path.dirname(self.model_path)
            if not os.path.exists(directory):
                os.makedirs(directory)
                
            self.recognizer.write(self.model_path)
            self.model_loaded = True
            
            self.logger.info(f"Face recognition model trained and saved to {self.model_path}")
            return True
        except Exception as e:
            self.logger.error(f"Error training face recognition model: {e}")
            return False
    
    def recognize_face(self, face_img):
        """
        Recognize a face.
        
        Args:
            face_img (numpy.ndarray): Face image
            
        Returns:
            tuple: (id, confidence) where id is the recognized ID and confidence is the recognition confidence
        """
        if not self.face_module_available:
            self.logger.warning("OpenCV face module not available. Cannot recognize face.")
            return -1, 100
        
        if not self.model_loaded:
            self.logger.warning("Face recognition model not loaded. Cannot recognize face.")
            return -1, 100
        
        try:
            # Convert to grayscale if needed
            if len(face_img.shape) > 2:
                gray = cv2.cvtColor(face_img, cv2.COLOR_BGR2GRAY)
            else:
                gray = face_img
            
            # Resize to standard size (100x100)
            resized = cv2.resize(gray, (100, 100))
            
            # Recognize face
            id, confidence = self.recognizer.predict(resized)
            
            return id, confidence
        except Exception as e:
            self.logger.error(f"Error recognizing face: {e}")
            return -1, 100
