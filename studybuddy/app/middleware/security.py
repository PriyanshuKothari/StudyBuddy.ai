"""
Security middleware - Rate limiting, authentication, protection
"""

from fastapi import Request, HTTPException
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from collections import defaultdict
from datetime import datetime, timedelta
from typing import Dict
import time

class RateLimiter:
    def __init__(self):
        self.requests: Dict[str, list] = defaultdict(list)
        
    def is_allowed(self, identifier: str, max_requests: int = 30, window_seconds: int = 60) -> bool:
        """
        Check if request is allowed based on rate limit
        
        Args:
            identifier: IP address or API key
            max_requests: Max requests allowed in window
            window_seconds: Time window in seconds
            
        Returns:
            True if allowed, False if rate limited
        """
        
        now=time.time()
        window_start= now - window_seconds
        
        self.requests[identifier] = [
            req_time for req_time in self.requests[identifier]
            if req_time > window_start
        ]
        
        if len(self.requests[identifier]) >= max_requests:
            return False
        
        self.requests[identifier].append(now)
        return True
    
    def get_retry_after(self, identifier: str, window_seconds: int = 60) -> int:
        """Get seconds until rate limit resets"""
        if not self.requests[identifier]:
            return 0
        oldest_request = min(self.requests[identifier])
        retry_after = int(window_seconds - (time.time() - oldest_request))
        return max(0, retry_after)
rate_limiter = RateLimiter()

class RateLimitMiddleware(BaseHTTPMiddleware):
    """Middleware to enforce rate limits"""
    
    async def dispatch(self, request: Request, call_next):
        if request.url.path in ["/health", "/", "/docs", "/openapi.json", "/redoc"]:
            return await call_next(request)
        
        client_ip = request.client.host
        
        if not rate_limiter.is_allowed(client_ip, max_requests=30, window_seconds=60):
            retry_after = rate_limiter.get_retry_after(client_ip)
            return JSONResponse(
                status_code=429,
                content={
                    "error": "Rate limit exceeded",
                    "message": "Too many requests. Please try again later.",
                    "retry_after_seconds": retry_after
                },
                headers={"Retry-After": str(retry_after)}
            )
        
        response = await call_next(request)
        return response
VALID_API_KEYS = set()
def validate_api_key(api_key: str = None) -> bool:
    """
    Validate API key (optional - for future paid tiers)
    
    Args:
        api_key: API key from header
        
    Returns:
        True if valid or if validation is disabled
    """
    if not VALID_API_KEYS:
        return True
    return api_key in VALID_API_KEYS

class CircuitBreaker:
    """Circuit breaker pattern for Groq API calls"""
    
    def __init__(self, failure_threshold: int = 5, timeout_seconds: int = 60):
        self.failure_threshold = failure_threshold
        self.timeout_seconds = timeout_seconds
        self.failures = 0
        self.last_failure_time = None
        self.state = "CLOSED"  
    
    def call(self, func, *args, **kwargs):
        """
        Execute function with circuit breaker protection
        
        States:
        - CLOSED: Normal operation
        - OPEN: Too many failures, reject requests
        - HALF_OPEN: Testing if service recovered
        """
        
        if self.state == "OPEN":
            if time.time() - self.last_failure_time > self.timeout_seconds:
                self.state = "HALF_OPEN"
            else:
                raise Exception("Circuit breaker is OPEN - too many API failures")
        
        try:
            result = func(*args, **kwargs)
            
            if self.state == "HALF_OPEN":
                self.state = "CLOSED"
                self.failures = 0
            
            return result
            
        except Exception as e:
            self.failures += 1
            self.last_failure_time = time.time()
            
            if self.failures >= self.failure_threshold:
                self.state = "OPEN"
            
            raise e

groq_circuit_breaker = CircuitBreaker(failure_threshold=5, timeout_seconds=60)