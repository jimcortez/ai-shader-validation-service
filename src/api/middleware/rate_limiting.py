"""
Rate limiting middleware
"""

from fastapi import Request, HTTPException, status
import time
from collections import defaultdict
from typing import Dict, Tuple
from src.config.settings import settings

class RateLimitMiddleware:
    """Rate limiting middleware for API endpoints"""
    
    def __init__(self, app):
        self.app = app
        self.requests: Dict[str, list] = defaultdict(list)
        self.rate_limit = settings.rate_limit_per_minute
        self.window_size = 60  # 1 minute window
    
    async def __call__(self, scope, receive, send):
        """ASGI callable"""
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return
        
        request = Request(scope, receive)
        
        # Get client identifier (IP address for now)
        client_id = self._get_client_id(request)
        
        # Check rate limit
        if not self._is_allowed(client_id):
            # Create rate limit response
            response_data = {
                "error": "Rate Limit Exceeded",
                "detail": f"Rate limit exceeded. Maximum {self.rate_limit} requests per minute.",
                "code": "RATE_LIMIT_EXCEEDED",
                "timestamp": time.time()
            }
            
            await send({
                "type": "http.response.start",
                "status": 429,
                "headers": [
                    (b"content-type", b"application/json"),
                    (b"retry-after", b"60")
                ]
            })
            
            import json
            await send({
                "type": "http.response.body",
                "body": json.dumps(response_data).encode()
            })
            return
        
        # Add request to tracking
        self._add_request(client_id)
        
        await self.app(scope, receive, send)
    
    def _get_client_id(self, request: Request) -> str:
        """Get client identifier (IP address)"""
        # Get real IP if behind proxy
        forwarded_for = request.headers.get("X-Forwarded-For")
        if forwarded_for:
            return forwarded_for.split(",")[0].strip()
        
        return request.client.host if request.client else "unknown"
    
    def _is_allowed(self, client_id: str) -> bool:
        """Check if client is within rate limit"""
        now = time.time()
        window_start = now - self.window_size
        
        # Clean old requests
        self.requests[client_id] = [
            req_time for req_time in self.requests[client_id]
            if req_time > window_start
        ]
        
        # Check if within limit
        return len(self.requests[client_id]) < self.rate_limit
    
    def _add_request(self, client_id: str):
        """Add a request to the tracking"""
        self.requests[client_id].append(time.time()) 