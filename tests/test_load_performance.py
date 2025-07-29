#!/usr/bin/env python3
"""
Load testing for webhook endpoints and execution engine.
Tests system performance under concurrent load and stress conditions.
"""

import asyncio
import aiohttp
import time
import statistics
import threading
import requests
import json
import os
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import List, Dict, Any, Tuple
import subprocess

# Add the app directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

BASE_URL = "http://127.0.0.1:8000"

class LoadTestRunner:
    """Load testing runner for AutomateOS endpoints."""
    
    def __init__(self):
        self.base_url = BASE_URL
        self.test_user_email = f"load_test_{int(time.time())}@example.com"
        self.test_password = "load_test_password_123"
        self.auth_token = None
        self.test_workflow_id = None
        self.webhook_url = None
        self.server_process = None
        self.results = {
            "response_times": [],
            "success_count": 0,
            "error_count": 0,
            "errors": []
        }
    
    def start_server(self) -> bool:
        """Start the FastAPI server for load testing."""
        try:
            # Check if server is already running
            response = requests.get(f"{self.base_url}/health", timeout=2)
            if response.status_code == 200:
                print("✅ Server already running")
                return True
        except requests.exceptions.RequestException:
            pass
        
        print("🚀 Starting server for load testing...")
        try:
            self.server_process = subprocess.Popen(
                [sys.executable, "-m", "uvicorn", "app.main:app", "--host", "127.0.0.1", "--port", "8000"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            
            # Wait for server to start
            for _ in range(30):
                try:
                    response = requests.get(f"{self.base_url}/health", timeout=1)
                    if response.status_code == 200:
                        print("✅ Server started successfully")
                        return True
                except requests.exceptions.RequestException:
                    time.sleep(1)
            
            print("❌ Server failed to start")
            return False
            
        except Exception as e:
            print(f"❌ Failed to start server: {e}")
            return False
    
    def stop_server(self):
        """Stop the test server."""
        if self.server_process:
            self.server_process.terminate()
            self.server_process.wait()
            print("🛑 Server stopped")
    
    def setup_test_data(self) -> bool:
        """Set up test user and workflow for load testing."""
        print("📝 Setting up test data...")
        
        # Register user
        user_data = {
            "email": self.test_user_email,
            "password": self.test_password
        }
        
        try:
            response = requests.post(f"{self.base_url}/register/", json=user_data, timeout=10)
            if response.status_code not in [200, 400]:  # 400 if user already exists
                print(f"❌ User registration failed: {response.status_code}")
                return False
        except requests.exceptions.RequestException as e:
            print(f"❌ Registration failed: {e}")
            return False
        
        # Login
        login_data = {
            "username": self.test_user_email,
            "password": self.test_password
        }
        
        try:
            response = requests.post(f"{self.base_url}/auth/token", data=login_data, timeout=10)
            if response.status_code != 200:
                print(f"❌ Login failed: {response.status_code}")
                return False
            
            self.auth_token = response.json()["access_token"]
        except requests.exceptions.RequestException as e:
            print(f"❌ Login failed: {e}")
            return False
        
        # Create test workflow
        workflow_data = {
            "name": "Load Test Workflow",
            "description": "Workflow for load testing",
            "definition": {
                "nodes": [
                    {
                        "id": "trigger-1",
                        "type": "webhook",
                        "config": {"method": "POST"}
                    },
                    {
                        "id": "http-1",
                        "type": "http_request",
                        "config": {
                            "url": "https://httpbin.org/post",
                            "method": "POST",
                            "headers": {"Content-Type": "application/json"},
                            "body": {"test": "load_test_data"}
                        }
                    }
                ],
                "connections": [{"from": "trigger-1", "to": "http-1"}]
            },
            "is_active": True
        }
        
        headers = {"Authorization": f"Bearer {self.auth_token}"}
        
        try:
            response = requests.post(f"{self.base_url}/workflows/", json=workflow_data, headers=headers, timeout=10)
            if response.status_code != 200:
                print(f"❌ Workflow creation failed: {response.status_code}")
                return False
            
            workflow = response.json()
            self.test_workflow_id = workflow["id"]
            self.webhook_url = workflow["webhook_url"]
            
            print(f"✅ Test data setup complete")
            print(f"   Workflow ID: {self.test_workflow_id}")
            print(f"   Webhook URL: {self.webhook_url}")
            
            return True
            
        except requests.exceptions.RequestException as e:
            print(f"❌ Workflow creation failed: {e}")
            return False
    
    def cleanup(self):
        """Clean up test data."""
        if self.auth_token and self.test_workflow_id:
            headers = {"Authorization": f"Bearer {self.auth_token}"}
            try:
                requests.delete(f"{self.base_url}/workflows/{self.test_workflow_id}", headers=headers)
            except:
                pass
        
        self.stop_server()
    
    def single_webhook_request(self, request_id: int) -> Dict[str, Any]:
        """Make a single webhook request and measure performance."""
        webhook_id = self.webhook_url.split("/")[-1]
        payload = {
            "request_id": request_id,
            "timestamp": time.time(),
            "test_data": f"load_test_request_{request_id}"
        }
        
        start_time = time.time()
        
        try:
            response = requests.post(f"{self.base_url}/webhook/{webhook_id}", json=payload, timeout=30)
            end_time = time.time()
            
            response_time = (end_time - start_time) * 1000  # Convert to milliseconds
            
            return {
                "request_id": request_id,
                "status_code": response.status_code,
                "response_time": response_time,
                "success": response.status_code == 200,
                "error": None
            }
            
        except requests.exceptions.RequestException as e:
            end_time = time.time()
            response_time = (end_time - start_time) * 1000
            
            return {
                "request_id": request_id,
                "status_code": 0,
                "response_time": response_time,
                "success": False,
                "error": str(e)
            }
    
    def concurrent_webhook_load_test(self, num_requests: int, max_workers: int = 10) -> Dict[str, Any]:
        """Run concurrent webhook load test."""
        print(f"\n🔥 Running concurrent webhook load test...")
        print(f"   Requests: {num_requests}")
        print(f"   Max Workers: {max_workers}")
        
        start_time = time.time()
        results = []
        
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            # Submit all requests
            future_to_request = {
                executor.submit(self.single_webhook_request, i): i 
                for i in range(num_requests)
            }
            
            # Collect results
            for future in as_completed(future_to_request):
                request_id = future_to_request[future]
                try:
                    result = future.result()
                    results.append(result)
                    
                    if result["success"]:
                        print(f"✅ Request {request_id}: {result['response_time']:.2f}ms")
                    else:
                        print(f"❌ Request {request_id}: {result['error'] or 'HTTP ' + str(result['status_code'])}")
                        
                except Exception as e:
                    print(f"❌ Request {request_id} failed: {e}")
                    results.append({
                        "request_id": request_id,
                        "success": False,
                        "error": str(e),
                        "response_time": 0
                    })
        
        end_time = time.time()
        total_time = end_time - start_time
        
        # Calculate statistics
        successful_results = [r for r in results if r["success"]]
        response_times = [r["response_time"] for r in successful_results]
        
        stats = {
            "total_requests": num_requests,
            "successful_requests": len(successful_results),
            "failed_requests": num_requests - len(successful_results),
            "success_rate": (len(successful_results) / num_requests) * 100,
            "total_time": total_time,
            "requests_per_second": num_requests / total_time,
            "response_times": {
                "min": min(response_times) if response_times else 0,
                "max": max(response_times) if response_times else 0,
                "mean": statistics.mean(response_times) if response_times else 0,
                "median": statistics.median(response_times) if response_times else 0,
                "p95": statistics.quantiles(response_times, n=20)[18] if len(response_times) > 20 else (max(response_times) if response_times else 0),
                "p99": statistics.quantiles(response_times, n=100)[98] if len(response_times) > 100 else (max(response_times) if response_times else 0)
            }
        }
        
        return stats
    
    def sequential_webhook_load_test(self, num_requests: int) -> Dict[str, Any]:
        """Run sequential webhook load test to establish baseline."""
        print(f"\n📊 Running sequential webhook load test...")
        print(f"   Requests: {num_requests}")
        
        start_time = time.time()
        results = []
        
        for i in range(num_requests):
            result = self.single_webhook_request(i)
            results.append(result)
            
            if result["success"]:
                print(f"✅ Request {i}: {result['response_time']:.2f}ms")
            else:
                print(f"❌ Request {i}: {result['error'] or 'HTTP ' + str(result['status_code'])}")
        
        end_time = time.time()
        total_time = end_time - start_time
        
        # Calculate statistics
        successful_results = [r for r in results if r["success"]]
        response_times = [r["response_time"] for r in successful_results]
        
        stats = {
            "total_requests": num_requests,
            "successful_requests": len(successful_results),
            "failed_requests": num_requests - len(successful_results),
            "success_rate": (len(successful_results) / num_requests) * 100,
            "total_time": total_time,
            "requests_per_second": num_requests / total_time,
            "response_times": {
                "min": min(response_times) if response_times else 0,
                "max": max(response_times) if response_times else 0,
                "mean": statistics.mean(response_times) if response_times else 0,
                "median": statistics.median(response_times) if response_times else 0
            }
        }
        
        return stats
    
    def api_endpoint_load_test(self, endpoint: str, method: str = "GET", num_requests: int = 50) -> Dict[str, Any]:
        """Load test API endpoints."""
        print(f"\n🎯 Load testing {method} {endpoint}...")
        
        headers = {"Authorization": f"Bearer {self.auth_token}"}
        results = []
        
        def make_request(request_id: int) -> Dict[str, Any]:
            start_time = time.time()
            
            try:
                if method == "GET":
                    response = requests.get(f"{self.base_url}{endpoint}", headers=headers, timeout=10)
                elif method == "POST":
                    response = requests.post(f"{self.base_url}{endpoint}", headers=headers, timeout=10)
                else:
                    raise ValueError(f"Unsupported method: {method}")
                
                end_time = time.time()
                response_time = (end_time - start_time) * 1000
                
                return {
                    "request_id": request_id,
                    "status_code": response.status_code,
                    "response_time": response_time,
                    "success": response.status_code == 200
                }
                
            except requests.exceptions.RequestException as e:
                end_time = time.time()
                response_time = (end_time - start_time) * 1000
                
                return {
                    "request_id": request_id,
                    "status_code": 0,
                    "response_time": response_time,
                    "success": False,
                    "error": str(e)
                }
        
        start_time = time.time()
        
        with ThreadPoolExecutor(max_workers=10) as executor:
            future_to_request = {
                executor.submit(make_request, i): i 
                for i in range(num_requests)
            }
            
            for future in as_completed(future_to_request):
                result = future.result()
                results.append(result)
        
        end_time = time.time()
        total_time = end_time - start_time
        
        # Calculate statistics
        successful_results = [r for r in results if r["success"]]
        response_times = [r["response_time"] for r in successful_results]
        
        stats = {
            "endpoint": endpoint,
            "method": method,
            "total_requests": num_requests,
            "successful_requests": len(successful_results),
            "failed_requests": num_requests - len(successful_results),
            "success_rate": (len(successful_results) / num_requests) * 100,
            "total_time": total_time,
            "requests_per_second": num_requests / total_time,
            "response_times": {
                "min": min(response_times) if response_times else 0,
                "max": max(response_times) if response_times else 0,
                "mean": statistics.mean(response_times) if response_times else 0,
                "median": statistics.median(response_times) if response_times else 0
            }
        }
        
        return stats
    
    def stress_test_webhook_endpoint(self, duration_seconds: int = 60, rps_target: int = 10) -> Dict[str, Any]:
        """Run stress test on webhook endpoint for specified duration."""
        print(f"\n💪 Running webhook stress test...")
        print(f"   Duration: {duration_seconds} seconds")
        print(f"   Target RPS: {rps_target}")
        
        start_time = time.time()
        end_time = start_time + duration_seconds
        results = []
        request_count = 0
        
        def make_continuous_requests():
            nonlocal request_count
            while time.time() < end_time:
                result = self.single_webhook_request(request_count)
                results.append(result)
                request_count += 1
                
                # Control request rate
                time.sleep(1.0 / rps_target)
        
        # Run stress test with multiple threads
        threads = []
        num_threads = min(rps_target, 5)  # Limit threads to avoid overwhelming
        
        for _ in range(num_threads):
            thread = threading.Thread(target=make_continuous_requests)
            thread.start()
            threads.append(thread)
        
        # Wait for all threads to complete
        for thread in threads:
            thread.join()
        
        actual_duration = time.time() - start_time
        
        # Calculate statistics
        successful_results = [r for r in results if r["success"]]
        response_times = [r["response_time"] for r in successful_results]
        
        stats = {
            "test_type": "stress_test",
            "duration": actual_duration,
            "target_rps": rps_target,
            "actual_rps": len(results) / actual_duration,
            "total_requests": len(results),
            "successful_requests": len(successful_results),
            "failed_requests": len(results) - len(successful_results),
            "success_rate": (len(successful_results) / len(results)) * 100 if results else 0,
            "response_times": {
                "min": min(response_times) if response_times else 0,
                "max": max(response_times) if response_times else 0,
                "mean": statistics.mean(response_times) if response_times else 0,
                "median": statistics.median(response_times) if response_times else 0
            }
        }
        
        return stats

def run_load_tests():
    """Run comprehensive load tests."""
    print("🧪 Running Load and Performance Tests")
    print("=" * 60)
    
    runner = LoadTestRunner()
    
    try:
        # Setup
        if not runner.start_server():
            print("❌ Failed to start server")
            return False
        
        if not runner.setup_test_data():
            print("❌ Failed to setup test data")
            return False
        
        test_results = {}
        
        # Test 1: Sequential baseline test
        print("\n1. Sequential Baseline Test")
        test_results["sequential"] = runner.sequential_webhook_load_test(10)
        
        # Test 2: Concurrent load test - Light load
        print("\n2. Concurrent Load Test - Light Load")
        test_results["concurrent_light"] = runner.concurrent_webhook_load_test(20, max_workers=5)
        
        # Test 3: Concurrent load test - Medium load
        print("\n3. Concurrent Load Test - Medium Load")
        test_results["concurrent_medium"] = runner.concurrent_webhook_load_test(50, max_workers=10)
        
        # Test 4: API endpoint load tests
        print("\n4. API Endpoint Load Tests")
        test_results["api_workflows"] = runner.api_endpoint_load_test("/workflows/", "GET", 30)
        test_results["api_health"] = runner.api_endpoint_load_test("/health", "GET", 50)
        
        # Test 5: Stress test (shorter duration for CI/CD)
        print("\n5. Webhook Stress Test")
        test_results["stress"] = runner.stress_test_webhook_endpoint(30, rps_target=5)
        
        # Print summary
        print("\n" + "=" * 60)
        print("📊 LOAD TEST RESULTS SUMMARY")
        print("=" * 60)
        
        for test_name, stats in test_results.items():
            print(f"\n{test_name.upper()}:")
            print(f"  Success Rate: {stats['success_rate']:.1f}%")
            print(f"  Requests/sec: {stats['requests_per_second']:.2f}")
            
            if 'response_times' in stats:
                rt = stats['response_times']
                print(f"  Response Times (ms):")
                print(f"    Min: {rt['min']:.2f}")
                print(f"    Mean: {rt['mean']:.2f}")
                print(f"    Median: {rt['median']:.2f}")
                print(f"    Max: {rt['max']:.2f}")
                if 'p95' in rt:
                    print(f"    P95: {rt['p95']:.2f}")
        
        # Determine overall success
        overall_success = True
        
        # Check success rates
        for test_name, stats in test_results.items():
            if stats['success_rate'] < 90:  # Require 90% success rate
                print(f"⚠️  {test_name} has low success rate: {stats['success_rate']:.1f}%")
                overall_success = False
        
        # Check response times
        for test_name, stats in test_results.items():
            if 'response_times' in stats and stats['response_times']['mean'] > 5000:  # 5 second threshold
                print(f"⚠️  {test_name} has high response times: {stats['response_times']['mean']:.2f}ms")
                overall_success = False
        
        print(f"\n{'✅' if overall_success else '❌'} Overall Load Test Result: {'PASSED' if overall_success else 'FAILED'}")
        
        return overall_success
        
    except Exception as e:
        print(f"❌ Load test failed with exception: {e}")
        return False
        
    finally:
        runner.cleanup()

if __name__ == "__main__":
    success = run_load_tests()
    if not success:
        exit(1)