#!/usr/bin/env python3
"""
Background worker script for processing AutomateOS workflow execution jobs.

This script runs RQ workers that consume jobs from the workflow execution queue.
It should be run as a separate process from the main FastAPI application to
handle asynchronous workflow processing.

Usage:
    python worker.py

Environment Variables:
    REDIS_URL: Redis connection URL (default: redis://localhost:6379/0)
    WORKER_COUNT: Number of worker processes (default: 1)
"""

import os
import sys
import signal
from rq import Worker
from app.queue import get_redis_connection, get_workflow_queue

def signal_handler(signum, frame):
    """Handle shutdown signals gracefully."""
    print(f"\nReceived signal {signum}. Shutting down worker...")
    sys.exit(0)

def main():
    """Main worker function."""
    # Register signal handlers for graceful shutdown
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    # Get Redis connection and queue
    redis_conn = get_redis_connection()
    queue = get_workflow_queue()
    
    print(f"Starting AutomateOS worker...")
    print(f"Redis URL: {os.getenv('REDIS_URL', 'redis://localhost:6379/0')}")
    print(f"Queue: {queue.name}")
    print(f"Worker PID: {os.getpid()}")
    
    # Create and start worker
    worker = Worker([queue], connection=redis_conn)
    print("Worker started. Waiting for jobs...")
    worker.work()

if __name__ == "__main__":
    main()