#!/usr/bin/env python3
"""
Simple script to start the FastAPI server for manual testing.
"""

import subprocess
import sys

def start_server():
    """Start the FastAPI server."""
    try:
        print("🚀 Starting AutomateOS API Server...")
        print("📍 Server will be available at: http://127.0.0.1:8002")
        print("📚 API Documentation: http://127.0.0.1:8002/docs")
        print("🛑 Press Ctrl+C to stop the server")
        print("-" * 50)
        
        # Start the server
        subprocess.run([
            sys.executable, "-m", "uvicorn", 
            "app.main:app", 
            "--host", "127.0.0.1", 
            "--port", "8002", 
            "--reload"
        ])
    except KeyboardInterrupt:
        print("\n🛑 Server stopped by user")
    except Exception as e:
        print(f"❌ Error starting server: {e}")

if __name__ == "__main__":
    start_server()