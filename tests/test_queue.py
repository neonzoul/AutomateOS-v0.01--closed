#!/usr/bin/env python3
"""
Test script for the task queue infrastructure.

This script tests the Redis connection, job enqueuing, and worker functionality.
"""

import time
import json
from app.queue import (
    get_redis_connection, 
    get_workflow_queue, 
    enqueue_workflow_execution,
    get_job_status,
    get_queue_info
)

def test_redis_connection():
    """Test Redis connection."""
    print("Testing Redis connection...")
    try:
        redis_conn = get_redis_connection()
        redis_conn.ping()
        print("✓ Redis connection successful")
        return True
    except Exception as e:
        print(f"✗ Redis connection failed: {e}")
        return False

def test_queue_operations():
    """Test queue operations."""
    print("\nTesting queue operations...")
    try:
        queue = get_workflow_queue()
        print(f"✓ Queue '{queue.name}' initialized")
        
        # Test queue info
        info = get_queue_info()
        print(f"✓ Queue info: {json.dumps(info, indent=2)}")
        return True
    except Exception as e:
        print(f"✗ Queue operations failed: {e}")
        return False

def test_job_enqueuing():
    """Test job enqueuing."""
    print("\nTesting job enqueuing...")
    try:
        # Test payload
        test_payload = {
            "test": True,
            "message": "Test workflow execution",
            "timestamp": time.time()
        }
        
        # Enqueue a test job (workflow_id=1 for testing)
        job_id = enqueue_workflow_execution(1, test_payload)
        print(f"✓ Job enqueued with ID: {job_id}")
        
        # Check job status
        status = get_job_status(job_id)
        print(f"✓ Job status: {json.dumps(status, indent=2)}")
        
        return True
    except Exception as e:
        print(f"✗ Job enqueuing failed: {e}")
        return False

def main():
    """Run all tests."""
    print("AutomateOS Queue Infrastructure Test")
    print("=" * 40)
    
    tests = [
        test_redis_connection,
        test_queue_operations,
        test_job_enqueuing
    ]
    
    passed = 0
    for test in tests:
        if test():
            passed += 1
    
    print(f"\nTest Results: {passed}/{len(tests)} passed")
    
    if passed == len(tests):
        print("✓ All tests passed! Queue infrastructure is working.")
    else:
        print("✗ Some tests failed. Check Redis installation and configuration.")

if __name__ == "__main__":
    main()