"""
Integration Test Script
This script performs integration testing of the Enhanced Attendance System.
"""

import os
import sys
import time
import tkinter as tk
import cv2
import numpy as np
import threading
import unittest
import tempfile
import shutil

# Add parent directory to path to import modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.face_recognition.face_detector import FaceDetector
from core.face_recognition.face_recognizer import FaceRecognizer
from core.face_recognition.model_trainer import ModelTrainer
from core.data_management.database import DatabaseManager
from core.data_management.config import ConfigManager
from core.data_management.attendance_logger import AttendanceLogger
from core.data_management.alert_system import AlertSystem
from utils.logger import Logger

class IntegrationTest:
    """
    Integration test for the Enhanced Attendance System.
    """
    
    def __init__(self):
        """Initialize the integration test."""
        self.logger = Logger(log_level=Logger.INFO)
        self.logger.info("Starting integration test")
        
        # Create temporary test directory
        self.test_dir = tempfile.mkdtemp()
        self.logger.info(f"Created temporary test directory: {self.test_dir}")
        
        # Initialize components
        self.config = ConfigManager()
        self.db = DatabaseManager()
        
        # Set up face recognition components
        cascade_path = self.config.get_path('FaceRecognition', 'CascadePath')
        model_path = self.config.get_path('FaceRecognition', 'ModelPath')
        
        self.face_detector = FaceDetector(cascade_path)
        self.face_recognizer = FaceRecognizer(model_path)
        self.model_trainer = ModelTrainer(cascade_path)
        
        # Set up attendance logger
        self.attendance_logger = AttendanceLogger(self.db, self.config)
        
        # Set up alert system
        self.alert_system = AlertSystem(self.config)
        
        # Test results
        self.test_results = {}
    
    def cleanup(self):
        """Clean up test environment."""
        # Remove temporary directory
        shutil.rmtree(self.test_dir)
        self.logger.info(f"Removed temporary test directory: {self.test_dir}")
    
    def test_student_registration_flow(self):
        """Test the student registration flow."""
        self.logger.info("Testing student registration flow")
        
        try:
            # Add a test student
            student_id = "12345"
            student_name = "Test Student"
            
            result = self.db.add_student(student_id, student_name)
            assert result, "Failed to add student to database"
            
            # Check if student exists
            assert self.db.student_exists(student_id), "Student does not exist after adding"
            
            # Get student name
            name = self.db.get_student_name(student_id)
            assert name == student_name, f"Expected student name '{student_name}', got '{name}'"
            
            self.test_results["student_registration"] = "PASS"
            self.logger.info("Student registration flow test passed")
        except AssertionError as e:
            self.test_results["student_registration"] = f"FAIL: {str(e)}"
            self.logger.error(f"Student registration flow test failed: {e}")
        except Exception as e:
            self.test_results["student_registration"] = f"ERROR: {str(e)}"
            self.logger.error(f"Error in student registration flow test: {e}")
    
    def test_attendance_marking_flow(self):
        """Test the attendance marking flow."""
        self.logger.info("Testing attendance marking flow")
        
        try:
            # Add a test student
            student_id = "12345"
            student_name = "Test Student"
            
            if not self.db.student_exists(student_id):
                self.db.add_student(student_id, student_name)
            
            # Set subject
            subject = "Test Subject"
            self.attendance_logger.set_subject(subject)
            
            # Mark attendance
            result = self.db.mark_attendance(student_id, subject)
            assert result, "Failed to mark attendance"
            
            # Get attendance records
            attendance = self.db.get_attendance(subject)
            assert not attendance.empty, "Attendance records are empty"
            assert len(attendance) >= 1, "Expected at least one attendance record"
            
            # Check if the student is in the attendance records
            student_records = attendance[attendance['ID'] == student_id]
            assert not student_records.empty, f"No attendance records found for student {student_id}"
            
            self.test_results["attendance_marking"] = "PASS"
            self.logger.info("Attendance marking flow test passed")
        except AssertionError as e:
            self.test_results["attendance_marking"] = f"FAIL: {str(e)}"
            self.logger.error(f"Attendance marking flow test failed: {e}")
        except Exception as e:
            self.test_results["attendance_marking"] = f"ERROR: {str(e)}"
            self.logger.error(f"Error in attendance marking flow test: {e}")
    
    def test_face_detection_flow(self):
        """Test the face detection flow."""
        self.logger.info("Testing face detection flow")
        
        try:
            # Create a test image with a face-like pattern
            test_image = np.zeros((300, 300, 3), dtype=np.uint8)
            cv2.rectangle(test_image, (100, 100), (200, 200), (255, 255, 255), -1)  # White square as a "face"
            
            # Detect faces
            faces = self.face_detector.detect_faces(test_image)
            
            # This is a basic test - in a real scenario with a real face image, we would expect faces to be detected
            assert isinstance(faces, np.ndarray), "detect_faces should return a numpy array"
            
            # Draw faces
            result_image, detected_faces = self.face_detector.detect_and_draw(test_image)
            assert isinstance(result_image, np.ndarray), "detect_and_draw should return a numpy array as the first element"
            assert isinstance(detected_faces, np.ndarray), "detect_and_draw should return a numpy array as the second element"
            
            self.test_results["face_detection"] = "PASS"
            self.logger.info("Face detection flow test passed")
        except AssertionError as e:
            self.test_results["face_detection"] = f"FAIL: {str(e)}"
            self.logger.error(f"Face detection flow test failed: {e}")
        except Exception as e:
            self.test_results["face_detection"] = f"ERROR: {str(e)}"
            self.logger.error(f"Error in face detection flow test: {e}")
    
    def test_alert_system_flow(self):
        """Test the alert system flow."""
        self.logger.info("Testing alert system flow")
        
        try:
            # Create a test image
            test_image = np.zeros((300, 300, 3), dtype=np.uint8)
            
            # Trigger an alert
            face_location = (100, 100, 100, 100)  # x, y, w, h
            self.alert_system.trigger_alert(test_image, face_location)
            
            # Check if alert is active
            assert self.alert_system.is_alert_active(), "Alert should be active after triggering"
            
            # Wait for alert to expire
            time.sleep(2)
            
            # Check if alert is still active
            alert_active = self.alert_system.is_alert_active()
            
            # Reset alert
            self.alert_system.reset_alert()
            
            # Check if alert is inactive after reset
            assert not self.alert_system.is_alert_active(), "Alert should be inactive after reset"
            
            self.test_results["alert_system"] = "PASS"
            self.logger.info("Alert system flow test passed")
        except AssertionError as e:
            self.test_results["alert_system"] = f"FAIL: {str(e)}"
            self.logger.error(f"Alert system flow test failed: {e}")
        except Exception as e:
            self.test_results["alert_system"] = f"ERROR: {str(e)}"
            self.logger.error(f"Error in alert system flow test: {e}")
    
    def run_all_tests(self):
        """Run all integration tests."""
        self.logger.info("Running all integration tests")
        
        # Run tests
        self.test_student_registration_flow()
        self.test_attendance_marking_flow()
        self.test_face_detection_flow()
        self.test_alert_system_flow()
        
        # Clean up
        self.cleanup()
        
        # Print results
        self.logger.info("Integration test results:")
        for test_name, result in self.test_results.items():
            self.logger.info(f"{test_name}: {result}")
        
        # Check if all tests passed
        all_passed = all(result == "PASS" for result in self.test_results.values())
        
        if all_passed:
            self.logger.info("All integration tests passed")
        else:
            self.logger.error("Some integration tests failed")
        
        return all_passed

def run_integration_tests():
    """Run integration tests."""
    test = IntegrationTest()
    return test.run_all_tests()

if __name__ == "__main__":
    run_integration_tests()
