-- AutomateOS Database Initialization Script
-- This script sets up the PostgreSQL database with proper configuration

-- Create database (if not exists)
-- Note: This is handled by the POSTGRES_DB environment variable in Docker

-- Set up database configuration for optimal performance
ALTER SYSTEM SET shared_preload_libraries = 'pg_stat_statements';
ALTER SYSTEM SET max_connections = 200;
ALTER SYSTEM SET shared_buffers = '256MB';
ALTER SYSTEM SET effective_cache_size = '1GB';
ALTER SYSTEM SET maintenance_work_mem = '64MB';
ALTER SYSTEM SET checkpoint_completion_target = 0.9;
ALTER SYSTEM SET wal_buffers = '16MB';
ALTER SYSTEM SET default_statistics_target = 100;
ALTER SYSTEM SET random_page_cost = 1.1;
ALTER SYSTEM SET effective_io_concurrency = 200;

-- Enable pg_stat_statements extension for query monitoring
CREATE EXTENSION IF NOT EXISTS pg_stat_statements;

-- Create indexes that will be used by the application
-- Note: The actual tables will be created by SQLModel/Alembic migrations

-- Grant necessary permissions to the application user
GRANT ALL PRIVILEGES ON DATABASE automate_os TO automate_user;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO automate_user;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO automate_user;

-- Set default privileges for future tables
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON TABLES TO automate_user;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON SEQUENCES TO automate_user;