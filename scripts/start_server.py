#!/usr/bin/env python3
"""
Startup script for AutomateOS FastAPI server.

This script starts the FastAPI server with proper configuration and
includes checks for the task queue infrastructure.
"""

import os
import sys
import subprocess

def check_redis():
    """Check if Redis is available."""
    try:
        import redis
        redis_url = os.getenv("REDIS_URL", "redis://localhost:6379/0")
        r = redis.from_url(redis_url)
        r.ping()
        print("[OK] Redis connection verified")
        return True
    except Exception as e:
        print(f"[!] Redis connection failed: {e}")
        print("  Queue functionality will not work without Redis")
        print("  Install Redis: https://redis.io/download")
        return False

def main():
    """Main startup function."""
    print("AutomateOS Server Startup")
    print("=" * 25)
    
    # Check Redis (non-blocking)
    redis_ok = check_redis()
    
    if redis_ok:
        print("[OK] Task queue infrastructure ready")
    else:
        print("[!] Starting server without queue functionality")
    
    print("Starting FastAPI server...")
    print("API will be available at: http://localhost:8000")
    print("API docs at: http://localhost:8000/docs")
    print("Press Ctrl+C to stop the server")
    print("-" * 40)
    
    # Start the server
    try:
        subprocess.run([
            sys.executable, "-m", "uvicorn", 
            "app.main:app", 
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