#!/bin/bash

# Render Build Script for AutomateOS
# This script is executed during the Render build process

set -e  # Exit on any error

echo "🚀 Starting Render build for AutomateOS..."

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

print_status() {
    echo -e "${GREEN}✓${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}⚠${NC} $1"
}

print_error() {
    echo -e "${RED}✗${NC} $1"
}

# Check if we're in the correct directory
if [ ! -f "requirements.txt" ] || [ ! -d "frontend" ]; then
    print_error "Build script must be run from project root"
    exit 1
fi

# Install Python dependencies
print_status "Installing Python dependencies..."
pip install --no-cache-dir -r requirements.txt

# Check if Node.js is available
if ! command -v node &> /dev/null; then
    print_error "Node.js is not installed"
    exit 1
fi

if ! command -v npm &> /dev/null; then
    print_error "npm is not installed"
    exit 1
fi

# Build frontend
print_status "Building React frontend..."
cd frontend

# Install Node dependencies
print_status "Installing Node.js dependencies..."
npm ci --only=production

# Build frontend for production
print_status "Building frontend assets..."
npm run build:prod

# Verify build output
if [ ! -d "dist" ]; then
    print_error "Frontend build failed - dist directory not found"
    exit 1
fi

cd ..

# Create static directory and copy frontend build
print_status "Copying frontend assets..."
mkdir -p static
cp -r frontend/dist/* static/

# Verify static assets
if [ ! -f "static/index.html" ]; then
    print_error "Frontend assets not copied correctly"
    exit 1
fi

print_status "Build completed successfully!"
print_status "Frontend assets are in the 'static' directory"
print_status "Python dependencies are installed"

echo ""
echo "🎉 AutomateOS is ready for Render deployment!"