# AutomateOS Render Deployment Guide

This guide walks you through deploying AutomateOS to Render.com, a modern cloud platform that provides easy deployment for web applications.

## Prerequisites

1. **GitHub Repository**: Your AutomateOS code must be in a GitHub repository
2. **Render Account**: Sign up at [render.com](https://render.com) (free tier available)
3. **Environment Secrets**: Generate secure values for production secrets

## Quick Deploy with Blueprint

The fastest way to deploy AutomateOS is using the Render Blueprint:

### 1. Deploy from Blueprint

1. Click this button to deploy: [![Deploy to Render](https://render.com/images/deploy-to-render-button.svg)](https://render.com/deploy?repo=https://github.com/yourusername/automate-os)

2. Or manually:
   - Go to [Render Dashboard](https://dashboard.render.com)
   - Click "New" → "Blueprint"
   - Connect your GitHub repository
   - Select the repository containing AutomateOS
   - Render will automatically detect the `render.yaml` file

### 2. Configure Environment Variables

The blueprint will prompt you to set these required variables:

- **SECRET_KEY**: Generate a secure 64-character key:
  ```bash
  openssl rand -hex 32
  ```

- **ALLOWED_ORIGINS**: Set to your Render web service URL:
  ```
  https://your-app-name.onrender.com
  ```

### 3. Deploy

Click "Apply" and Render will:
- Create PostgreSQL database
- Create Redis instance  
- Deploy web service
- Deploy background worker
- Set up all connections automatically

## Manual Deployment (Step by Step)

If you prefer manual setup or need custom configuration:

### Step 1: Create Database

1. Go to Render Dashboard → "New" → "PostgreSQL"
2. Configure:
   - **Name**: `automate-os-db`
   - **Database**: `automate_os`
   - **User**: `automate_user`
   - **Region**: Choose closest to your users
   - **Plan**: Starter (free) or higher
3. Click "Create Database"
4. Note the connection string for later

### Step 2: Create Redis Instance

1. Go to Render Dashboard → "New" → "Redis"
2. Configure:
   - **Name**: `automate-os-redis`
   - **Region**: Same as database
   - **Plan**: Starter (free) or higher
3. Click "Create Redis"
4. Note the connection string for later

### Step 3: Create Web Service

1. Go to Render Dashboard → "New" → "Web Service"
2. Connect your GitHub repository
3. Configure:
   - **Name**: `automate-os-web`
   - **Runtime**: `Python 3`
   - **Build Command**: `./scripts/render-build.sh`
   - **Start Command**: `./scripts/render-start.sh`
   - **Plan**: Starter or higher

4. Add Environment Variables:
   ```
   ENVIRONMENT=production
   DEBUG=false
   SECRET_KEY=your-64-character-secret-key
   DATABASE_URL=postgresql://user:pass@host/db
   REDIS_URL=redis://host:port
   ALLOWED_ORIGINS=https://your-app-name.onrender.com
   API_HOST=0.0.0.0
   WORKER_CONCURRENCY=4
   JOB_TIMEOUT=600
   LOG_LEVEL=INFO
   LOG_FORMAT=json
   ```

5. Click "Create Web Service"

### Step 4: Create Background Worker

1. Go to Render Dashboard → "New" → "Background Worker"
2. Connect same GitHub repository
3. Configure:
   - **Name**: `automate-os-worker`
   - **Runtime**: `Python 3`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `RENDER_SERVICE_TYPE=worker ./scripts/render-start.sh`
   - **Plan**: Starter or higher

4. Add same environment variables as web service, plus:
   ```
   RENDER_SERVICE_TYPE=worker
   ```

5. Click "Create Background Worker"

## Environment Variables Reference

### Required Variables

| Variable | Description | Example |
|----------|-------------|---------|
| `ENVIRONMENT` | Deployment environment | `production` |
| `DEBUG` | Enable debug mode | `false` |
| `SECRET_KEY` | JWT signing key (64 chars) | `abc123...` |
| `DATABASE_URL` | PostgreSQL connection | `postgresql://...` |
| `REDIS_URL` | Redis connection | `redis://...` |
| `ALLOWED_ORIGINS` | CORS allowed origins | `https://app.onrender.com` |

### Optional Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `API_HOST` | Server bind address | `0.0.0.0` |
| `WORKER_CONCURRENCY` | Worker processes | `4` |
| `JOB_TIMEOUT` | Job timeout (seconds) | `600` |
| `LOG_LEVEL` | Logging level | `INFO` |
| `LOG_FORMAT` | Log format | `json` |

## Deployment Process

### Build Process

1. **Install Dependencies**: Python packages from `requirements.txt`
2. **Build Frontend**: React app compiled to static assets
3. **Copy Assets**: Frontend build copied to `static/` directory
4. **Prepare Services**: Both web and worker services prepared

### Startup Process

1. **Health Checks**: Verify database and Redis connections
2. **Run Migrations**: Database schema updated (web service only)
3. **Start Services**: Web server and background workers started

### Service Architecture

```
┌─────────────────┐    ┌─────────────────┐
│   Web Service   │    │ Background      │
│                 │    │ Worker          │
│ FastAPI + React │    │                 │
│ Port: 10000     │    │ RQ Consumer     │
└─────────┬───────┘    └─────────┬───────┘
          │                      │
          └──────────┬───────────┘
                     │
          ┌──────────▼───────────┐
          │                      │
          │    PostgreSQL        │
          │    Database          │
          │                      │
          └──────────┬───────────┘
                     │
          ┌──────────▼───────────┐
          │                      │
          │    Redis Cache       │
          │    & Queue           │
          │                      │
          └──────────────────────┘
```

## Post-Deployment

### 1. Verify Deployment

Check that all services are running:

- **Web Service**: Visit your app URL
- **Database**: Check connection in web service logs
- **Redis**: Check connection in worker logs
- **Worker**: Verify background jobs are processing

### 2. Test Functionality

1. **Register Account**: Create a new user account
2. **Create Workflow**: Build a simple test workflow
3. **Test Webhook**: Trigger the workflow via webhook
4. **Check Logs**: Verify execution logs are created

### 3. Configure Domain (Optional)

1. Go to your web service settings
2. Add custom domain under "Custom Domains"
3. Update `ALLOWED_ORIGINS` environment variable
4. Configure DNS records as instructed

## Monitoring and Maintenance

### Logs

Access logs for debugging:
- **Web Service**: Render Dashboard → Web Service → Logs
- **Worker**: Render Dashboard → Background Worker → Logs
- **Database**: Render Dashboard → PostgreSQL → Logs

### Metrics

Monitor performance:
- **Response Times**: Web service metrics
- **Queue Length**: Redis queue monitoring
- **Database Performance**: PostgreSQL metrics
- **Error Rates**: Application logs

### Scaling

Scale services based on load:
- **Web Service**: Increase plan or add instances
- **Worker**: Add more background worker services
- **Database**: Upgrade to higher plan
- **Redis**: Upgrade to higher plan

## Troubleshooting

### Common Issues

1. **Build Failures**:
   - Check build logs for specific errors
   - Verify all dependencies are in `requirements.txt`
   - Ensure Node.js version compatibility

2. **Database Connection Errors**:
   - Verify `DATABASE_URL` format
   - Check database service status
   - Review connection limits

3. **Redis Connection Errors**:
   - Verify `REDIS_URL` format
   - Check Redis service status
   - Review memory limits

4. **Static Files Not Loading**:
   - Verify frontend build completed successfully
   - Check `static/` directory exists
   - Review CORS configuration

### Getting Help

- **Render Support**: [Render Community](https://community.render.com)
- **Application Logs**: Check service logs in Render Dashboard
- **GitHub Issues**: Report bugs in your repository

## Security Considerations

1. **Environment Variables**: Never commit secrets to Git
2. **HTTPS**: Render provides HTTPS by default
3. **Database Security**: Use strong passwords
4. **CORS Configuration**: Restrict to your domain only
5. **Regular Updates**: Keep dependencies updated

## Cost Optimization

### Free Tier Limits

Render's free tier includes:
- Web Service: 750 hours/month
- Background Worker: 750 hours/month
- PostgreSQL: 1GB storage
- Redis: 25MB memory

### Optimization Tips

1. **Sleep on Inactivity**: Free services sleep after 15 minutes
2. **Efficient Queries**: Optimize database queries
3. **Cache Strategy**: Use Redis effectively
4. **Log Retention**: Clean up old execution logs
5. **Resource Monitoring**: Monitor usage to avoid overages

This completes the Render deployment setup for AutomateOS. Your application will be accessible at `https://your-app-name.onrender.com` with full production capabilities including database persistence, background job processing, and automatic scaling.