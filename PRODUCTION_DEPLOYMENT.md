# AutomateOS Production Deployment Guide

This guide covers deploying AutomateOS to production environments including Render, Docker, and traditional VPS deployments.

## Quick Start

### 1. Environment Configuration

Copy the example environment file and configure for production:

```bash
cp .env.example .env
```

Edit `.env` with your production settings:

```bash
# Production Configuration
ENVIRONMENT=production
DEBUG=false
SECRET_KEY=your-64-character-secret-key-here
DATABASE_URL=postgresql://user:password@host:5432/automate_os
REDIS_URL=redis://:password@host:6379/0
ALLOWED_ORIGINS=https://yourdomain.com
API_HOST=0.0.0.0
API_PORT=8000
```

### 2. Build for Production

Run the production build script:

```bash
./scripts/build-production.sh
```

This creates a `build/` directory with all production assets.

### 3. Deploy

Choose your deployment method:

- [Render Deployment](#render-deployment)
- [Docker Deployment](#docker-deployment)
- [Traditional VPS](#traditional-vps-deployment)

## Render Deployment

Render is the recommended platform for easy production deployment.

### Prerequisites

1. GitHub repository with your AutomateOS code
2. Render account (free tier available)

### Services Setup

#### 1. PostgreSQL Database

1. Go to Render Dashboard → New → PostgreSQL
2. Configure:
   - Name: `automate-os-db`
   - Database: `automate_os`
   - User: `automate_user`
   - Region: Choose closest to your users
3. Note the connection details for later

#### 2. Redis Instance

1. Go to Render Dashboard → New → Redis
2. Configure:
   - Name: `automate-os-redis`
   - Region: Same as database
3. Note the connection URL

#### 3. Web Service

1. Go to Render Dashboard → New → Web Service
2. Connect your GitHub repository
3. Configure:
   - Name: `automate-os-web`
   - Environment: `Docker`
   - Build Command: `docker build -t automate-os .`
   - Start Command: `./start.sh`
4. Add environment variables:
   ```
   ENVIRONMENT=production
   DEBUG=false
   SECRET_KEY=your-secret-key
   DATABASE_URL=postgresql://user:pass@host/db
   REDIS_URL=redis://host:port
   ALLOWED_ORIGINS=https://your-app.onrender.com
   PROCESS_TYPE=web
   ```

#### 4. Background Worker

1. Go to Render Dashboard → New → Background Worker
2. Connect same GitHub repository
3. Configure:
   - Name: `automate-os-worker`
   - Environment: `Docker`
   - Build Command: `docker build -t automate-os .`
   - Start Command: `./start.sh`
4. Add same environment variables as web service, but set:
   ```
   PROCESS_TYPE=worker
   ```

### Deployment

1. Push your code to GitHub
2. Render will automatically build and deploy
3. Monitor logs for any issues
4. Test your deployment at the provided URL

## Docker Deployment

### Local Production Testing

Test the production setup locally:

```bash
# Build and start all services
docker-compose -f docker-compose.production.yml up --build

# Access the application
open http://localhost:8000
```

### Production Docker Deployment

1. Build the image:
   ```bash
   docker build -t automate-os .
   ```

2. Set up external services (PostgreSQL, Redis)

3. Run the web service:
   ```bash
   docker run -d \
     --name automate-os-web \
     -p 8000:8000 \
     -e ENVIRONMENT=production \
     -e DATABASE_URL=postgresql://... \
     -e REDIS_URL=redis://... \
     -e SECRET_KEY=your-secret \
     -e PROCESS_TYPE=web \
     automate-os
   ```

4. Run the worker:
   ```bash
   docker run -d \
     --name automate-os-worker \
     -e ENVIRONMENT=production \
     -e DATABASE_URL=postgresql://... \
     -e REDIS_URL=redis://... \
     -e SECRET_KEY=your-secret \
     -e PROCESS_TYPE=worker \
     automate-os
   ```

## Traditional VPS Deployment

### Prerequisites

- Ubuntu 20.04+ or similar Linux distribution
- Python 3.11+
- Node.js 18+
- PostgreSQL 13+
- Redis 6+

### Setup Steps

1. **Install dependencies:**
   ```bash
   sudo apt update
   sudo apt install python3.11 python3.11-venv nodejs npm postgresql redis-server nginx
   ```

2. **Clone and setup:**
   ```bash
   git clone https://github.com/yourusername/automate-os.git
   cd automate-os
   python3.11 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```

3. **Configure database:**
   ```bash
   sudo -u postgres createuser automate_user
   sudo -u postgres createdb automate_os -O automate_user
   sudo -u postgres psql -c "ALTER USER automate_user PASSWORD 'your_password';"
   ```

4. **Configure environment:**
   ```bash
   cp .env.example .env
   # Edit .env with your production settings
   ```

5. **Build frontend:**
   ```bash
   cd frontend
   npm install
   npm run build:prod
   cd ..
   ```

6. **Run migrations:**
   ```bash
   python -m app.migrations
   ```

7. **Start services:**
   ```bash
   # Start with production script
   python start_production.py
   
   # Or use systemd services (recommended)
   sudo cp deploy/automate-os-web.service /etc/systemd/system/
   sudo cp deploy/automate-os-worker.service /etc/systemd/system/
   sudo systemctl enable automate-os-web automate-os-worker
   sudo systemctl start automate-os-web automate-os-worker
   ```

## Environment Variables Reference

| Variable | Description | Default | Required |
|----------|-------------|---------|----------|
| `ENVIRONMENT` | Deployment environment | `development` | Yes |
| `DEBUG` | Enable debug mode | `true` | No |
| `SECRET_KEY` | JWT signing key | - | Yes |
| `DATABASE_URL` | PostgreSQL connection URL | SQLite | Yes (prod) |
| `REDIS_URL` | Redis connection URL | `redis://localhost:6379/0` | Yes |
| `ALLOWED_ORIGINS` | CORS allowed origins | localhost URLs | Yes |
| `API_HOST` | Server bind address | `0.0.0.0` | No |
| `API_PORT` | Server port | `8000` | No |
| `WORKER_CONCURRENCY` | Worker processes | `4` | No |
| `JOB_TIMEOUT` | Job timeout (seconds) | `300` | No |
| `LOG_LEVEL` | Logging level | `INFO` | No |

## Monitoring and Maintenance

### Health Checks

- Web service: `GET /`
- Queue status: `GET /queue/info`
- Database: Check connection in logs

### Log Management

- Application logs: stdout/stderr
- Database logs: PostgreSQL logs
- Redis logs: Redis logs
- Worker logs: RQ worker logs

### Backup Strategy

1. **Database backups:**
   ```bash
   pg_dump automate_os > backup_$(date +%Y%m%d).sql
   ```

2. **Redis backups:**
   ```bash
   redis-cli BGSAVE
   cp /var/lib/redis/dump.rdb backup_redis_$(date +%Y%m%d).rdb
   ```

### Scaling

- **Horizontal scaling:** Add more worker instances
- **Vertical scaling:** Increase server resources
- **Database scaling:** Use read replicas for heavy read workloads

## Troubleshooting

### Common Issues

1. **Database connection errors:**
   - Check DATABASE_URL format
   - Verify database server is running
   - Check firewall settings

2. **Redis connection errors:**
   - Verify Redis server is running
   - Check REDIS_URL format
   - Verify authentication if enabled

3. **Worker not processing jobs:**
   - Check worker logs
   - Verify Redis connection
   - Check job queue status

4. **CORS errors:**
   - Update ALLOWED_ORIGINS
   - Check frontend build configuration

### Getting Help

- Check application logs
- Review this deployment guide
- Check GitHub issues
- Contact support

## Security Considerations

1. **Use strong SECRET_KEY** (64+ characters)
2. **Enable database authentication**
3. **Use Redis authentication**
4. **Configure HTTPS** (use reverse proxy like nginx)
5. **Regular security updates**
6. **Monitor access logs**
7. **Use environment variables** for secrets
8. **Regular backups**

## Performance Optimization

1. **Database indexing** (handled by migrations)
2. **Redis persistence** configuration
3. **Worker scaling** based on load
4. **CDN** for static assets
5. **Database connection pooling**
6. **Monitoring** and alerting

This completes the production deployment configuration for AutomateOS!