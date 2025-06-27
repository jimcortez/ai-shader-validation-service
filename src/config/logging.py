"""
Logging configuration
"""

import logging
import logging.handlers
import os
from datetime import datetime
from typing import Optional

def setup_logging(
    log_level: str = "INFO",
    log_format: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    log_file: Optional[str] = None
) -> logging.Logger:
    """Setup application logging"""
    
    # Create logs directory if it doesn't exist
    if log_file:
        os.makedirs(os.path.dirname(log_file), exist_ok=True)
    
    # Configure root logger
    logging.basicConfig(
        level=getattr(logging, log_level.upper()),
        format=log_format,
        handlers=[
            logging.StreamHandler(),  # Console handler
            logging.handlers.RotatingFileHandler(
                log_file or f"logs/app_{datetime.now().strftime('%Y%m%d')}.log",
                maxBytes=10*1024*1024,  # 10MB
                backupCount=5
            ) if log_file else logging.NullHandler()
        ]
    )
    
    # Set specific loggers
    logging.getLogger("uvicorn").setLevel(logging.INFO)
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
    logging.getLogger("sqlalchemy").setLevel(logging.WARNING)
    
    # Create logger for this application
    logger = logging.getLogger("ai_shader_validator")
    logger.setLevel(getattr(logging, log_level.upper()))
    
    return logger

def get_logger(name: str) -> logging.Logger:
    """Get a logger instance"""
    return logging.getLogger(f"ai_shader_validator.{name}") 