#!/bin/bash

# Render Startup Script for AutomateOS
# This script handles the startup process for both web and worker services

set -e

echo "🚀 Starting AutomateOS on Render..."

# Determine service type from environment or default to web
SERVICE_TYPE=${RENDER_SERVICE_TYPE:-web}

echo "Service Type: $SERVICE_TYPE"
echo "Environment: ${ENVIRONMENT:-production}"
echo "Port: ${PORT:-10000}"

# Wait for database to be ready
echo "Waiting for database connection..."
python -c "
import time
import sys
from app.database import engine
from sqlalchemy import text

max_retries = 30
for i in range(max_retries):
    try:
        with engine.connect() as conn:
            conn.execute(text('SELECT 1'))
        print('✓ Database connection successful!')
        break
    except Exception as e:
        if i == max_retries - 1:
            print(f'✗ Database connection failed after {max_retries} attempts: {e}')
            sys.exit(1)
        print(f'Database not ready, retrying in 2 seconds... ({i+1}/{max_retries})')
        time.sleep(2)
"

# Wait for Redis to be ready
echo "Waiting for Redis connection..."
python -c "
import time
import sys
from app.queue import get_redis_connection

max_retries = 30
redis_conn = get_redis_connection()

for i in range(max_retries):
    try:
        redis_conn.ping()
        print('✓ Redis connection successful!')
        break
    except Exception as e:
        if i == max_retries - 1:
            print(f'✗ Redis connection failed after {max_retries} attempts: {e}')
            sys.exit(1)
        print(f'Redis not ready, retrying in 2 seconds... ({i+1}/{max_retries})')
        time.sleep(2)
"

# Run database migrations (only for web service)
if [ "$SERVICE_TYPE" = "web" ]; then
    echo "Running database migrations..."
    python -m app.migrations
    echo "✓ Database migrations completed"
fi

# Start the appropriate service
if [ "$SERVICE_TYPE" = "worker" ]; then
    echo "Starting background worker..."
    exec python worker.py
else
    echo "Starting web server..."
    exec uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-10000}
fi