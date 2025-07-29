# AutomateOS Production Dockerfile
# Multi-stage build for optimized production image

# Stage 1: Build frontend
FROM node:18-alpine AS frontend-builder

WORKDIR /app/frontend

# Copy package files
COPY frontend/package*.json ./

# Install dependencies
RUN npm ci --only=production

# Copy frontend source
COPY frontend/ ./

# Build frontend for production
RUN npm run build:prod

# Stage 2: Python application
FROM python:3.11-slim AS backend

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV ENVIRONMENT=production
ENV DEBUG=false

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Create app user
RUN useradd --create-home --shell /bin/bash app

# Set work directory
WORKDIR /app

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY app/ ./app/
COPY worker.py .
COPY .env.example .

# Copy frontend build from previous stage
COPY --from=frontend-builder /app/frontend/dist ./static

# Copy startup scripts
COPY scripts/build-production.sh ./scripts/
RUN chmod +x scripts/build-production.sh

# Create startup script
COPY --chmod=755 <<EOF /app/start.sh
#!/bin/bash
set -e

echo "Starting AutomateOS..."

# Wait for database
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
        print('Database is ready!')
        break
    except Exception as e:
        if i == max_retries - 1:
            print(f'Database not ready after {max_retries} attempts: {e}')
            sys.exit(1)
        print(f'Database not ready, retrying in 2 seconds... ({i+1}/{max_retries})')
        time.sleep(2)
"

# Run migrations
echo "Running database migrations..."
python -m app.migrations

# Start application based on process type
if [ "\$PROCESS_TYPE" = "worker" ]; then
    echo "Starting background worker..."
    exec python worker.py
else
    echo "Starting web server..."
    exec uvicorn app.main:app --host 0.0.0.0 --port \${PORT:-8000}
fi
EOF

# Change ownership to app user
RUN chown -R app:app /app

# Switch to app user
USER app

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:8000/', timeout=10)"

# Default command
CMD ["./start.sh"]