"""
Performance Test Script
This script tests the performance of the Enhanced Attendance System on the target hardware.
"""

import os
import sys
import time
import psutil
import cv2
import numpy as np
import threading
import platform
import matplotlib.pyplot as plt

# Add parent directory to path to import modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.face_recognition.face_detector import FaceDetector
from core.face_recognition.face_recognizer import FaceRecognizer
from core.data_management.database import DatabaseManager
from core.data_management.config import ConfigManager
from utils.logger import Logger

class PerformanceTest:
    """
    Performance test for the Enhanced Attendance System.
    """
    
    def __init__(self):
        """Initialize the performance test."""
        self.logger = Logger(log_level=Logger.INFO)
        self.logger.info("Starting performance test")
        
        # Initialize components
        self.config = ConfigManager()
        self.db = DatabaseManager()
        
        # Set up face recognition components
        cascade_path = self.config.get_path('FaceRecognition', 'CascadePath')
        model_path = self.config.get_path('FaceRecognition', 'ModelPath')
        
        self.face_detector = FaceDetector(cascade_path)
        self.face_recognizer = FaceRecognizer(model_path)
        
        # Performance metrics
        self.metrics = {
            "face_detection_times": [],
            "face_recognition_times": [],
            "database_operation_times": [],
            "cpu_usage": [],
            "memory_usage": []
        }
        
        # System info
        self.system_info = self.get_system_info()
        self.logger.info(f"System information: {self.system_info}")
    
    def get_system_info(self):
        """Get system information."""
        info = {
            "platform": platform.platform(),
            "processor": platform.processor(),
            "python_version": platform.python_version(),
            "cpu_count": psutil.cpu_count(logical=True),
            "physical_cpu_count": psutil.cpu_count(logical=False),
            "total_memory": f"{psutil.virtual_memory().total / (1024 ** 3):.2f} GB"
        }
        return info
    
    def test_face_detection_performance(self, num_iterations=100):
        """
        Test face detection performance.
        
        Args:
            num_iterations (int): Number of test iterations
        """
        self.logger.info(f"Testing face detection performance with {num_iterations} iterations")
        
        # Create a test image with a face-like pattern
        test_image = np.zeros((300, 300, 3), dtype=np.uint8)
        cv2.rectangle(test_image, (100, 100), (200, 200), (255, 255, 255), -1)  # White square as a "face"
        
        # Run test iterations
        for i in range(num_iterations):
            # Monitor CPU and memory
            self.metrics["cpu_usage"].append(psutil.cpu_percent())
            self.metrics["memory_usage"].append(psutil.virtual_memory().percent)
            
            # Measure face detection time
            start_time = time.time()
            self.face_detector.detect_faces(test_image)
            end_time = time.time()
            
            # Record time
            detection_time = (end_time - start_time) * 1000  # Convert to milliseconds
            self.metrics["face_detection_times"].append(detection_time)
            
            # Log progress
            if (i + 1) % 10 == 0:
                self.logger.info(f"Completed {i + 1}/{num_iterations} face detection iterations")
        
        # Calculate statistics
        avg_time = sum(self.metrics["face_detection_times"]) / len(self.metrics["face_detection_times"])
        max_time = max(self.metrics["face_detection_times"])
        min_time = min(self.metrics["face_detection_times"])
        
        self.logger.info(f"Face detection performance: Avg={avg_time:.2f}ms, Min={min_time:.2f}ms, Max={max_time:.2f}ms")
    
    def test_face_recognition_performance(self, num_iterations=50):
        """
        Test face recognition performance.
        
        Args:
            num_iterations (int): Number of test iterations
        """
        self.logger.info(f"Testing face recognition performance with {num_iterations} iterations")
        
        # Create a test face image
        face_img = np.zeros((100, 100, 3), dtype=np.uint8)
        cv2.rectangle(face_img, (30, 30), (70, 70), (255, 255, 255), -1)  # White square as a "face feature"
        
        # Run test iterations
        for i in range(num_iterations):
            # Monitor CPU and memory
            self.metrics["cpu_usage"].append(psutil.cpu_percent())
            self.metrics["memory_usage"].append(psutil.virtual_memory().percent)
            
            # Measure face recognition time
            start_time = time.time()
            self.face_recognizer.recognize_face(face_img)
            end_time = time.time()
            
            # Record time
            recognition_time = (end_time - start_time) * 1000  # Convert to milliseconds
            self.metrics["face_recognition_times"].append(recognition_time)
            
            # Log progress
            if (i + 1) % 10 == 0:
                self.logger.info(f"Completed {i + 1}/{num_iterations} face recognition iterations")
        
        # Calculate statistics
        avg_time = sum(self.metrics["face_recognition_times"]) / len(self.metrics["face_recognition_times"])
        max_time = max(self.metrics["face_recognition_times"])
        min_time = min(self.metrics["face_recognition_times"])
        
        self.logger.info(f"Face recognition performance: Avg={avg_time:.2f}ms, Min={min_time:.2f}ms, Max={max_time:.2f}ms")
    
    def test_database_performance(self, num_iterations=100):
        """
        Test database operation performance.
        
        Args:
            num_iterations (int): Number of test iterations
        """
        self.logger.info(f"Testing database performance with {num_iterations} iterations")
        
        # Run test iterations
        for i in range(num_iterations):
            # Generate a unique student ID
            student_id = f"perf{i:05d}"
            student_name = f"Performance Test Student {i}"
            
            # Monitor CPU and memory
            self.metrics["cpu_usage"].append(psutil.cpu_percent())
            self.metrics["memory_usage"].append(psutil.virtual_memory().percent)
            
            # Measure database operation time
            start_time = time.time()
            
            # Add student
            self.db.add_student(student_id, student_name)
            
            # Check if student exists
            self.db.student_exists(student_id)
            
            # Get student name
            self.db.get_student_name(student_id)
            
            end_time = time.time()
            
            # Record time
            db_time = (end_time - start_time) * 1000  # Convert to milliseconds
            self.metrics["database_operation_times"].append(db_time)
            
            # Log progress
            if (i + 1) % 10 == 0:
                self.logger.info(f"Completed {i + 1}/{num_iterations} database operation iterations")
        
        # Calculate statistics
        avg_time = sum(self.metrics["database_operation_times"]) / len(self.metrics["database_operation_times"])
        max_time = max(self.metrics["database_operation_times"])
        min_time = min(self.metrics["database_operation_times"])
        
        self.logger.info(f"Database operation performance: Avg={avg_time:.2f}ms, Min={min_time:.2f}ms, Max={max_time:.2f}ms")
    
    def generate_performance_report(self, output_dir=None):
        """
        Generate a performance report.
        
        Args:
            output_dir (str): Directory to save the report
            
        Returns:
            str: Path to the generated report
        """
        if output_dir is None:
            output_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "reports")
        
        # Create output directory if it doesn't exist
        os.makedirs(output_dir, exist_ok=True)
        
        # Generate report file path
        report_path = os.path.join(output_dir, f"performance_report_{int(time.time())}.txt")
        
        # Write report
        with open(report_path, "w") as f:
            # Write system information
            f.write("System Information:\n")
            for key, value in self.system_info.items():
                f.write(f"  {key}: {value}\n")
            f.write("\n")
            
            # Write performance metrics
            f.write("Performance Metrics:\n")
            
            # Face detection
            if self.metrics["face_detection_times"]:
                avg_time = sum(self.metrics["face_detection_times"]) / len(self.metrics["face_detection_times"])
                max_time = max(self.metrics["face_detection_times"])
                min_time = min(self.metrics["face_detection_times"])
                f.write(f"  Face Detection:\n")
                f.write(f"    Average Time: {avg_time:.2f} ms\n")
                f.write(f"    Minimum Time: {min_time:.2f} ms\n")
                f.write(f"    Maximum Time: {max_time:.2f} ms\n")
                f.write(f"    Iterations: {len(self.metrics['face_detection_times'])}\n")
                f.write("\n")
            
            # Face recognition
            if self.metrics["face_recognition_times"]:
                avg_time = sum(self.metrics["face_recognition_times"]) / len(self.metrics["face_recognition_times"])
                max_time = max(self.metrics["face_recognition_times"])
                min_time = min(self.metrics["face_recognition_times"])
                f.write(f"  Face Recognition:\n")
                f.write(f"    Average Time: {avg_time:.2f} ms\n")
                f.write(f"    Minimum Time: {min_time:.2f} ms\n")
                f.write(f"    Maximum Time: {max_time:.2f} ms\n")
                f.write(f"    Iterations: {len(self.metrics['face_recognition_times'])}\n")
                f.write("\n")
            
            # Database operations
            if self.metrics["database_operation_times"]:
                avg_time = sum(self.metrics["database_operation_times"]) / len(self.metrics["database_operation_times"])
                max_time = max(self.metrics["database_operation_times"])
                min_time = min(self.metrics["database_operation_times"])
                f.write(f"  Database Operations:\n")
                f.write(f"    Average Time: {avg_time:.2f} ms\n")
                f.write(f"    Minimum Time: {min_time:.2f} ms\n")
                f.write(f"    Maximum Time: {max_time:.2f} ms\n")
                f.write(f"    Iterations: {len(self.metrics['database_operation_times'])}\n")
                f.write("\n")
            
            # Resource usage
            if self.metrics["cpu_usage"]:
                avg_cpu = sum(self.metrics["cpu_usage"]) / len(self.metrics["cpu_usage"])
                max_cpu = max(self.metrics["cpu_usage"])
                min_cpu = min(self.metrics["cpu_usage"])
                f.write(f"  CPU Usage:\n")
                f.write(f"    Average: {avg_cpu:.2f}%\n")
                f.write(f"    Minimum: {min_cpu:.2f}%\n")
                f.write(f"    Maximum: {max_cpu:.2f}%\n")
                f.write("\n")
            
            if self.metrics["memory_usage"]:
                avg_mem = sum(self.metrics["memory_usage"]) / len(self.metrics["memory_usage"])
                max_mem = max(self.metrics["memory_usage"])
                min_mem = min(self.metrics["memory_usage"])
                f.write(f"  Memory Usage:\n")
                f.write(f"    Average: {avg_mem:.2f}%\n")
                f.write(f"    Minimum: {min_mem:.2f}%\n")
                f.write(f"    Maximum: {max_mem:.2f}%\n")
                f.write("\n")
            
            # Conclusion
            f.write("Conclusion:\n")
            
            # Determine if performance is acceptable for i5 gen 8
            is_acceptable = True
            
            if self.metrics["face_detection_times"]:
                avg_detection_time = sum(self.metrics["face_detection_times"]) / len(self.metrics["face_detection_times"])
                if avg_detection_time > 100:  # More than 100ms is slow
                    is_acceptable = False
                    f.write("  Face detection performance may be slow on the target hardware.\n")
            
            if self.metrics["face_recognition_times"]:
                avg_recognition_time = sum(self.metrics["face_recognition_times"]) / len(self.metrics["face_recognition_times"])
                if avg_recognition_time > 200:  # More than 200ms is slow
                    is_acceptable = False
                    f.write("  Face recognition performance may be slow on the target hardware.\n")
            
            if is_acceptable:
                f.write("  The system should perform well on i5 gen 8 processors.\n")
        
        # Generate performance charts
        self.generate_performance_charts(output_dir)
        
        self.logger.info(f"Performance report generated: {report_path}")
        
        return report_path
    
    def generate_performance_charts(self, output_dir):
        """
        Generate performance charts.
        
        Args:
            output_dir (str): Directory to save the charts
        """
        # Create charts directory
        charts_dir = os.path.join(output_dir, "charts")
        os.makedirs(charts_dir, exist_ok=True)
        
        # Face detection time chart
        if self.metrics["face_detection_times"]:
            plt.figure(figsize=(10, 6))
            plt.plot(self.metrics["face_detection_times"])
            plt.title("Face Detection Time")
            plt.xlabel("Iteration")
            plt.ylabel("Time (ms)")
            plt.grid(True)
            plt.savefig(os.path.join(charts_dir, "face_detection_time.png"))
            plt.close()
        
        # Face recognition time chart
        if self.metrics["face_recognition_times"]:
            plt.figure(figsize=(10, 6))
            plt.plot(self.metrics["face_recognition_times"])
            plt.title("Face Recognition Time")
            plt.xlabel("Iteration")
            plt.ylabel("Time (ms)")
            plt.grid(True)
            plt.savefig(os.path.join(charts_dir, "face_recognition_time.png"))
            plt.close()
        
        # Database operation time chart
        if self.metrics["database_operation_times"]:
            plt.figure(figsize=(10, 6))
            plt.plot(self.metrics["database_operation_times"])
            plt.title("Database Operation Time")
            plt.xlabel("Iteration")
            plt.ylabel("Time (ms)")
            plt.grid(True)
            plt.savefig(os.path.join(charts_dir, "database_operation_time.png"))
            plt.close()
        
        # CPU usage chart
        if self.metrics["cpu_usage"]:
            plt.figure(figsize=(10, 6))
            plt.plot(self.metrics["cpu_usage"])
            plt.title("CPU Usage")
            plt.xlabel("Measurement")
            plt.ylabel("Usage (%)")
            plt.grid(True)
            plt.savefig(os.path.join(charts_dir, "cpu_usage.png"))
            plt.close()
        
        # Memory usage chart
        if self.metrics["memory_usage"]:
            plt.figure(figsize=(10, 6))
            plt.plot(self.metrics["memory_usage"])
            plt.title("Memory Usage")
            plt.xlabel("Measurement")
            plt.ylabel("Usage (%)")
            plt.grid(True)
            plt.savefig(os.path.join(charts_dir, "memory_usage.png"))
            plt.close()
        
        self.logger.info(f"Performance charts generated in: {charts_dir}")
    
    def run_performance_tests(self):
        """Run all performance tests."""
        self.logger.info("Running all performance tests")
        
        # Run tests
        self.test_face_detection_performance()
        self.test_face_recognition_performance()
        self.test_database_performance()
        
        # Generate report
        report_path = self.generate_performance_report()
        
        return report_path

def run_performance_tests():
    """Run performance tests."""
    test = PerformanceTest()
    return test.run_performance_tests()

if __name__ == "__main__":
    run_performance_tests()
