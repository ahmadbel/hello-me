"""
Face Detector Module
This module provides functionality for detecting faces in images.
"""

import os
import cv2
import numpy as np

class FaceDetector:
    """
    A class for detecting faces in images using Haar cascades.
    """
    
    def __init__(self, cascade_path):
        """
        Initialize the face detector.
        
        Args:
            cascade_path (str): Path to the Haar cascade XML file
        """
        # Normalize path for the current OS
        self.cascade_path = os.path.normpath(cascade_path)
        
        # Check if cascade file exists
        if not os.path.exists(self.cascade_path):
            # Try to find the file in standard locations
            base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
            alternative_paths = [
                os.path.join(base_dir, 'data', 'haarcascades', 'haarcascade_frontalface_default.xml'),
                os.path.join(base_dir, 'data', 'haarcascade_frontalface_default.xml'),
                os.path.join(os.path.dirname(cv2.__file__), 'data', 'haarcascade_frontalface_default.xml')
            ]
            
            for path in alternative_paths:
                if os.path.exists(path):
                    self.cascade_path = path
                    break
            else:
                raise ValueError(f"Error: Could not find cascade classifier file. Tried: {self.cascade_path} and standard locations")
        
        # Load the cascade classifier
        self.face_cascade = cv2.CascadeClassifier(self.cascade_path)
        
        # Check if cascade loaded successfully
        if self.face_cascade.empty():
            raise ValueError(f"Error: Could not load cascade classifier from {self.cascade_path}")
        
        # Default parameters
        self.min_face_size = (30, 30)
        self.scale_factor = 1.1
        self.min_neighbors = 5
    
    def set_parameters(self, min_face_size=(30, 30), scale_factor=1.1, min_neighbors=5):
        """
        Set face detection parameters.
        
        Args:
            min_face_size (tuple): Minimum face size (width, height)
            scale_factor (float): Scale factor for detection
            min_neighbors (int): Minimum number of neighbors
        """
        self.min_face_size = min_face_size
        self.scale_factor = scale_factor
        self.min_neighbors = min_neighbors
    
    def detect_faces(self, image):
        """
        Detect faces in an image.
        
        Args:
            image: Input image
            
        Returns:
            numpy.ndarray: Array of face rectangles (x, y, w, h)
        """
        # Convert to grayscale if needed
        if len(image.shape) == 3:
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        else:
            gray = image
        
        # Detect faces
        faces = self.face_cascade.detectMultiScale(
            gray,
            scaleFactor=self.scale_factor,
            minNeighbors=self.min_neighbors,
            minSize=self.min_face_size,
            flags=cv2.CASCADE_SCALE_IMAGE
        )
        
        return faces
    
    def detect_and_draw(self, image, color=(0, 255, 0), thickness=2):
        """
        Detect faces in an image and draw rectangles around them.
        
        Args:
            image: Input image
            color (tuple): Rectangle color (B, G, R)
            thickness (int): Rectangle line thickness
            
        Returns:
            tuple: (image with rectangles, detected faces)
        """
        # Create a copy of the image
        result_image = image.copy()
        
        # Detect faces
        faces = self.detect_faces(image)
        
        # Draw rectangles around faces
        for (x, y, w, h) in faces:
            cv2.rectangle(result_image, (x, y), (x + w, y + h), color, thickness)
        
        return result_image, faces
    
    def extract_faces(self, image, padding=0):
        """
        Extract face regions from an image.
        
        Args:
            image: Input image
            padding (int): Padding around faces
            
        Returns:
            list: List of face images
        """
        # Detect faces
        faces = self.detect_faces(image)
        
        # Extract face regions
        face_images = []
        for (x, y, w, h) in faces:
            # Apply padding
            x1 = max(0, x - padding)
            y1 = max(0, y - padding)
            x2 = min(image.shape[1], x + w + padding)
            y2 = min(image.shape[0], y + h + padding)
            
            # Extract face region
            face_image = image[y1:y2, x1:x2]
            face_images.append(face_image)
        
        return face_images
    
    def get_largest_face(self, image):
        """
        Get the largest face in an image.
        
        Args:
            image: Input image
            
        Returns:
            tuple: (x, y, w, h) of the largest face, or None if no face is detected
        """
        # Detect faces
        faces = self.detect_faces(image)
        
        if len(faces) == 0:
            return None
        
        # Find the largest face
        largest_face = max(faces, key=lambda face: face[2] * face[3])
        
        return largest_face
