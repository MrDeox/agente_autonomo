"""
Authentication Manager - Agente Autônomo v2.8.1
Implements secure JWT authentication and thread-safe session management.
"""

import jwt
import secrets
import hashlib
import hmac
import time
import logging
import threading
from typing import Dict, Any, Optional, Union, List
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
import json
import base64
from pathlib import Path

from fastapi import HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials


class AuthLevel(Enum):
    """Authentication levels"""
    NONE = 0
    READ = 1
    WRITE = 2
    ADMIN = 3
    SYSTEM = 4


class TokenType(Enum):
    """JWT token types"""
    ACCESS = "access"
    REFRESH = "refresh"
    SYSTEM = "system"
    AGENT = "agent"


@dataclass
class UserSession:
    """User session data"""
    user_id: str
    username: str
    auth_level: AuthLevel
    permissions: List[str]
    created_at: datetime
    last_activity: datetime
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    is_active: bool = True


@dataclass
class TokenPayload:
    """JWT token payload"""
    user_id: str
    username: str
    auth_level: AuthLevel
    permissions: List[str]
    token_type: TokenType
    exp: datetime
    iat: datetime
    jti: str  # JWT ID for token revocation


class AuthManager:
    """Secure authentication manager with JWT and session management"""
    
    def __init__(self, config: Dict[str, Any], logger: logging.Logger):
        self.config = config
        self.logger = logger
        
        # Security configuration
        self.secret_key = self._get_secret_key()
        self.algorithm = "HS256"
        self.access_token_expiry = timedelta(hours=1)
        self.refresh_token_expiry = timedelta(days=7)
        self.system_token_expiry = timedelta(hours=24)
        
        # Thread-safe session storage
        self._sessions: Dict[str, UserSession] = {}
        self._session_lock = threading.RLock()
        
        # Token blacklist for revocation
        self._blacklisted_tokens: set = set()
        self._blacklist_lock = threading.RLock()
        
        # Rate limiting
        self._rate_limit_store: Dict[str, List[float]] = {}
        self._rate_limit_lock = threading.RLock()
        self.max_requests_per_minute = 60
        
        # Initialize security
        self._initialize_security()
        
        self.logger.info("🔐 Authentication Manager initialized")
    
    def _get_secret_key(self) -> str:
        """Get or generate secret key"""
        secret_key = self.config.get("security", {}).get("secret_key")
        if not secret_key:
            # Generate a secure random key
            secret_key = secrets.token_urlsafe(32)
            self.logger.warning("No secret key configured, generated new one")
        
        return secret_key
    
    def _initialize_security(self):
        """Initialize security settings"""
        # Validate secret key strength
        if len(self.secret_key) < 32:
            raise ValueError("Secret key must be at least 32 characters long")
        
        # Set up security headers
        self.security_headers = {
            "X-Content-Type-Options": "nosniff",
            "X-Frame-Options": "DENY",
            "X-XSS-Protection": "1; mode=block",
            "Strict-Transport-Security": "max-age=31536000; includeSubDomains"
        }
    
    def create_access_token(self, user_id: str, username: str, 
                          auth_level: AuthLevel, permissions: List[str]) -> str:
        """Create a JWT access token"""
        try:
            now = datetime.utcnow()
            payload = TokenPayload(
                user_id=user_id,
                username=username,
                auth_level=auth_level,
                permissions=permissions,
                token_type=TokenType.ACCESS,
                exp=now + self.access_token_expiry,
                iat=now,
                jti=secrets.token_urlsafe(16)
            )
            
            token_data = {
                "user_id": payload.user_id,
                "username": payload.username,
                "auth_level": payload.auth_level.value,
                "permissions": payload.permissions,
                "token_type": payload.token_type.value,
                "exp": int(payload.exp.timestamp()),
                "iat": int(payload.iat.timestamp()),
                "jti": payload.jti
            }
            
            token = jwt.encode(token_data, self.secret_key, algorithm=self.algorithm)
            self.logger.info(f"Created access token for user {username}")
            return token
            
        except Exception as e:
            self.logger.error(f"Failed to create access token: {e}")
            raise
    
    def create_refresh_token(self, user_id: str, username: str) -> str:
        """Create a JWT refresh token"""
        try:
            now = datetime.utcnow()
            payload = TokenPayload(
                user_id=user_id,
                username=username,
                auth_level=AuthLevel.READ,  # Minimal permissions for refresh
                permissions=["refresh"],
                token_type=TokenType.REFRESH,
                exp=now + self.refresh_token_expiry,
                iat=now,
                jti=secrets.token_urlsafe(16)
            )
            
            token_data = {
                "user_id": payload.user_id,
                "username": payload.username,
                "auth_level": payload.auth_level.value,
                "permissions": payload.permissions,
                "token_type": payload.token_type.value,
                "exp": int(payload.exp.timestamp()),
                "iat": int(payload.iat.timestamp()),
                "jti": payload.jti
            }
            
            token = jwt.encode(token_data, self.secret_key, algorithm=self.algorithm)
            self.logger.info(f"Created refresh token for user {username}")
            return token
            
        except Exception as e:
            self.logger.error(f"Failed to create refresh token: {e}")
            raise
    
    def create_system_token(self, agent_id: str, capabilities: List[str]) -> str:
        """Create a system token for agent authentication"""
        try:
            now = datetime.utcnow()
            payload = TokenPayload(
                user_id=agent_id,
                username=f"system_{agent_id}",
                auth_level=AuthLevel.SYSTEM,
                permissions=capabilities,
                token_type=TokenType.SYSTEM,
                exp=now + self.system_token_expiry,
                iat=now,
                jti=secrets.token_urlsafe(16)
            )
            
            token_data = {
                "user_id": payload.user_id,
                "username": payload.username,
                "auth_level": payload.auth_level.value,
                "permissions": payload.permissions,
                "token_type": payload.token_type.value,
                "exp": int(payload.exp.timestamp()),
                "iat": int(payload.iat.timestamp()),
                "jti": payload.jti
            }
            
            token = jwt.encode(token_data, self.secret_key, algorithm=self.algorithm)
            self.logger.info(f"Created system token for agent {agent_id}")
            return token
            
        except Exception as e:
            self.logger.error(f"Failed to create system token: {e}")
            raise
    
    def verify_token(self, token: str) -> Optional[TokenPayload]:
        """Verify and decode a JWT token"""
        try:
            # Check if token is blacklisted
            with self._blacklist_lock:
                if token in self._blacklisted_tokens:
                    self.logger.warning("Token is blacklisted")
                    return None
            
            # Decode token
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            
            # Validate token structure
            required_fields = ["user_id", "username", "auth_level", "permissions", 
                             "token_type", "exp", "iat", "jti"]
            if not all(field in payload for field in required_fields):
                self.logger.warning("Token missing required fields")
                return None
            
            # Create TokenPayload object
            token_payload = TokenPayload(
                user_id=payload["user_id"],
                username=payload["username"],
                auth_level=AuthLevel(payload["auth_level"]),
                permissions=payload["permissions"],
                token_type=TokenType(payload["token_type"]),
                exp=datetime.fromtimestamp(payload["exp"]),
                iat=datetime.fromtimestamp(payload["iat"]),
                jti=payload["jti"]
            )
            
            # Check expiration
            if token_payload.exp < datetime.utcnow():
                self.logger.warning("Token has expired")
                return None
            
            self.logger.debug(f"Token verified for user {token_payload.username}")
            return token_payload
            
        except jwt.ExpiredSignatureError:
            self.logger.warning("Token has expired")
            return None
        except jwt.InvalidTokenError as e:
            self.logger.warning(f"Invalid token: {e}")
            return None
        except Exception as e:
            self.logger.error(f"Error verifying token: {e}")
            return None
    
    def revoke_token(self, token: str) -> bool:
        """Revoke a token by adding it to blacklist"""
        try:
            with self._blacklist_lock:
                self._blacklisted_tokens.add(token)
            
            self.logger.info("Token revoked successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to revoke token: {e}")
            return False
    
    def create_session(self, user_id: str, username: str, auth_level: AuthLevel,
                      permissions: List[str], ip_address: Optional[str] = None,
                      user_agent: Optional[str] = None) -> str:
        """Create a new user session"""
        try:
            session_id = secrets.token_urlsafe(32)
            now = datetime.utcnow()
            
            session = UserSession(
                user_id=user_id,
                username=username,
                auth_level=auth_level,
                permissions=permissions,
                created_at=now,
                last_activity=now,
                ip_address=ip_address,
                user_agent=user_agent
            )
            
            with self._session_lock:
                self._sessions[session_id] = session
            
            self.logger.info(f"Created session for user {username}")
            return session_id
            
        except Exception as e:
            self.logger.error(f"Failed to create session: {e}")
            raise
    
    def get_session(self, session_id: str) -> Optional[UserSession]:
        """Get a user session"""
        try:
            with self._session_lock:
                session = self._sessions.get(session_id)
                if session and session.is_active:
                    # Update last activity
                    session.last_activity = datetime.utcnow()
                    return session
                return None
                
        except Exception as e:
            self.logger.error(f"Failed to get session: {e}")
            return None
    
    def invalidate_session(self, session_id: str) -> bool:
        """Invalidate a user session"""
        try:
            with self._session_lock:
                if session_id in self._sessions:
                    self._sessions[session_id].is_active = False
                    del self._sessions[session_id]
                    self.logger.info(f"Invalidated session {session_id}")
                    return True
                return False
                
        except Exception as e:
            self.logger.error(f"Failed to invalidate session: {e}")
            return False
    
    def check_rate_limit(self, identifier: str) -> bool:
        """Check rate limiting for an identifier (IP, user_id, etc.)"""
        try:
            now = time.time()
            window_start = now - 60  # 1 minute window
            
            with self._rate_limit_lock:
                if identifier not in self._rate_limit_store:
                    self._rate_limit_store[identifier] = []
                
                # Remove old requests outside the window
                self._rate_limit_store[identifier] = [
                    req_time for req_time in self._rate_limit_store[identifier]
                    if req_time > window_start
                ]
                
                # Check if limit exceeded
                if len(self._rate_limit_store[identifier]) >= self.max_requests_per_minute:
                    self.logger.warning(f"Rate limit exceeded for {identifier}")
                    return False
                
                # Add current request
                self._rate_limit_store[identifier].append(now)
                return True
                
        except Exception as e:
            self.logger.error(f"Error checking rate limit: {e}")
            return False
    
    def authenticate_user(self, username: str, password: str) -> Optional[Dict[str, Any]]:
        """Authenticate a user with username and password"""
        try:
            # In production, this should check against a secure database
            # For now, implement basic authentication for demo purposes
            
            # Demo users (in production, use proper user management)
            demo_users = {
                "admin": {
                    "password_hash": self._hash_password("admin123"),
                    "auth_level": AuthLevel.ADMIN,
                    "permissions": ["read", "write", "admin", "system"]
                },
                "user": {
                    "password_hash": self._hash_password("user123"),
                    "auth_level": AuthLevel.WRITE,
                    "permissions": ["read", "write"]
                },
                "viewer": {
                    "password_hash": self._hash_password("viewer123"),
                    "auth_level": AuthLevel.READ,
                    "permissions": ["read"]
                }
            }
            
            if username not in demo_users:
                self.logger.warning(f"Authentication failed for unknown user: {username}")
                return None
            
            user_data = demo_users[username]
            if not self._verify_password(password, user_data["password_hash"]):
                self.logger.warning(f"Authentication failed for user: {username}")
                return None
            
            self.logger.info(f"User {username} authenticated successfully")
            return {
                "user_id": f"user_{username}",
                "username": username,
                "auth_level": user_data["auth_level"],
                "permissions": user_data["permissions"]
            }
            
        except Exception as e:
            self.logger.error(f"Authentication error: {e}")
            return None
    
    def _hash_password(self, password: str) -> str:
        """Hash a password using secure method"""
        salt = secrets.token_hex(16)
        hash_obj = hashlib.pbkdf2_hmac('sha256', password.encode(), salt.encode(), 100000)
        return f"{salt}${hash_obj.hex()}"
    
    def _verify_password(self, password: str, password_hash: str) -> bool:
        """Verify a password against its hash"""
        try:
            salt, hash_hex = password_hash.split('$')
            hash_obj = hashlib.pbkdf2_hmac('sha256', password.encode(), salt.encode(), 100000)
            return hmac.compare_digest(hash_obj.hex(), hash_hex)
        except Exception:
            return False
    
    def cleanup_expired_sessions(self):
        """Clean up expired sessions"""
        try:
            now = datetime.utcnow()
            expired_sessions = []
            
            with self._session_lock:
                for session_id, session in self._sessions.items():
                    # Remove sessions inactive for more than 24 hours
                    if (now - session.last_activity) > timedelta(hours=24):
                        expired_sessions.append(session_id)
                
                for session_id in expired_sessions:
                    del self._sessions[session_id]
            
            if expired_sessions:
                self.logger.info(f"Cleaned up {len(expired_sessions)} expired sessions")
                
        except Exception as e:
            self.logger.error(f"Error cleaning up sessions: {e}")
    
    def get_security_headers(self) -> Dict[str, str]:
        """Get security headers for responses"""
        return self.security_headers.copy()


# Global auth manager instance
_auth_manager = None

def get_auth_manager(config: Dict[str, Any], logger: logging.Logger) -> AuthManager:
    """Get the global authentication manager instance"""
    global _auth_manager
    if _auth_manager is None:
        _auth_manager = AuthManager(config, logger)
    return _auth_manager 