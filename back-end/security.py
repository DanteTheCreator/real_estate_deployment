"""
Production security middleware and configuration
"""
import time
import redis
from fastapi import Request, HTTPException, status
from fastapi.responses import JSONResponse
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
import logging
from typing import Optional
import secrets
import hashlib
from config import settings

logger = logging.getLogger(__name__)

# Initialize Redis client for rate limiting and caching
if settings.rate_limit_enabled:
    try:
        redis_client = redis.from_url(settings.redis_url_with_auth)
        limiter = Limiter(
            key_func=get_remote_address,
            storage_uri=settings.redis_url_with_auth,
            default_limits=["1000/day", "100/hour"]
        )
    except Exception as e:
        logger.warning(f"Redis not available, using in-memory rate limiting: {e}")
        limiter = Limiter(key_func=get_remote_address)
else:
    limiter = None

class SecurityMiddleware:
    """Custom security middleware for production"""
    
    def __init__(self, app):
        self.app = app
        self.failed_login_attempts = {}  # In production, use Redis
        self.max_login_attempts = 5
        self.lockout_duration = 900  # 15 minutes
        
    async def __call__(self, scope, receive, send):
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return
            
        request = Request(scope, receive)
        
        # Security checks
        if not await self._check_security_headers(request):
            response = JSONResponse(
                status_code=400,
                content={"error": "Invalid request"}
            )
            await response(scope, receive, send)
            return
            
        # Check for suspicious patterns
        if await self._is_suspicious_request(request):
            response = JSONResponse(
                status_code=429,
                content={"error": "Request blocked"}
            )
            await response(scope, receive, send)
            return
            
        await self.app(scope, receive, send)
    
    async def _check_security_headers(self, request: Request) -> bool:
        """Check for required security headers in production, but allow HTTP from localhost and Docker network"""
        if not settings.is_production():
            return True

        # Allow HTTP from trusted internal sources
        trusted_hosts = {"127.0.0.1", "localhost", "::1", "172.20.0.1"}
        client_host = str(request.client.host)
        if client_host in trusted_hosts:
            return True

        # Check for HTTPS in production
        if request.headers.get("x-forwarded-proto") != "https":
            logger.warning(f"Non-HTTPS request from {client_host}")
            return False

        return True
    
    async def _is_suspicious_request(self, request: Request) -> bool:
        """Detect suspicious request patterns"""
        user_agent = request.headers.get("user-agent", "").lower()
        
        # Block common attack patterns
        suspicious_patterns = [
            "sqlmap", "nikto", "nmap", "masscan", "dirb", "gobuster",
            "wpscan", "burpsuite", "metasploit", "curl", "wget", "python-requests"
        ]
        
        # Block requests to root path from external IPs
        client_host = str(request.client.host)
        trusted_hosts = {"127.0.0.1", "localhost", "::1", "172.20.0.1"}
        
        if (client_host not in trusted_hosts and 
            str(request.url.path) == "/" and 
            request.method == "GET"):
            logger.warning(f"External root path access from {client_host}")
            return True
        
        if any(pattern in user_agent for pattern in suspicious_patterns):
            logger.warning(f"Suspicious user agent: {user_agent} from {request.client.host}")
            return True
            
        # Check for SQL injection patterns in query params
        query_string = str(request.query_params).lower()
        sql_patterns = ["union select", "drop table", "insert into", "delete from", "'or'1'='1"]
        
        if any(pattern in query_string for pattern in sql_patterns):
            logger.warning(f"Potential SQL injection from {request.client.host}: {query_string}")
            return True
            
        return False

async def rate_limit_handler(request: Request, exc: RateLimitExceeded):
    """Custom rate limit handler"""
    logger.warning(f"Rate limit exceeded for {request.client.host}: {exc}")
    return JSONResponse(
        status_code=status.HTTP_429_TOO_MANY_REQUESTS,
        content={
            "error": "Too many requests",
            "message": "Please slow down and try again later",
            "retry_after": exc.retry_after
        }
    )

class LoginAttemptTracker:
    """Track failed login attempts"""
    
    def __init__(self):
        self.attempts = {}
        
    def record_failed_attempt(self, identifier: str):
        """Record a failed login attempt"""
        current_time = time.time()
        if identifier not in self.attempts:
            self.attempts[identifier] = []
            
        # Clean old attempts
        self.attempts[identifier] = [
            attempt for attempt in self.attempts[identifier]
            if current_time - attempt < 900  # 15 minutes
        ]
        
        self.attempts[identifier].append(current_time)
        
    def is_locked_out(self, identifier: str) -> bool:
        """Check if identifier is locked out"""
        if identifier not in self.attempts:
            return False
            
        current_time = time.time()
        recent_attempts = [
            attempt for attempt in self.attempts[identifier]
            if current_time - attempt < 900  # 15 minutes
        ]
        
        return len(recent_attempts) >= 5
        
    def clear_attempts(self, identifier: str):
        """Clear attempts for successful login"""
        if identifier in self.attempts:
            del self.attempts[identifier]

# Global instance
login_tracker = LoginAttemptTracker()

def generate_secure_token() -> str:
    """Generate a cryptographically secure token"""
    return secrets.token_urlsafe(32)

def hash_password_secure(password: str) -> str:
    """Hash password with secure method"""
    salt = secrets.token_bytes(32)
    key = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt, 100000)
    return salt.hex() + key.hex()

def verify_password_secure(password: str, hashed_password: str) -> bool:
    """Verify password against secure hash"""
    try:
        salt = bytes.fromhex(hashed_password[:64])
        stored_key = hashed_password[64:]
        key = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt, 100000)
        return key.hex() == stored_key
    except Exception:
        return False
