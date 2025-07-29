"""
Configuration management for AutomateOS application.

This module handles environment-based configuration for different deployment environments.
"""

import os
from typing import List
from pydantic_settings import BaseSettings
from pydantic import validator


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # Security Configuration
    secret_key: str = "fallback-secret-key-change-in-production"
    access_token_expire_minutes: int = 30
    algorithm: str = "HS256"
    
    # Database Configuration
    database_url: str = "sqlite:///database.db"
    
    # Redis Configuration
    redis_url: str = "redis://localhost:6379/0"
    
    # Application Configuration
    environment: str = "development"
    debug: bool = True
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    
    # CORS Configuration
    allowed_origins: str = "http://localhost:5173,http://localhost:3000"
    
    # Worker Configuration
    worker_concurrency: int = 4
    job_timeout: int = 300
    
    # Logging Configuration
    log_level: str = "INFO"
    log_format: str = "json"
    
    @validator('allowed_origins')
    def parse_cors_origins(cls, v):
        """Parse comma-separated CORS origins into a list."""
        if isinstance(v, str):
            return [origin.strip() for origin in v.split(',')]
        return v
    
    @property
    def is_production(self) -> bool:
        """Check if running in production environment."""
        return self.environment.lower() == "production"
    
    @property
    def is_development(self) -> bool:
        """Check if running in development environment."""
        return self.environment.lower() == "development"
    
    @property
    def database_echo(self) -> bool:
        """Enable SQL logging in development."""
        return self.is_development and self.debug
    
    class Config:
        env_file = ".env"
        case_sensitive = False


# Global settings instance
settings = Settings()