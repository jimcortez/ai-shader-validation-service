"""
Development environment configuration
"""

from src.config.settings import Settings

class DevelopmentSettings(Settings):
    """Development settings"""
    
    debug: bool = True
    reload: bool = True
    log_level: str = "DEBUG"
    
    # Development database
    database_url: str = "sqlite:///./storage/shader_validator_dev.db"
    
    # Development storage
    storage_path: str = "./storage/dev"
    logs_path: str = "./logs/dev"
    cache_path: str = "./cache/dev"
    
    # Development security (less restrictive)
    secret_key: str = "dev-secret-key-change-in-production"
    allowed_origins: list = ["*"]
    
    # Development rate limiting (more permissive)
    rate_limit_per_minute: int = 1000
    
    # Development validation (more permissive)
    max_shader_size: int = 5 * 1024 * 1024  # 5MB
    max_batch_size: int = 50
    validation_timeout: int = 60  # seconds 