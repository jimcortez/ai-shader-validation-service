"""
Security Middleware

This module provides security middleware for input sanitization,
malicious code detection, and access control.
"""

import logging
import re
import hashlib
import time
from typing import Dict, Any, Optional, List
from fastapi import Request, HTTPException, status
from fastapi.responses import JSONResponse
import json

logger = logging.getLogger(__name__)


class SecurityMiddleware:
    """
    Security middleware for request validation and sanitization.
    
    This middleware provides comprehensive security measures including
    input sanitization, malicious code detection, and access control.
    """
    
    def __init__(self):
        """Initialize the security middleware."""
        self.malicious_patterns = self._load_malicious_patterns()
        self.allowed_content_types = [
            'application/json',
            'text/plain',
            'application/x-www-form-urlencoded'
        ]
        self.max_request_size = 10 * 1024 * 1024  # 10MB
        self.max_shader_size = 1024 * 1024  # 1MB
        self.blocked_ips = set()
        self.suspicious_ips = {}
    
    async def __call__(self, request: Request, call_next):
        """Process the request through security checks."""
        try:
            # Check IP address
            if not self._check_ip_address(request):
                return JSONResponse(
                    status_code=status.HTTP_403_FORBIDDEN,
                    content={"error": "Access denied"}
                )
            
            # Check request size
            if not self._check_request_size(request):
                return JSONResponse(
                    status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                    content={"error": "Request too large"}
                )
            
            # Check content type
            if not self._check_content_type(request):
                return JSONResponse(
                    status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
                    content={"error": "Unsupported content type"}
                )
            
            # Sanitize request body
            sanitized_body = await self._sanitize_request_body(request)
            if sanitized_body is None:
                return JSONResponse(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    content={"error": "Invalid request content"}
                )
            
            # Check for malicious content
            if self._detect_malicious_content(sanitized_body):
                self._log_suspicious_activity(request, "malicious_content")
                return JSONResponse(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    content={"error": "Malicious content detected"}
                )
            
            # Process request
            response = await call_next(request)
            
            # Add security headers
            response.headers["X-Content-Type-Options"] = "nosniff"
            response.headers["X-Frame-Options"] = "DENY"
            response.headers["X-XSS-Protection"] = "1; mode=block"
            response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
            response.headers["Content-Security-Policy"] = "default-src 'self'"
            
            return response
            
        except Exception as e:
            logger.error(f"Security middleware error: {e}")
            return JSONResponse(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                content={"error": "Internal server error"}
            )
    
    def _check_ip_address(self, request: Request) -> bool:
        """Check if IP address is allowed."""
        client_ip = request.client.host
        
        # Check if IP is blocked
        if client_ip in self.blocked_ips:
            logger.warning(f"Blocked IP attempted access: {client_ip}")
            return False
        
        # Check for suspicious activity
        if client_ip in self.suspicious_ips:
            suspicious_count = self.suspicious_ips[client_ip]['count']
            last_attempt = self.suspicious_ips[client_ip]['last_attempt']
            
            # If too many suspicious activities, block IP
            if suspicious_count > 10 and time.time() - last_attempt < 3600:
                self.blocked_ips.add(client_ip)
                logger.warning(f"IP blocked due to suspicious activity: {client_ip}")
                return False
        
        return True
    
    def _check_request_size(self, request: Request) -> bool:
        """Check if request size is within limits."""
        content_length = request.headers.get("content-length")
        if content_length:
            size = int(content_length)
            if size > self.max_request_size:
                logger.warning(f"Request too large: {size} bytes")
                return False
        
        return True
    
    def _check_content_type(self, request: Request) -> bool:
        """Check if content type is allowed."""
        content_type = request.headers.get("content-type", "")
        
        # Extract base content type
        base_type = content_type.split(";")[0].strip()
        
        return base_type in self.allowed_content_types
    
    async def _sanitize_request_body(self, request: Request) -> Optional[Dict[str, Any]]:
        """Sanitize and validate request body."""
        try:
            # Read request body
            body = await request.body()
            
            if not body:
                return {}
            
            # Check shader size for validation endpoints
            if "/api/v1/validate" in request.url.path:
                if len(body) > self.max_shader_size:
                    logger.warning(f"Shader too large: {len(body)} bytes")
                    return None
            
            # Parse JSON
            try:
                data = json.loads(body.decode('utf-8'))
            except json.JSONDecodeError:
                logger.warning("Invalid JSON in request body")
                return None
            
            # Sanitize the data
            sanitized_data = self._sanitize_data(data)
            
            return sanitized_data
            
        except Exception as e:
            logger.error(f"Error sanitizing request body: {e}")
            return None
    
    def _sanitize_data(self, data: Any) -> Any:
        """Recursively sanitize data structure."""
        if isinstance(data, dict):
            return {k: self._sanitize_data(v) for k, v in data.items()}
        elif isinstance(data, list):
            return [self._sanitize_data(item) for item in data]
        elif isinstance(data, str):
            return self._sanitize_string(data)
        else:
            return data
    
    def _sanitize_string(self, value: str) -> str:
        """Sanitize a string value."""
        # Remove null bytes
        value = value.replace('\x00', '')
        
        # Remove control characters except newlines and tabs
        value = re.sub(r'[\x00-\x08\x0B\x0C\x0E-\x1F\x7F]', '', value)
        
        # Normalize whitespace
        value = re.sub(r'\s+', ' ', value)
        
        # Limit length
        if len(value) > 10000:  # 10KB limit for strings
            value = value[:10000]
        
        return value.strip()
    
    def _detect_malicious_content(self, data: Any) -> bool:
        """Detect malicious content in data."""
        if isinstance(data, dict):
            return any(self._detect_malicious_content(v) for v in data.values())
        elif isinstance(data, list):
            return any(self._detect_malicious_content(item) for item in data)
        elif isinstance(data, str):
            return self._check_malicious_patterns(data)
        else:
            return False
    
    def _check_malicious_patterns(self, content: str) -> bool:
        """Check content against malicious patterns."""
        content_lower = content.lower()
        
        for pattern_name, pattern_info in self.malicious_patterns.items():
            pattern = pattern_info['pattern']
            if re.search(pattern, content_lower, re.IGNORECASE):
                logger.warning(f"Malicious pattern detected: {pattern_name}")
                return True
        
        return False
    
    def _log_suspicious_activity(self, request: Request, activity_type: str):
        """Log suspicious activity."""
        client_ip = request.client.host
        
        if client_ip not in self.suspicious_ips:
            self.suspicious_ips[client_ip] = {
                'count': 0,
                'last_attempt': time.time(),
                'activities': []
            }
        
        self.suspicious_ips[client_ip]['count'] += 1
        self.suspicious_ips[client_ip]['last_attempt'] = time.time()
        self.suspicious_ips[client_ip]['activities'].append({
            'type': activity_type,
            'timestamp': time.time(),
            'path': request.url.path,
            'method': request.method
        })
        
        logger.warning(f"Suspicious activity from {client_ip}: {activity_type}")
    
    def _load_malicious_patterns(self) -> Dict[str, Dict[str, Any]]:
        """Load malicious code patterns."""
        return {
            'sql_injection': {
                'pattern': r'(union|select|insert|update|delete|drop|create|alter)\s+.*\s+from\s+',
                'severity': 'high'
            },
            'xss_script': {
                'pattern': r'<script[^>]*>.*?</script>|<script[^>]*>',
                'severity': 'high'
            },
            'command_injection': {
                'pattern': r'(\||&|;|`|\$\(|eval\s*\(|exec\s*\()',
                'severity': 'high'
            },
            'path_traversal': {
                'pattern': r'\.\./|\.\.\\|%2e%2e%2f|%2e%2e%5c',
                'severity': 'medium'
            },
            'malicious_glsl': {
                'pattern': r'(discard\s*;|gl_FragColor\s*=|gl_FragData\s*\[)',
                'severity': 'low'
            },
            'suspicious_functions': {
                'pattern': r'(system|exec|eval|shell_exec|passthru|proc_open)',
                'severity': 'high'
            }
        }
    
    def get_security_stats(self) -> Dict[str, Any]:
        """Get security statistics."""
        return {
            'blocked_ips': len(self.blocked_ips),
            'suspicious_ips': len(self.suspicious_ips),
            'malicious_patterns': len(self.malicious_patterns),
            'max_request_size': self.max_request_size,
            'max_shader_size': self.max_shader_size,
            'timestamp': time.time()
        }
    
    def unblock_ip(self, ip: str):
        """Unblock an IP address."""
        if ip in self.blocked_ips:
            self.blocked_ips.remove(ip)
            logger.info(f"IP unblocked: {ip}")
    
    def clear_suspicious_activity(self, ip: str):
        """Clear suspicious activity for an IP."""
        if ip in self.suspicious_ips:
            del self.suspicious_ips[ip]
            logger.info(f"Suspicious activity cleared for IP: {ip}")


# Global security middleware instance
security_middleware = SecurityMiddleware() 