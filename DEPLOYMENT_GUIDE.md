# AutomateOS Deployment Guide

This guide covers how to deploy AutomateOS in various environments, from local development to production.

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Local Development Setup](#local-development-setup)
3. [Production Deployment](#production-deployment)
4. [Environment Variables](#environment-variables)
5. [Database Setup](#database-setup)
6. [Redis Configuration](#redis-configuration)
7. [Troubleshooting](#troubleshooting)

## Prerequisites

### System Requirements

- **Python**: 3.9 or higher
- **Node.js**: 18 or higher
- **npm**: 8 or higher
- **Database**: PostgreSQL 12+ (production) or SQLite (development)
- **Redis**: 6.0 or higher
- **Operating System**: Linux, macOS, or Windows

### Required Tools

- Git
- Docker (optional, for containerized deployment)
- A text editor or IDE

## Local Development Setup

### 1. Clone the Repository

```bash
git clone https://github.com/your-username/automate-os.git
cd automate-os
```

### 2. Backend Setup

#### Install Python Dependencies

```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

#### Environment Configuration

Create a `.env` file in the root directory:

```bash
cp .env.example .env
```

Edit `.env` with your local settings:

```env
# Environment
ENVIRONMENT=development

# Database (SQLite for development)
DATABASE_URL=sqlite:///./database.db

# Redis
REDIS_URL=redis://localhost:6379/0

# Security
SECRET_KEY=your-super-secret-key-change-this-in-production
ACCESS_TOKEN_EXPIRE_MINUTES=30

# CORS (for development)
ALLOWED_ORIGINS=http://localhost:3000,http://127.0.0.1:3000
```

#### Start Redis

```bash
# Install Redis (if not already installed)
# On macOS with Homebrew:
brew install redis
brew services start redis

# On Ubuntu/Debian:
sudo apt-get install redis-server
sudo systemctl start redis-server

# On Windows:
# Download and install Redis from https://redis.io/download
```

#### Initialize Database

```bash
# Run database migrations
python -c "from app.database import create_db_and_tables; create_db_and_tables()"
```

#### Start Backend Server

```bash
# Start the FastAPI server
python start_server.py

# Or use uvicorn directly:
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

#### Start Background Worker

In a separate terminal:

```bash
# Activate virtual environment
source venv/bin/activate  # or venv\Scripts\activate on Windows

# Start the worker
python start_worker.py
```

### 3. Frontend Setup

#### Install Dependencies

```bash
cd frontend
npm install
```

#### Environment Configuration

Create `frontend/.env.development`:

```env
VITE_API_BASE_URL=http://localhost:8000
```

#### Start Development Server

```bash
npm run dev
```

### 4. Verify Installation

1. **Backend API**: Visit http://localhost:8000/docs to see the API documentation
2. **Frontend**: Visit http://localhost:3000 to access the web interface
3. **Health Check**: Visit http://localhost:8000/health to verify all services are running

## Production Deployment

### Option 1: Render Deployment (Recommended)

AutomateOS is optimized for deployment on Render.com.

#### 1. Prepare Your Repository

Ensure your code is pushed to GitHub with all necessary files:

- `render.yaml` (service configuration)
- `requirements.txt` (Python dependencies)
- `scripts/render-build.sh` (build script)
- `scripts/render-start.sh` (start script)

#### 2. Create Render Services

1. **Web Service** (FastAPI + React):
   - Connect your GitHub repository
   - Use `scripts/render-build.sh` as build command
   - Use `scripts/render-start.sh` as start command
   - Set environment variables (see below)

2. **Background Worker**:
   - Connect the same repository
   - Use `python start_worker.py` as start command
   - Set the same environment variables

3. **PostgreSQL Database**:
   - Create a PostgreSQL service
   - Note the connection details

4. **Redis Instance**:
   - Create a Redis service
   - Note the connection URL

#### 3. Environment Variables for Render

Set these in your Render service settings:

```env
ENVIRONMENT=production
DATABASE_URL=postgresql://user:password@host:port/database
REDIS_URL=redis://host:port
SECRET_KEY=your-production-secret-key
ACCESS_TOKEN_EXPIRE_MINUTES=30
ALLOWED_ORIGINS=https://your-app-name.onrender.com
```

### Option 2: Docker Deployment

#### 1. Build Docker Image

```bash
# Build the image
docker build -t automate-os .

# Or use docker-compose
docker-compose -f docker-compose.production.yml up --build
```

#### 2. Environment Configuration

Create a `docker-compose.production.yml` file:

```yaml
version: '3.8'

services:
  web:
    build: .
    ports:
      - "8000:8000"
    environment:
      - ENVIRONMENT=production
      - DATABASE_URL=postgresql://user:password@db:5432/automate_os
      - REDIS_URL=redis://redis:6379/0
      - SECRET_KEY=your-production-secret-key
    depends_on:
      - db
      - redis

  worker:
    build: .
    command: python start_worker.py
    environment:
      - ENVIRONMENT=production
      - DATABASE_URL=postgresql://user:password@db:5432/automate_os
      - REDIS_URL=redis://redis:6379/0
    depends_on:
      - db
      - redis

  db:
    image: postgres:14
    environment:
      - POSTGRES_DB=automate_os
      - POSTGRES_USER=user
      - POSTGRES_PASSWORD=password
    volumes:
      - postgres_data:/var/lib/postgresql/data

  redis:
    image: redis:7-alpine
    volumes:
      - redis_data:/data

volumes:
  postgres_data:
  redis_data:
```

### Option 3: Manual Server Deployment

#### 1. Server Setup

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install Python, Node.js, PostgreSQL, Redis
sudo apt install python3 python3-pip python3-venv nodejs npm postgresql redis-server

# Install nginx (for reverse proxy)
sudo apt install nginx
```

#### 2. Application Setup

```bash
# Clone repository
git clone https://github.com/your-username/automate-os.git
cd automate-os

# Setup Python environment
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Build frontend
cd frontend
npm install
npm run build
cd ..
```

#### 3. Database Setup

```bash
# Create database and user
sudo -u postgres psql
CREATE DATABASE automate_os;
CREATE USER automate_user WITH PASSWORD 'your_password';
GRANT ALL PRIVILEGES ON DATABASE automate_os TO automate_user;
\q
```

#### 4. Process Management

Create systemd services for the application:

**`/etc/systemd/system/automate-os-web.service`**:
```ini
[Unit]
Description=AutomateOS Web Server
After=network.target

[Service]
Type=simple
User=www-data
WorkingDirectory=/path/to/automate-os
Environment=PATH=/path/to/automate-os/venv/bin
EnvironmentFile=/path/to/automate-os/.env
ExecStart=/path/to/automate-os/venv/bin/python start_production.py
Restart=always

[Install]
WantedBy=multi-user.target
```

**`/etc/systemd/system/automate-os-worker.service`**:
```ini
[Unit]
Description=AutomateOS Background Worker
After=network.target

[Service]
Type=simple
User=www-data
WorkingDirectory=/path/to/automate-os
Environment=PATH=/path/to/automate-os/venv/bin
EnvironmentFile=/path/to/automate-os/.env
ExecStart=/path/to/automate-os/venv/bin/python start_worker.py
Restart=always

[Install]
WantedBy=multi-user.target
```

#### 5. Nginx Configuration

**`/etc/nginx/sites-available/automate-os`**:
```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location /static/ {
        alias /path/to/automate-os/static/;
        expires 1y;
        add_header Cache-Control "public, immutable";
    }
}
```

#### 6. Start Services

```bash
# Enable and start services
sudo systemctl enable automate-os-web automate-os-worker
sudo systemctl start automate-os-web automate-os-worker

# Enable and restart nginx
sudo systemctl enable nginx
sudo ln -s /etc/nginx/sites-available/automate-os /etc/nginx/sites-enabled/
sudo systemctl restart nginx
```

## Environment Variables

### Required Variables

| Variable | Description | Example |
|----------|-------------|---------|
| `ENVIRONMENT` | Deployment environment | `development`, `production` |
| `DATABASE_URL` | Database connection string | `postgresql://user:pass@host:port/db` |
| `REDIS_URL` | Redis connection string | `redis://host:port/0` |
| `SECRET_KEY` | JWT signing key | `your-super-secret-key` |

### Optional Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `ACCESS_TOKEN_EXPIRE_MINUTES` | JWT token expiration | `30` |
| `ALLOWED_ORIGINS` | CORS allowed origins | `*` |
| `LOG_LEVEL` | Logging level | `INFO` |

### Generating Secret Keys

```bash
# Generate a secure secret key
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

## Database Setup

### Development (SQLite)

SQLite is used automatically in development. No additional setup required.

### Production (PostgreSQL)

#### Local PostgreSQL Setup

```bash
# Install PostgreSQL
sudo apt install postgresql postgresql-contrib

# Create database
sudo -u postgres createdb automate_os
sudo -u postgres createuser automate_user
sudo -u postgres psql -c "ALTER USER automate_user WITH PASSWORD 'your_password';"
sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE automate_os TO automate_user;"
```

#### Managed PostgreSQL (Render, AWS RDS, etc.)

1. Create a PostgreSQL instance
2. Note the connection details
3. Set `DATABASE_URL` environment variable

### Database Migrations

```bash
# Run migrations
python -c "from app.migrations import run_migrations; run_migrations()"
```

## Redis Configuration

### Development

```bash
# Install Redis locally
brew install redis  # macOS
sudo apt install redis-server  # Ubuntu

# Start Redis
redis-server
```

### Production

#### Managed Redis (Render, AWS ElastiCache, etc.)

1. Create a Redis instance
2. Note the connection URL
3. Set `REDIS_URL` environment variable

#### Self-hosted Redis

```bash
# Install Redis
sudo apt install redis-server

# Configure Redis for production
sudo nano /etc/redis/redis.conf

# Key settings:
# bind 127.0.0.1
# requirepass your_redis_password
# maxmemory 256mb
# maxmemory-policy allkeys-lru

# Restart Redis
sudo systemctl restart redis-server
```

## Troubleshooting

### Common Issues

#### 1. Database Connection Errors

**Symptoms**: `connection refused` or `authentication failed`

**Solutions**:
- Verify database is running: `pg_isready -h localhost -p 5432`
- Check connection string format
- Verify user permissions
- Check firewall settings

#### 2. Redis Connection Errors

**Symptoms**: `Connection refused` to Redis

**Solutions**:
- Verify Redis is running: `redis-cli ping`
- Check Redis configuration
- Verify `REDIS_URL` format
- Check network connectivity

#### 3. Frontend Build Errors

**Symptoms**: Build fails during deployment

**Solutions**:
- Verify Node.js version (18+)
- Clear npm cache: `npm cache clean --force`
- Delete `node_modules` and reinstall: `rm -rf node_modules && npm install`
- Check for TypeScript errors

#### 4. Worker Not Processing Jobs

**Symptoms**: Webhooks accepted but workflows don't execute

**Solutions**:
- Verify worker is running: `ps aux | grep start_worker`
- Check worker logs for errors
- Verify Redis connection from worker
- Check job queue status: `redis-cli LLEN rq:queue:default`

#### 5. CORS Errors

**Symptoms**: Frontend can't connect to API

**Solutions**:
- Verify `ALLOWED_ORIGINS` includes frontend URL
- Check API server is accessible
- Verify no proxy/firewall blocking requests

### Debugging Commands

```bash
# Check service status
systemctl status automate-os-web
systemctl status automate-os-worker

# View logs
journalctl -u automate-os-web -f
journalctl -u automate-os-worker -f

# Test database connection
python -c "from app.database import engine; print(engine.execute('SELECT 1').scalar())"

# Test Redis connection
redis-cli ping

# Check queue status
redis-cli LLEN rq:queue:default

# Test API health
curl http://localhost:8000/health
```

### Performance Optimization

#### Database Optimization

```sql
-- Add indexes for better performance
CREATE INDEX idx_workflows_owner_id ON workflows(owner_id);
CREATE INDEX idx_execution_logs_workflow_id ON execution_logs(workflow_id);
CREATE INDEX idx_execution_logs_started_at ON execution_logs(started_at);
```

#### Redis Optimization

```bash
# Monitor Redis performance
redis-cli --latency-history -i 1

# Check memory usage
redis-cli INFO memory
```

#### Application Monitoring

Consider adding monitoring tools:
- **Sentry**: Error tracking
- **Prometheus + Grafana**: Metrics and dashboards
- **New Relic**: Application performance monitoring

## Security Considerations

### Production Security Checklist

- [ ] Use strong, unique `SECRET_KEY`
- [ ] Enable HTTPS with SSL certificates
- [ ] Restrict `ALLOWED_ORIGINS` to your domain
- [ ] Use strong database passwords
- [ ] Enable Redis authentication
- [ ] Keep dependencies updated
- [ ] Use firewall to restrict access
- [ ] Regular security updates
- [ ] Monitor logs for suspicious activity
- [ ] Backup data regularly

### SSL/HTTPS Setup

For production deployments, always use HTTPS:

```bash
# Install Certbot for Let's Encrypt
sudo apt install certbot python3-certbot-nginx

# Get SSL certificate
sudo certbot --nginx -d your-domain.com

# Auto-renewal
sudo crontab -e
# Add: 0 12 * * * /usr/bin/certbot renew --quiet
```

## Backup and Recovery

### Database Backup

```bash
# Backup PostgreSQL
pg_dump -h localhost -U automate_user automate_os > backup.sql

# Restore PostgreSQL
psql -h localhost -U automate_user automate_os < backup.sql
```

### Redis Backup

```bash
# Redis automatically saves to dump.rdb
# Copy the file for backup
cp /var/lib/redis/dump.rdb /backup/location/
```

### Application Backup

```bash
# Backup application files
tar -czf automate-os-backup.tar.gz /path/to/automate-os
```

---

For additional help or questions, please refer to the [User Guide](USER_GUIDE.md) or check the API documentation at `/docs` when the server is running.