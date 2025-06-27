"""
Production environment configuration
"""

from src.config.settings import Settings

class ProductionSettings(Settings):
    """Production settings"""
    
    debug: bool = False
    reload: bool = False
    log_level: str = "WARNING"
    
    # Production database
    database_url: str = "sqlite:///./storage/shader_validator_prod.db"
    
    # Production storage
    storage_path: str = "./storage/prod"
    logs_path: str = "./logs/prod"
    cache_path: str = "./cache/prod"
    
    # Production security (more restrictive)
    secret_key: str = "CHANGE_THIS_IN_PRODUCTION"
    allowed_origins: list = ["https://yourdomain.com"]
    
    # Production rate limiting (more restrictive)
    rate_limit_per_minute: int = 100
    
    # Production validation (more restrictive)
    max_shader_size: int = 1024 * 1024  # 1MB
    max_batch_size: int = 10
    validation_timeout: int = 30  # seconds 