#!/usr/bin/env python3
"""
Comprehensive test runner for AutomateOS testing and quality assurance.
Executes all test suites and generates a comprehensive test report.
"""

import os
import sys
import subprocess
import time
import json
from datetime import datetime
from typing import Dict, List, Any

# Add the app directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

class TestSuiteRunner:
    """Comprehensive test suite runner for AutomateOS."""
    
    def __init__(self):
        self.test_results = {}
        self.start_time = None
        self.end_time = None
        self.total_tests = 0
        self.passed_tests = 0
        self.failed_tests = 0
    
    def run_pytest_tests(self, test_file: str, test_name: str) -> Dict[str, Any]:
        """Run pytest tests and capture results."""
        print(f"\n🧪 Running {test_name}...")
        print("-" * 50)
        
        start_time = time.time()
        
        try:
            # Run pytest with verbose output and JSON report
            result = subprocess.run([
                sys.executable, "-m", "pytest", 
                test_file, 
                "-v", 
                "--tb=short",
                "--no-header"
            ], capture_output=True, text=True, timeout=300)
            
            end_time = time.time()
            duration = end_time - start_time
            
            # Parse pytest output
            output_lines = result.stdout.split('\n')
            passed = 0
            failed = 0
            errors = []
            
            for line in output_lines:
                if " PASSED " in line:
                    passed += 1
                elif " FAILED " in line:
                    failed += 1
                    errors.append(line.strip())
                elif " ERROR " in line:
                    failed += 1
                    errors.append(line.strip())
            
            # Look for summary line
            summary_line = ""
            for line in output_lines:
                if "passed" in line and ("failed" in line or "error" in line or line.endswith("passed")):
                    summary_line = line.strip()
                    break
            
            success = result.returncode == 0
            
            test_result = {
                "name": test_name,
                "file": test_file,
                "success": success,
                "duration": duration,
                "passed": passed,
                "failed": failed,
                "total": passed + failed,
                "return_code": result.returncode,
                "summary": summary_line,
                "errors": errors,
                "stdout": result.stdout,
                "stderr": result.stderr
            }
            
            if success:
                print(f"✅ {test_name} - PASSED ({passed} tests, {duration:.2f}s)")
            else:
                print(f"❌ {test_name} - FAILED ({passed} passed, {failed} failed, {duration:.2f}s)")
                if errors:
                    print("   Errors:")
                    for error in errors[:3]:  # Show first 3 errors
                        print(f"     {error}")
            
            return test_result
            
        except subprocess.TimeoutExpired:
            print(f"⏰ {test_name} - TIMEOUT (exceeded 5 minutes)")
            return {
                "name": test_name,
                "file": test_file,
                "success": False,
                "duration": 300,
                "passed": 0,
                "failed": 1,
                "total": 1,
                "return_code": -1,
                "summary": "Test timed out",
                "errors": ["Test execution timed out after 5 minutes"],
                "stdout": "",
                "stderr": "Timeout"
            }
        
        except Exception as e:
            print(f"❌ {test_name} - ERROR: {e}")
            return {
                "name": test_name,
                "file": test_file,
                "success": False,
                "duration": 0,
                "passed": 0,
                "failed": 1,
                "total": 1,
                "return_code": -1,
                "summary": f"Exception: {e}",
                "errors": [str(e)],
                "stdout": "",
                "stderr": str(e)
            }
    
    def run_python_script_tests(self, script_file: str, test_name: str) -> Dict[str, Any]:
        """Run Python script tests and capture results."""
        print(f"\n🧪 Running {test_name}...")
        print("-" * 50)
        
        start_time = time.time()
        
        try:
            result = subprocess.run([
                sys.executable, script_file
            ], capture_output=True, text=True, timeout=600)  # 10 minute timeout for E2E and load tests
            
            end_time = time.time()
            duration = end_time - start_time
            
            success = result.returncode == 0
            
            # Try to extract test counts from output
            output = result.stdout
            passed = output.count("✅") + output.count("PASSED")
            failed = output.count("❌") + output.count("FAILED")
            
            test_result = {
                "name": test_name,
                "file": script_file,
                "success": success,
                "duration": duration,
                "passed": passed if success else 0,
                "failed": failed if not success else 1,
                "total": max(passed + failed, 1),
                "return_code": result.returncode,
                "summary": f"Script execution {'succeeded' if success else 'failed'}",
                "errors": [result.stderr] if result.stderr else [],
                "stdout": result.stdout,
                "stderr": result.stderr
            }
            
            if success:
                print(f"✅ {test_name} - PASSED ({duration:.2f}s)")
            else:
                print(f"❌ {test_name} - FAILED ({duration:.2f}s)")
                if result.stderr:
                    print(f"   Error: {result.stderr[:200]}...")
            
            return test_result
            
        except subprocess.TimeoutExpired:
            print(f"⏰ {test_name} - TIMEOUT")
            return {
                "name": test_name,
                "file": script_file,
                "success": False,
                "duration": 600,
                "passed": 0,
                "failed": 1,
                "total": 1,
                "return_code": -1,
                "summary": "Test timed out",
                "errors": ["Test execution timed out"],
                "stdout": "",
                "stderr": "Timeout"
            }
        
        except Exception as e:
            print(f"❌ {test_name} - ERROR: {e}")
            return {
                "name": test_name,
                "file": script_file,
                "success": False,
                "duration": 0,
                "passed": 0,
                "failed": 1,
                "total": 1,
                "return_code": -1,
                "summary": f"Exception: {e}",
                "errors": [str(e)],
                "stdout": "",
                "stderr": str(e)
            }
    
    def check_dependencies(self) -> bool:
        """Check if required dependencies are installed."""
        print("🔍 Checking test dependencies...")
        
        required_packages = ["pytest", "requests", "fastapi", "sqlmodel"]
        missing_packages = []
        
        for package in required_packages:
            try:
                __import__(package)
                print(f"✅ {package}")
            except ImportError:
                print(f"❌ {package} - MISSING")
                missing_packages.append(package)
        
        if missing_packages:
            print(f"\n❌ Missing required packages: {', '.join(missing_packages)}")
            print("Please install them with: pip install pytest requests fastapi sqlmodel")
            return False
        
        print("✅ All dependencies available")
        return True
    
    def run_all_tests(self) -> Dict[str, Any]:
        """Run all test suites."""
        print("🚀 AutomateOS Comprehensive Test Suite")
        print("=" * 60)
        print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        self.start_time = time.time()
        
        # Check dependencies first
        if not self.check_dependencies():
            return {"success": False, "error": "Missing dependencies"}
        
        # Define test suites
        test_suites = [
            # Unit tests with pytest
            {
                "name": "Authentication Unit Tests",
                "file": "tests/test_auth_unit.py",
                "type": "pytest",
                "description": "Unit tests for authentication endpoints and JWT handling"
            },
            {
                "name": "Workflow Integration Tests", 
                "file": "tests/test_workflow_integration.py",
                "type": "pytest",
                "description": "Integration tests for workflow CRUD operations"
            },
            {
                "name": "Node Execution Tests",
                "file": "tests/test_node_execution.py", 
                "type": "pytest",
                "description": "Tests for node execution logic and error handling"
            },
            
            # Script-based tests
            {
                "name": "Frontend Component Tests",
                "file": "tests/test_frontend_components.py",
                "type": "script",
                "description": "Frontend component tests for critical user flows"
            },
            {
                "name": "End-to-End Tests",
                "file": "tests/test_e2e_workflow.py",
                "type": "script", 
                "description": "End-to-end tests for complete workflow creation and execution"
            },
            {
                "name": "Load Performance Tests",
                "file": "tests/test_load_performance.py",
                "type": "script",
                "description": "Load testing on webhook endpoints and execution engine"
            }
        ]
        
        # Run each test suite
        for suite in test_suites:
            print(f"\n📋 {suite['description']}")
            
            if not os.path.exists(suite['file']):
                print(f"⚠️  Test file not found: {suite['file']}")
                self.test_results[suite['name']] = {
                    "name": suite['name'],
                    "file": suite['file'],
                    "success": False,
                    "duration": 0,
                    "passed": 0,
                    "failed": 1,
                    "total": 1,
                    "summary": "Test file not found",
                    "errors": ["Test file does not exist"]
                }
                continue
            
            if suite['type'] == 'pytest':
                result = self.run_pytest_tests(suite['file'], suite['name'])
            else:
                result = self.run_python_script_tests(suite['file'], suite['name'])
            
            self.test_results[suite['name']] = result
        
        self.end_time = time.time()
        
        # Calculate totals
        self.total_tests = sum(r['total'] for r in self.test_results.values())
        self.passed_tests = sum(r['passed'] for r in self.test_results.values())
        self.failed_tests = sum(r['failed'] for r in self.test_results.values())
        
        return self.generate_report()
    
    def generate_report(self) -> Dict[str, Any]:
        """Generate comprehensive test report."""
        total_duration = self.end_time - self.start_time if self.end_time and self.start_time else 0
        
        # Calculate success rate
        success_rate = (self.passed_tests / self.total_tests * 100) if self.total_tests > 0 else 0
        
        # Count successful test suites
        successful_suites = sum(1 for r in self.test_results.values() if r['success'])
        total_suites = len(self.test_results)
        
        report = {
            "timestamp": datetime.now().isoformat(),
            "duration": total_duration,
            "summary": {
                "total_suites": total_suites,
                "successful_suites": successful_suites,
                "failed_suites": total_suites - successful_suites,
                "total_tests": self.total_tests,
                "passed_tests": self.passed_tests,
                "failed_tests": self.failed_tests,
                "success_rate": success_rate,
                "overall_success": success_rate >= 80 and successful_suites >= (total_suites * 0.8)
            },
            "test_results": self.test_results
        }
        
        self.print_report(report)
        self.save_report(report)
        
        return report
    
    def print_report(self, report: Dict[str, Any]):
        """Print formatted test report."""
        print("\n" + "=" * 60)
        print("📊 COMPREHENSIVE TEST REPORT")
        print("=" * 60)
        
        summary = report['summary']
        
        print(f"\n⏱️  Total Duration: {report['duration']:.2f} seconds")
        print(f"📋 Test Suites: {summary['successful_suites']}/{summary['total_suites']} passed")
        print(f"🧪 Individual Tests: {summary['passed_tests']}/{summary['total_tests']} passed")
        print(f"📈 Success Rate: {summary['success_rate']:.1f}%")
        
        print(f"\n{'✅' if summary['overall_success'] else '❌'} Overall Result: {'PASSED' if summary['overall_success'] else 'FAILED'}")
        
        # Detailed results
        print(f"\n📋 DETAILED RESULTS:")
        print("-" * 40)
        
        for name, result in report['test_results'].items():
            status = "✅ PASSED" if result['success'] else "❌ FAILED"
            duration = result['duration']
            tests = f"{result['passed']}/{result['total']}"
            
            print(f"{status} {name}")
            print(f"   Duration: {duration:.2f}s | Tests: {tests}")
            
            if not result['success'] and result['errors']:
                print(f"   Errors: {result['errors'][0][:80]}...")
        
        # Requirements coverage
        print(f"\n📋 REQUIREMENTS COVERAGE:")
        print("-" * 40)
        
        requirements_coverage = {
            "1.1, 1.2, 1.3, 1.4, 1.5": "Authentication Unit Tests",
            "2.1, 2.2, 2.3, 2.4": "Workflow Integration Tests", 
            "3.1, 3.2, 3.3": "Node Execution Tests",
            "User Flows": "Frontend Component Tests",
            "4.1, 4.2, 4.3": "End-to-End Tests",
            "7.1, 7.2": "Load Performance Tests"
        }
        
        for req, test_name in requirements_coverage.items():
            if test_name in report['test_results']:
                status = "✅" if report['test_results'][test_name]['success'] else "❌"
                print(f"{status} Requirements {req}: {test_name}")
            else:
                print(f"⚠️  Requirements {req}: {test_name} - NOT FOUND")
    
    def save_report(self, report: Dict[str, Any]):
        """Save test report to file."""
        try:
            report_file = f"tests/test_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            with open(report_file, 'w') as f:
                json.dump(report, f, indent=2)
            print(f"\n💾 Test report saved to: {report_file}")
        except Exception as e:
            print(f"⚠️  Failed to save report: {e}")

def main():
    """Main function to run all tests."""
    runner = TestSuiteRunner()
    
    try:
        report = runner.run_all_tests()
        
        # Exit with appropriate code
        if report['summary']['overall_success']:
            print(f"\n🎉 All tests completed successfully!")
            sys.exit(0)
        else:
            print(f"\n💥 Some tests failed. Check the report above.")
            sys.exit(1)
            
    except KeyboardInterrupt:
        print(f"\n⚠️  Test execution interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Test execution failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()