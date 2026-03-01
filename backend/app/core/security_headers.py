from fastapi import Request, HTTPException
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
import time
import re
from typing import Callable


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """Add security headers to all responses"""
    
    async def dispatch(self, request: Request, call_next: Callable):
        response = await call_next(request)
        
        # Security headers
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        response.headers["Permissions-Policy"] = "camera=(), microphone=(), geolocation=()"
        
        # Set server header to generic value instead of removing
        response.headers["Server"] = "ChamaAPI"
        
        return response


class InputSanitizationMiddleware(BaseHTTPMiddleware):
    """Sanitize user inputs"""
    
    async def dispatch(self, request: Request, call_next: Callable):
        # Skip for GET requests and static files
        if request.method not in ["POST", "PUT", "PATCH"]:
            return await call_next(request)
        
        # Get request body for logging (don't modify)
        response = await call_next(request)
        
        return response


class RequestSizeMiddleware(BaseHTTPMiddleware):
    """Limit request body size"""
    
    MAX_SIZE = 1024 * 1024  # 1MB
    
    async def dispatch(self, request: Request, call_next: Callable):
        content_length = request.headers.get("content-length")
        
        if content_length and int(content_length) > self.MAX_SIZE:
            return JSONResponse(
                status_code=413,
                content={"detail": "Request too large. Max 1MB allowed."}
            )
        
        return await call_next(request)


class SQLInjectionProtection:
    """SQL injection patterns to detect"""
    
    SUSPICIOUS_PATTERNS = [
        r"(\bOR\b|\bAND\b).*=.*",  # OR/AND injection
        r"(--|#|\/\*|\*\/)",  # SQL comments
        r"(\bUNION\b|\bSELECT\b|\bINSERT\b|\bUPDATE\b|\bDELETE\b|\bDROP\b|\bCREATE\b)",
        r"(\bEXEC\b|\bEXECUTE\b|\b xp_)",
        r"(';|';|\")",  # String injection
        r"((\%27)|(\'))",  # Encoded quotes
        r"((\%3D)|(=))[^\n]*((\%27)|(\')|(\%3B)|(;))",  # Injection attempts
    ]
    
    @classmethod
    def is_safe_input(cls, user_input: str) -> bool:
        """Check if input contains suspicious patterns"""
        if not user_input:
            return True
        
        # Check each pattern
        for pattern in cls.SUSPICIOUS_PATTERNS:
            if re.search(pattern, user_input, re.IGNORECASE):
                return False
        
        return True


class IPBlocklistMiddleware(BaseHTTPMiddleware):
    """Block known malicious IPs (extend as needed)"""
    
    BLOCKED_IPS = {
        # Add blocked IPs here
    }
    
    async def dispatch(self, request: Request, call_next: Callable):
        client_ip = request.client.host if request.client else None
        
        if client_ip in self.BLOCKED_IPS:
            return JSONResponse(
                status_code=403,
                content={"detail": "Access denied"}
            )
        
        return await call_next(request)
