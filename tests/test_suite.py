"""
Test Suite for Enhanced Attendance System
This module provides comprehensive testing for the Enhanced Attendance System.
"""

import os
import sys
import unittest
import logging
import cv2
import numpy as np
import shutil
import tempfile

# Add parent directory to path
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.append(parent_dir)

# Import modules
from core.data_management.config import ConfigManager
from core.data_management.database import DatabaseManager
from core.face_recognition.face_detector import FaceDetector
from core.face_recognition.face_recognizer import FaceRecognizer
from core.face_recognition.model_trainer import ModelTrainer

class TestFaceRecognition(unittest.TestCase):
    """Test face recognition functionality."""
    
    def setUp(self):
        """Set up test environment."""
        # Create temporary directory for test data
        self.test_dir = tempfile.mkdtemp()
        
        # Create test configuration
        self.config = ConfigManager()
        
        # Create test cascade path
        cascade_path = self.config.get_path("FaceRecognition", "CascadePath")
        self.assertTrue(os.path.exists(cascade_path), f"Cascade file not found at {cascade_path}")
        
        # Create test model path
        self.model_path = os.path.join(self.test_dir, "test_model.yml")
        
        # Create test data directory
        self.data_dir = os.path.join(self.test_dir, "data")
        os.makedirs(self.data_dir, exist_ok=True)
        
        # Initialize face detector
        self.face_detector = FaceDetector(cascade_path)
        
        # Initialize face recognizer
        self.face_recognizer = FaceRecognizer(self.model_path, self.config)
    
    def tearDown(self):
        """Clean up test environment."""
        # Remove temporary directory
        shutil.rmtree(self.test_dir)
    
    def test_face_detector_initialization(self):
        """Test face detector initialization."""
        self.assertIsNotNone(self.face_detector, "Face detector should not be None")
        self.assertIsNotNone(self.face_detector.face_cascade, "Cascade classifier should not be None")
    
    def test_face_recognizer_initialization(self):
        """Test face recognizer initialization."""
        self.assertIsNotNone(self.face_recognizer, "Face recognizer should not be None")
        
        # Check if OpenCV face module is available
        if hasattr(cv2, 'face'):
            self.assertTrue(self.face_recognizer.is_face_module_available(), 
                           "Face module should be available")
        else:
            self.assertFalse(self.face_recognizer.is_face_module_available(), 
                            "Face module should not be available")
    
    def test_model_trainer_initialization(self):
        """Test model trainer initialization."""
        # Test with config
        trainer_with_config = ModelTrainer(self.face_recognizer, self.config)
        self.assertIsNotNone(trainer_with_config, "Model trainer with config should not be None")
        self.assertEqual(trainer_with_config.config, self.config, 
                        "Model trainer config should match provided config")
        
        # Test without config
        trainer_without_config = ModelTrainer(self.face_recognizer)
        self.assertIsNotNone(trainer_without_config, "Model trainer without config should not be None")
        self.assertIsNotNone(trainer_without_config.config, 
                            "Model trainer should create config if not provided")

class TestDatabaseManager(unittest.TestCase):
    """Test database manager functionality."""
    
    def setUp(self):
        """Set up test environment."""
        # Create temporary directory for test data
        self.test_dir = tempfile.mkdtemp()
        
        # Create test database path
        self.db_path = os.path.join(self.test_dir, "test.db")
        
        # Initialize database manager
        self.db = DatabaseManager(self.db_path)
    
    def tearDown(self):
        """Clean up test environment."""
        # Remove temporary directory
        shutil.rmtree(self.test_dir)
    
    def test_database_initialization(self):
        """Test database initialization."""
        self.assertIsNotNone(self.db, "Database manager should not be None")
        self.assertTrue(os.path.exists(self.db_path), "Database file should exist")
    
    def test_is_connected(self):
        """Test database connection check."""
        self.assertTrue(self.db.is_connected(), "Database should be connected")
    
    def test_student_operations(self):
        """Test student operations."""
        # Add student
        self.assertTrue(self.db.add_student("1001", "Test Student"), 
                       "Should successfully add student")
        
        # Get student name
        self.assertEqual(self.db.get_student_name("1001"), "Test Student", 
                        "Should retrieve correct student name")
        
        # Check if student exists
        self.assertTrue(self.db.student_exists("1001"), 
                       "Student should exist after adding")
        
        # Get all students
        students = self.db.get_all_students()
        self.assertEqual(len(students), 1, "Should have one student")
        # Convert ID to string for comparison to ensure consistent type
        self.assertEqual(str(students.iloc[0]["ID"]), "1001", "Student ID should match")
        self.assertEqual(students.iloc[0]["Name"], "Test Student", "Student name should match")

class TestConfigManager(unittest.TestCase):
    """Test configuration manager functionality."""
    
    def setUp(self):
        """Set up test environment."""
        # Create temporary directory for test data
        self.test_dir = tempfile.mkdtemp()
        
        # Create test configuration path
        self.config_path = os.path.join(self.test_dir, "test_config.json")
        
        # Initialize configuration manager
        self.config = ConfigManager(self.config_path)
    
    def tearDown(self):
        """Clean up test environment."""
        # Remove temporary directory
        shutil.rmtree(self.test_dir)
    
    def test_config_initialization(self):
        """Test configuration initialization."""
        self.assertIsNotNone(self.config, "Configuration manager should not be None")
        self.assertTrue(os.path.exists(self.config_path), "Configuration file should exist")
    
    def test_get_set_value(self):
        """Test getting and setting configuration values."""
        # Set value
        self.assertTrue(self.config.set_value("Test", "TestKey", "TestValue"), 
                       "Should successfully set value")
        
        # Get value
        self.assertEqual(self.config.get_value("Test", "TestKey"), "TestValue", 
                        "Should retrieve correct value")
        
        # Get value with default
        self.assertEqual(self.config.get_value("Test", "NonExistentKey", "DefaultValue"), 
                        "DefaultValue", "Should return default value for non-existent key")
    
    def test_get_path(self):
        """Test getting paths from configuration."""
        # Get cascade path
        cascade_path = self.config.get_path("FaceRecognition", "CascadePath")
        self.assertIsNotNone(cascade_path, "Cascade path should not be None")
        
        # Get model path
        model_path = self.config.get_path("FaceRecognition", "ModelPath")
        self.assertIsNotNone(model_path, "Model path should not be None")
        
        # Get data directory
        data_dir = self.config.get_path("FaceRecognition", "DataDir")
        self.assertIsNotNone(data_dir, "Data directory should not be None")

if __name__ == "__main__":
    # Configure logging
    logging.basicConfig(level=logging.ERROR)
    
    # Run tests
    unittest.main()
