"""
Request logging middleware
"""

from fastapi import Request, Response
import time
import logging
from typing import Callable
from src.config.logging import get_logger

logger = get_logger("api.middleware")

class LoggingMiddleware:
    """Request logging middleware for API endpoints"""
    
    def __init__(self, app):
        self.app = app
    
    async def __call__(self, scope, receive, send):
        """ASGI callable"""
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return
        
        request = Request(scope, receive)
        
        # Start time
        start_time = time.time()
        
        # Log request
        logger.info(
            f"Request started: {request.method} {request.url.path} "
            f"from {request.client.host if request.client else 'unknown'}"
        )
        
        # Process request
        try:
            # Create a custom send function to capture response
            async def custom_send(message):
                if message["type"] == "http.response.start":
                    # Add response time header
                    message["headers"].append((b"x-response-time", f"{time.time() - start_time:.3f}s".encode()))
                await send(message)
            
            await self.app(scope, receive, custom_send)
            
            # Calculate duration
            duration = time.time() - start_time
            
            # Log successful response
            logger.info(
                f"Request completed: {request.method} {request.url.path} "
                f"in {duration:.3f}s"
            )
            
        except Exception as e:
            # Calculate duration
            duration = time.time() - start_time
            
            # Log error
            logger.error(
                f"Request failed: {request.method} {request.url.path} "
                f"-> {type(e).__name__}: {str(e)} in {duration:.3f}s"
            )
            
            # Re-raise the exception
            raise 