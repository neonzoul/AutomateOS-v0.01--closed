# AutomateOS Deployment Checklist

Use this checklist to ensure a successful deployment to Render.com.

## Pre-Deployment Checklist

### 1. Code Preparation
- [ ] All code committed and pushed to GitHub main branch
- [ ] No sensitive data (passwords, keys) in code
- [ ] All dependencies listed in `requirements.txt`
- [ ] Frontend builds successfully with `npm run build:prod`
- [ ] Backend starts successfully with production settings

### 2. Environment Configuration
- [ ] Generate secure `SECRET_KEY` (64 characters)
- [ ] Prepare production environment variables
- [ ] Review CORS settings for production domain
- [ ] Verify database connection string format
- [ ] Confirm Redis connection string format

### 3. Testing
- [ ] Run local tests with production-like settings
- [ ] Test database migrations
- [ ] Verify frontend builds without errors
- [ ] Test API endpoints with production configuration
- [ ] Verify webhook functionality

## Render Deployment Steps

### 1. Database Setup
- [ ] Create PostgreSQL database on Render
- [ ] Note connection string
- [ ] Verify database is accessible

### 2. Redis Setup
- [ ] Create Redis instance on Render
- [ ] Note connection string
- [ ] Verify Redis is accessible

### 3. Web Service Deployment
- [ ] Create web service from GitHub repository
- [ ] Set build command: `./scripts/render-build.sh`
- [ ] Set start command: `./scripts/render-start.sh`
- [ ] Configure all environment variables
- [ ] Deploy and verify build succeeds

### 4. Worker Service Deployment
- [ ] Create background worker service
- [ ] Set build command: `pip install -r requirements.txt`
- [ ] Set start command: `RENDER_SERVICE_TYPE=worker ./scripts/render-start.sh`
- [ ] Configure same environment variables as web service
- [ ] Deploy and verify worker starts

## Post-Deployment Verification

### 1. Service Health
- [ ] Web service is running and accessible
- [ ] Background worker is running
- [ ] Database connection successful
- [ ] Redis connection successful
- [ ] Health check endpoint returns healthy status

### 2. Functionality Testing
- [ ] Homepage loads correctly
- [ ] User registration works
- [ ] User login works
- [ ] Dashboard displays correctly
- [ ] Workflow creation works
- [ ] Workflow execution works
- [ ] Webhook triggers work
- [ ] Execution logs display correctly

### 3. Performance Verification
- [ ] Page load times are acceptable
- [ ] API response times are reasonable
- [ ] Background jobs process within expected time
- [ ] No memory leaks or excessive resource usage

## Environment Variables Checklist

### Required Variables (Both Services)
- [ ] `ENVIRONMENT=production`
- [ ] `DEBUG=false`
- [ ] `SECRET_KEY=<64-character-key>`
- [ ] `DATABASE_URL=<postgresql-connection-string>`
- [ ] `REDIS_URL=<redis-connection-string>`
- [ ] `ALLOWED_ORIGINS=<your-render-domain>`

### Optional Variables
- [ ] `API_HOST=0.0.0.0`
- [ ] `WORKER_CONCURRENCY=4`
- [ ] `JOB_TIMEOUT=600`
- [ ] `LOG_LEVEL=INFO`
- [ ] `LOG_FORMAT=json`

### Worker-Specific Variables
- [ ] `RENDER_SERVICE_TYPE=worker` (for worker service only)

## Troubleshooting Checklist

### Build Issues
- [ ] Check build logs for specific errors
- [ ] Verify all dependencies are installed
- [ ] Ensure Node.js and Python versions are compatible
- [ ] Check file permissions on scripts

### Runtime Issues
- [ ] Check service logs for errors
- [ ] Verify environment variables are set correctly
- [ ] Test database and Redis connections
- [ ] Check for port conflicts

### Frontend Issues
- [ ] Verify static files are served correctly
- [ ] Check API base URL configuration
- [ ] Test CORS configuration
- [ ] Verify routing works for all pages

## Security Checklist

### Production Security
- [ ] Strong `SECRET_KEY` generated and set
- [ ] Database uses strong password
- [ ] Redis uses authentication if available
- [ ] CORS restricted to production domain only
- [ ] No debug information exposed in production
- [ ] HTTPS enabled (automatic on Render)

### Data Protection
- [ ] User passwords are properly hashed
- [ ] JWT tokens have appropriate expiration
- [ ] Sensitive data not logged
- [ ] Database backups configured

## Monitoring Setup

### Health Monitoring
- [ ] Health check endpoint configured
- [ ] Service monitoring enabled in Render
- [ ] Log aggregation configured
- [ ] Error tracking setup

### Performance Monitoring
- [ ] Response time monitoring
- [ ] Database performance monitoring
- [ ] Queue length monitoring
- [ ] Resource usage monitoring

## Backup and Recovery

### Data Backup
- [ ] Database backup strategy configured
- [ ] Redis persistence enabled
- [ ] Application code backed up in Git
- [ ] Environment variables documented securely

### Recovery Plan
- [ ] Database restore procedure documented
- [ ] Service restart procedure documented
- [ ] Rollback procedure documented
- [ ] Emergency contact information available

## Documentation

### User Documentation
- [ ] API documentation accessible
- [ ] User guide available
- [ ] Deployment guide updated
- [ ] Troubleshooting guide available

### Technical Documentation
- [ ] Architecture documented
- [ ] Environment setup documented
- [ ] Deployment process documented
- [ ] Monitoring procedures documented

## Final Verification

- [ ] All services running and healthy
- [ ] All functionality tested and working
- [ ] Performance meets requirements
- [ ] Security measures in place
- [ ] Monitoring configured
- [ ] Documentation complete
- [ ] Team notified of deployment
- [ ] Deployment marked as successful

## Post-Deployment Tasks

- [ ] Monitor services for first 24 hours
- [ ] Check error logs regularly
- [ ] Verify backup procedures
- [ ] Update team on any issues
- [ ] Schedule regular health checks
- [ ] Plan for future updates and maintenance

---

**Deployment Date**: ___________
**Deployed By**: ___________
**Version**: ___________
**Notes**: ___________