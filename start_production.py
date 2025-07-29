#!/usr/bin/env python3
"""
Production startup script for AutomateOS.

This script starts the AutomateOS application in production mode with
proper configuration and process management.
"""

import os
import sys
import subprocess
import signal
import time
from pathlib import Path

# Add the app directory to Python path
sys.path.insert(0, str(Path(__file__).parent))

from app.config import settings


def check_dependencies():
    """Check if all required dependencies are available."""
    try:
        import redis
        import psycopg2
        from app.database import engine
        from sqlalchemy import text
        
        # Test database connection
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        print("✓ Database connection successful")
        
        # Test Redis connection
        from app.queue import get_redis_connection
        redis_conn = get_redis_connection()
        redis_conn.ping()
        print("✓ Redis connection successful")
        
        return True
    except Exception as e:
        print(f"✗ Dependency check failed: {e}")
        return False


def run_migrations():
    """Run database migrations."""
    try:
        from app.migrations import run_migrations
        run_migrations()
        print("✓ Database migrations completed")
        return True
    except Exception as e:
        print(f"✗ Migration failed: {e}")
        return False


def start_web_server():
    """Start the FastAPI web server."""
    cmd = [
        "uvicorn",
        "app.main:app",
        "--host", settings.api_host,
        "--port", str(settings.api_port),
        "--workers", "4" if settings.is_production else "1",
        "--access-log" if not settings.is_production else "--no-access-log",
    ]
    
    if settings.is_production:
        cmd.extend(["--worker-class", "uvicorn.workers.UvicornWorker"])
    
    return subprocess.Popen(cmd)


def start_worker():
    """Start the background worker."""
    cmd = ["python", "worker.py"]
    return subprocess.Popen(cmd)


def main():
    """Main startup function."""
    print("🚀 Starting AutomateOS in production mode...")
    print(f"Environment: {settings.environment}")
    print(f"Debug mode: {settings.debug}")
    print(f"Database: {settings.database_url}")
    print(f"Redis: {settings.redis_url}")
    
    # Check dependencies
    if not check_dependencies():
        print("❌ Dependency check failed. Please check your configuration.")
        sys.exit(1)
    
    # Run migrations
    if not run_migrations():
        print("❌ Database migration failed.")
        sys.exit(1)
    
    processes = []
    
    try:
        # Start web server
        print("Starting web server...")
        web_process = start_web_server()
        processes.append(("web", web_process))
        print(f"✓ Web server started (PID: {web_process.pid})")
        
        # Start worker
        print("Starting background worker...")
        worker_process = start_worker()
        processes.append(("worker", worker_process))
        print(f"✓ Background worker started (PID: {worker_process.pid})")
        
        print("\n🎉 AutomateOS is running!")
        print(f"Web interface: http://{settings.api_host}:{settings.api_port}")
        print("Press Ctrl+C to stop all processes")
        
        # Wait for processes
        while True:
            time.sleep(1)
            for name, process in processes:
                if process.poll() is not None:
                    print(f"❌ {name} process died unexpectedly")
                    raise KeyboardInterrupt
    
    except KeyboardInterrupt:
        print("\n🛑 Shutting down AutomateOS...")
        
        # Terminate all processes
        for name, process in processes:
            try:
                process.terminate()
                process.wait(timeout=10)
                print(f"✓ {name} process stopped")
            except subprocess.TimeoutExpired:
                print(f"⚠ Force killing {name} process")
                process.kill()
                process.wait()
            except Exception as e:
                print(f"⚠ Error stopping {name} process: {e}")
        
        print("✓ AutomateOS stopped")


if __name__ == "__main__":
    main()