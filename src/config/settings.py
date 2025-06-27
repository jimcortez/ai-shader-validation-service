"""
Application settings configuration
"""

from pydantic_settings import BaseSettings
from typing import Optional, List
import os

class Settings(BaseSettings):
    """Application settings"""
    
    # Application
    app_name: str = "AI Shader Validation Tool"
    app_version: str = "1.0.0"
    debug: bool = False
    
    # Server
    host: str = "0.0.0.0"
    port: int = 8000
    reload: bool = True
    
    # Database - Use SQLite for development by default
    database_url: str = "sqlite:///./storage/shader_validator.db"
    
    # Storage
    storage_path: str = "./storage"
    logs_path: str = "./logs"
    cache_path: str = "./cache"
    
    # Security
    secret_key: str = "your-secret-key-change-in-production"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    
    # CORS
    allowed_origins: List[str] = ["*"]
    allowed_credentials: bool = True
    allowed_methods: List[str] = ["*"]
    allowed_headers: List[str] = ["*"]
    
    # Rate limiting
    rate_limit_per_minute: int = 100
    
    # Logging
    log_level: str = "INFO"
    log_format: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    
    # Validation
    max_shader_size: int = 1024 * 1024  # 1MB
    max_batch_size: int = 10
    validation_timeout: int = 30  # seconds
    
    # Rendering
    default_image_width: int = 512
    default_image_height: int = 512
    max_image_size: int = 2048
    
    # VVISF-GL
    vvisf_gl_path: Optional[str] = None
    enable_vvisf_gl: bool = True
    
    class Config:
        env_file = ".env"
        case_sensitive = False

# Create global settings instance
settings = Settings()

# Ensure directories exist
os.makedirs(settings.storage_path, exist_ok=True)
os.makedirs(settings.logs_path, exist_ok=True)
os.makedirs(settings.cache_path, exist_ok=True) 