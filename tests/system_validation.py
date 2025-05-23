"""
System Validation Script
This script validates the overall functionality of the Enhanced Attendance System.
"""

import os
import sys
import subprocess
import time
import datetime
import tkinter as tk
from tkinter import ttk
import threading

# Add parent directory to path to import modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from tests.test_suite import run_tests
from tests.integration_test import run_integration_tests
from tests.performance_test import run_performance_tests
from utils.logger import Logger

class SystemValidator:
    """
    System validator for the Enhanced Attendance System.
    """
    
    def __init__(self):
        """Initialize the system validator."""
        self.logger = Logger(log_level=Logger.INFO)
        self.logger.info("Starting system validation")
        
        # Create reports directory
        self.reports_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "reports")
        os.makedirs(self.reports_dir, exist_ok=True)
        
        # Validation results
        self.validation_results = {
            "unit_tests": None,
            "integration_tests": None,
            "performance_tests": None,
            "ui_tests": None,
            "overall": None
        }
    
    def run_unit_tests(self):
        """Run unit tests."""
        self.logger.info("Running unit tests")
        
        try:
            # Run unit tests
            test_result = run_tests()
            
            # Check if all tests passed
            if test_result.wasSuccessful():
                self.validation_results["unit_tests"] = "PASS"
                self.logger.info("Unit tests passed")
            else:
                self.validation_results["unit_tests"] = "FAIL"
                self.logger.error(f"Unit tests failed: {test_result.failures} failures, {test_result.errors} errors")
        except Exception as e:
            self.validation_results["unit_tests"] = f"ERROR: {str(e)}"
            self.logger.error(f"Error running unit tests: {e}")
    
    def run_integration_tests(self):
        """Run integration tests."""
        self.logger.info("Running integration tests")
        
        try:
            # Run integration tests
            integration_result = run_integration_tests()
            
            # Check if all tests passed
            if integration_result:
                self.validation_results["integration_tests"] = "PASS"
                self.logger.info("Integration tests passed")
            else:
                self.validation_results["integration_tests"] = "FAIL"
                self.logger.error("Integration tests failed")
        except Exception as e:
            self.validation_results["integration_tests"] = f"ERROR: {str(e)}"
            self.logger.error(f"Error running integration tests: {e}")
    
    def run_performance_tests(self):
        """Run performance tests."""
        self.logger.info("Running performance tests")
        
        try:
            # Run performance tests
            report_path = run_performance_tests()
            
            # Check if report was generated
            if os.path.exists(report_path):
                self.validation_results["performance_tests"] = "PASS"
                self.logger.info(f"Performance tests completed, report generated: {report_path}")
            else:
                self.validation_results["performance_tests"] = "FAIL"
                self.logger.error("Performance tests failed, no report generated")
        except Exception as e:
            self.validation_results["performance_tests"] = f"ERROR: {str(e)}"
            self.logger.error(f"Error running performance tests: {e}")
    
    def run_ui_tests(self):
        """Run UI tests."""
        self.logger.info("Running UI tests")
        
        try:
            # Create a root window for testing
            root = tk.Tk()
            root.withdraw()  # Hide the window
            
            # Import UI components
            from ui.admin.admin_app import AdminApp
            from ui.scanner.scanner_app import ScannerApp
            from utils.theme_manager import ThemeManager
            from utils.icon_manager import IconManager
            
            # Test theme manager
            theme_manager = ThemeManager()
            dark_colors = theme_manager.get_theme_colors("dark")
            light_colors = theme_manager.get_theme_colors("light")
            
            # Test icon manager
            icon_manager = IconManager()
            
            # Test UI components
            try:
                # Create admin app instance
                admin_app = AdminApp(tk.Toplevel())
                admin_app.root.after(1000, admin_app.root.destroy)  # Destroy after 1 second
                
                # Create scanner app instance
                scanner_app = ScannerApp(tk.Toplevel())
                scanner_app.root.after(1000, scanner_app.root.destroy)  # Destroy after 1 second
                
                # Run main loop briefly
                root.after(2000, root.quit)
                root.mainloop()
                
                self.validation_results["ui_tests"] = "PASS"
                self.logger.info("UI tests passed")
            except Exception as e:
                self.validation_results["ui_tests"] = f"FAIL: {str(e)}"
                self.logger.error(f"UI tests failed: {e}")
            finally:
                # Destroy the root window
                root.destroy()
        except Exception as e:
            self.validation_results["ui_tests"] = f"ERROR: {str(e)}"
            self.logger.error(f"Error running UI tests: {e}")
    
    def generate_validation_report(self):
        """
        Generate a validation report.
        
        Returns:
            str: Path to the generated report
        """
        # Generate report file path
        report_path = os.path.join(self.reports_dir, f"validation_report_{int(time.time())}.txt")
        
        # Write report
        with open(report_path, "w") as f:
            # Write header
            f.write("Enhanced Attendance System - Validation Report\n")
            f.write("==============================================\n\n")
            f.write(f"Date: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            
            # Write validation results
            f.write("Validation Results:\n")
            f.write("-----------------\n\n")
            
            # Unit tests
            f.write("Unit Tests: ")
            if self.validation_results["unit_tests"] == "PASS":
                f.write("PASSED\n")
            else:
                f.write(f"FAILED - {self.validation_results['unit_tests']}\n")
            
            # Integration tests
            f.write("Integration Tests: ")
            if self.validation_results["integration_tests"] == "PASS":
                f.write("PASSED\n")
            else:
                f.write(f"FAILED - {self.validation_results['integration_tests']}\n")
            
            # Performance tests
            f.write("Performance Tests: ")
            if self.validation_results["performance_tests"] == "PASS":
                f.write("PASSED\n")
            else:
                f.write(f"FAILED - {self.validation_results['performance_tests']}\n")
            
            # UI tests
            f.write("UI Tests: ")
            if self.validation_results["ui_tests"] == "PASS":
                f.write("PASSED\n")
            else:
                f.write(f"FAILED - {self.validation_results['ui_tests']}\n")
            
            f.write("\n")
            
            # Overall result
            f.write("Overall Validation: ")
            if all(result == "PASS" for result in self.validation_results.values() if result is not None):
                self.validation_results["overall"] = "PASS"
                f.write("PASSED\n")
            else:
                self.validation_results["overall"] = "FAIL"
                f.write("FAILED\n")
            
            f.write("\n")
            
            # System requirements
            f.write("System Requirements:\n")
            f.write("------------------\n")
            f.write("- Python 3.6 or higher\n")
            f.write("- OpenCV 4.x\n")
            f.write("- Tkinter\n")
            f.write("- NumPy\n")
            f.write("- Pandas\n")
            f.write("- Matplotlib (for performance reports)\n")
            f.write("- Minimum: Intel i5 Gen 8 processor\n")
            f.write("- Recommended: 8GB RAM\n")
            f.write("- Webcam for face detection and recognition\n")
            f.write("\n")
            
            # Usage instructions
            f.write("Usage Instructions:\n")
            f.write("-----------------\n")
            f.write("1. Run the main.py script to start the application\n")
            f.write("2. Choose between Admin Interface and Scanner Interface\n")
            f.write("3. Admin Interface: Register students, view reports, manage settings\n")
            f.write("4. Scanner Interface: Monitor attendance, detect unauthorized entry\n")
            f.write("\n")
            
            # Additional notes
            f.write("Additional Notes:\n")
            f.write("---------------\n")
            f.write("- The system supports both dark and light themes\n")
            f.write("- Face registration requires multiple angles for better recognition\n")
            f.write("- Automatic scanning works in real-time for attendance tracking\n")
            f.write("- Security alerts are triggered for unrecognized faces\n")
            f.write("- Attendance reports can be exported to CSV format\n")
        
        self.logger.info(f"Validation report generated: {report_path}")
        
        return report_path
    
    def run_validation(self):
        """
        Run the complete system validation.
        
        Returns:
            dict: Validation results
        """
        self.logger.info("Running complete system validation")
        
        # Run tests
        self.run_unit_tests()
        self.run_integration_tests()
        self.run_performance_tests()
        self.run_ui_tests()
        
        # Generate report
        report_path = self.generate_validation_report()
        
        # Log results
        self.logger.info("Validation results:")
        for test_name, result in self.validation_results.items():
            self.logger.info(f"{test_name}: {result}")
        
        return self.validation_results, report_path

def run_system_validation():
    """
    Run system validation.
    
    Returns:
        tuple: (validation_results, report_path)
    """
    validator = SystemValidator()
    return validator.run_validation()

if __name__ == "__main__":
    run_system_validation()
