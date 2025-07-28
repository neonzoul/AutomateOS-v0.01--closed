#!/usr/bin/env python3
"""
Startup script for AutomateOS FastAPI server without Redis dependency.

This script starts the FastAPI server with mock queue functionality
when Redis is not available.
"""

import os
import sys
import subprocess

def check_redis():
    """Check if Redis is available (non-blocking)."""
    try:
        import redis
        redis_url = os.getenv("REDIS_URL", "redis://localhost:6379/0")
        r = redis.from_url(redis_url)
        r.ping()
        print("✓ Redis connection verified - using real queue")
        return True
    except Exception as e:
        print(f"⚠ Redis not available: {e}")
        print("  Using mock queue for testing")
        return False

def patch_queue_imports():
    """Patch the queue imports to use mock queue."""
    # Set environment variable to use mock queue
    os.environ["USE_MOCK_QUEUE"] = "true"

def main():
    """Main startup function."""
    print("AutomateOS Server Startup (No Redis Required)")
    print("=" * 45)
    
    # Check Redis (non-blocking)
    redis_ok = check_redis()
    
    if not redis_ok:
        print("✓ Configuring mock queue for testing")
        patch_queue_imports()
    
    print("Starting FastAPI server...")
    print("API will be available at: http://localhost:8000")
    print("API docs at: http://localhost:8000/docs")
    print("Press Ctrl+C to stop the server")
    print("-" * 45)
    
    # Start the server
    try:
        subprocess.run([
            sys.executable, "-m", "uvicorn", 
            "app.main_no_redis:app", 
            "--reload", 
            "--host", "0.0.0.0", 
            "--port", "8000"
        ])
    except KeyboardInterrupt:
        print("\nServer stopped by user")
    except Exception as e:
        print(f"Server error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()