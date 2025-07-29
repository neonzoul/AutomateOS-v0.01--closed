#!/usr/bin/env python3
"""
Startup script for AutomateOS background workers.

This script provides an easy way to start background workers for processing
workflow execution jobs. It includes basic configuration and error handling.
"""

import os
import sys
import subprocess
from pathlib import Path

def check_redis():
    """Check if Redis is available."""
    try:
        import redis
        redis_url = os.getenv("REDIS_URL", "redis://localhost:6379/0")
        r = redis.from_url(redis_url)
        r.ping()
        return True
    except Exception as e:
        print(f"Redis connection failed: {e}")
        print("Please ensure Redis is installed and running.")
        print("Install Redis: https://redis.io/download")
        return False

def check_dependencies():
    """Check if required dependencies are installed."""
    try:
        import rq
        import redis
        return True
    except ImportError as e:
        print(f"Missing dependency: {e}")
        print("Please install dependencies: pip install -r requirements.txt")
        return False

def main():
    """Main startup function."""
    print("AutomateOS Worker Startup")
    print("=" * 25)
    
    # Check dependencies
    if not check_dependencies():
        sys.exit(1)
    
    # Check Redis connection
    if not check_redis():
        sys.exit(1)
    
    print("✓ Dependencies and Redis connection verified")
    print("Starting worker...")
    print("Press Ctrl+C to stop the worker")
    print("-" * 40)
    
    # Start the worker
    try:
        subprocess.run([sys.executable, "worker.py"])
    except KeyboardInterrupt:
        print("\nWorker stopped by user")
    except Exception as e:
        print(f"Worker error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()