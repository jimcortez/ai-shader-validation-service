"""
Testing environment configuration
"""

from src.config.settings import Settings

class TestingSettings(Settings):
    """Testing settings"""
    
    debug: bool = True
    reload: bool = False
    log_level: str = "ERROR"
    
    # Testing database (in-memory)
    database_url: str = "sqlite:///:memory:"
    
    # Testing storage (temporary)
    storage_path: str = "./storage/test"
    logs_path: str = "./logs/test"
    cache_path: str = "./cache/test"
    
    # Testing security
    secret_key: str = "test-secret-key"
    allowed_origins: list = ["*"]
    
    # Testing rate limiting (permissive)
    rate_limit_per_minute: int = 10000
    
    # Testing validation (permissive)
    max_shader_size: int = 10 * 1024 * 1024  # 10MB
    max_batch_size: int = 100
    validation_timeout: int = 120  # seconds 