#!/bin/bash

# AutomateOS Production Build Script
# This script builds the complete application for production deployment

set -e  # Exit on any error

echo "🚀 Starting AutomateOS production build..."

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${GREEN}✓${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}⚠${NC} $1"
}

print_error() {
    echo -e "${RED}✗${NC} $1"
}

# Check if we're in the project root
if [ ! -f "requirements.txt" ] || [ ! -d "frontend" ]; then
    print_error "Please run this script from the project root directory"
    exit 1
fi

# Clean previous builds
print_status "Cleaning previous builds..."
rm -rf frontend/dist
rm -rf build
mkdir -p build

# Install Python dependencies
print_status "Installing Python dependencies..."
if [ ! -d "venv" ]; then
    print_warning "Virtual environment not found, creating one..."
    python -m venv venv
fi

# Activate virtual environment
source venv/bin/activate || source venv/Scripts/activate

pip install -r requirements.txt
print_status "Python dependencies installed"

# Build frontend
print_status "Building React frontend..."
cd frontend

# Install Node dependencies
if [ ! -d "node_modules" ]; then
    print_status "Installing Node.js dependencies..."
    npm install
fi

# Build frontend for production
npm run build:prod
print_status "Frontend build completed"

# Copy frontend build to main build directory
cd ..
cp -r frontend/dist build/static
print_status "Frontend assets copied to build directory"

# Create production startup script
print_status "Creating production startup scripts..."

cat > build/start-production.sh << 'EOF'
#!/bin/bash

# AutomateOS Production Startup Script

set -e

echo "Starting AutomateOS in production mode..."

# Set production environment
export ENVIRONMENT=production
export DEBUG=false

# Start Redis server (if not using external Redis)
if [ "$USE_EXTERNAL_REDIS" != "true" ]; then
    echo "Starting Redis server..."
    redis-server redis.conf &
    REDIS_PID=$!
    echo "Redis started with PID: $REDIS_PID"
fi

# Run database migrations
echo "Running database migrations..."
python -m app.migrations

# Start the web server
echo "Starting FastAPI web server..."
uvicorn app.main:app --host 0.0.0.0 --port ${API_PORT:-8000} --workers ${WEB_WORKERS:-4} &
WEB_PID=$!
echo "Web server started with PID: $WEB_PID"

# Start background workers
echo "Starting background workers..."
python worker.py &
WORKER_PID=$!
echo "Worker started with PID: $WORKER_PID"

# Function to handle shutdown
shutdown() {
    echo "Shutting down AutomateOS..."
    kill $WEB_PID 2>/dev/null || true
    kill $WORKER_PID 2>/dev/null || true
    if [ "$USE_EXTERNAL_REDIS" != "true" ]; then
        kill $REDIS_PID 2>/dev/null || true
    fi
    exit 0
}

# Set up signal handlers
trap shutdown SIGTERM SIGINT

# Wait for processes
wait
EOF

chmod +x build/start-production.sh

# Create Docker-friendly startup script
cat > build/start-docker.sh << 'EOF'
#!/bin/bash

# AutomateOS Docker Startup Script

set -e

echo "Starting AutomateOS in Docker..."

# Set production environment
export ENVIRONMENT=production
export DEBUG=false

# Wait for database to be ready
echo "Waiting for database to be ready..."
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

# Run database migrations
echo "Running database migrations..."
python -m app.migrations

# Start the application based on the process type
if [ "$PROCESS_TYPE" = "worker" ]; then
    echo "Starting background worker..."
    exec python worker.py
else
    echo "Starting FastAPI web server..."
    exec uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}
fi
EOF

chmod +x build/start-docker.sh

# Copy configuration files
print_status "Copying configuration files..."
cp requirements.txt build/
cp redis.conf build/
cp worker.py build/
cp -r app build/
cp .env.example build/

# Create production requirements file (optimized)
cat > build/requirements-production.txt << 'EOF'
# Production-optimized requirements for AutomateOS
fastapi>=0.116.0
uvicorn[standard]>=0.35.0
pydantic>=2.11.0
python-dotenv>=1.0.0
sqlmodel>=0.0.22
python-jose[cryptography]>=3.3.0
passlib[bcrypt]>=1.7.4
python-multipart>=0.0.9
redis>=4.5.0,<5.0.0
rq>=1.10.0,<1.15.0
requests>=2.31.0
psycopg2-binary>=2.9.0
pydantic-settings>=2.0.0
gunicorn>=21.2.0
EOF

# Create deployment README
cat > build/README-DEPLOYMENT.md << 'EOF'
# AutomateOS Production Deployment

This directory contains the production build of AutomateOS.

## Quick Start

1. Set up environment variables:
   ```bash
   cp .env.example .env
   # Edit .env with your production settings
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements-production.txt
   ```

3. Start the application:
   ```bash
   ./start-production.sh
   ```

## Docker Deployment

Build and run with Docker:

```bash
# Build image
docker build -t automate-os .

# Run web server
docker run -e PROCESS_TYPE=web -p 8000:8000 automate-os

# Run worker
docker run -e PROCESS_TYPE=worker automate-os
```

## Environment Variables

See `.env.example` for all available configuration options.

## Health Checks

- Web server: `GET /`
- Queue status: `GET /queue/info`

## Monitoring

- Application logs are written to stdout
- Redis logs are in the Redis data directory
- Database logs depend on your database configuration
EOF

print_status "Production build completed successfully!"
print_status "Build artifacts are in the 'build' directory"
print_warning "Don't forget to:"
print_warning "  1. Copy .env.example to .env and configure for production"
print_warning "  2. Set up your PostgreSQL database"
print_warning "  3. Configure Redis connection"
print_warning "  4. Review security settings"

echo ""
echo "🎉 AutomateOS is ready for production deployment!"