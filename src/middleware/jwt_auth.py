"""JWT token-based authentication for user endpoints."""

import jwt
import os
import logging
from datetime import datetime, timedelta
from typing import Optional, Dict
from fastapi import Request, HTTPException, status, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from ..models.responses import ServiceResponse

logger = logging.getLogger(__name__)

# JWT secret key (should be set via environment variable)
JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "change-this-secret-key-in-production")
JWT_ALGORITHM = "HS256"
JWT_EXPIRATION_HOURS = 24

# HTTP Bearer token security
security = HTTPBearer(auto_error=False)


class JWTAuth:
    """JWT authentication manager."""
    
    def __init__(self, secret_key: str = None, algorithm: str = "HS256"):
        """Initialize JWT auth."""
        self.secret_key = secret_key or JWT_SECRET_KEY
        self.algorithm = algorithm
    
    def create_token(self, user_id: str, payload: Dict = None) -> str:
        """Create a JWT token."""
        if payload is None:
            payload = {}
        
        payload.update({
            "user_id": user_id,
            "exp": datetime.utcnow() + timedelta(hours=JWT_EXPIRATION_HOURS),
            "iat": datetime.utcnow()
        })
        
        token = jwt.encode(payload, self.secret_key, algorithm=self.algorithm)
        return token
    
    def verify_token(self, token: str) -> Optional[Dict]:
        """Verify and decode JWT token."""
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            return payload
        except jwt.ExpiredSignatureError:
            logger.warning("JWT token expired")
            return None
        except jwt.InvalidTokenError as e:
            logger.warning(f"Invalid JWT token: {e}")
            return None
    
    def get_user_from_token(self, token: str) -> Optional[str]:
        """Extract user ID from JWT token."""
        payload = self.verify_token(token)
        if payload:
            return payload.get("user_id")
        return None


# Global JWT auth instance
jwt_auth = JWTAuth()


async def verify_jwt_token(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security)
) -> Dict:
    """
    Verify JWT token from Authorization header.
    
    Usage:
        @router.get("/protected")
        async def protected_endpoint(user: Dict = Depends(verify_jwt_token)):
            return {"user_id": user["user_id"]}
    """
    if not credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing or invalid authentication token",
            headers={"WWW-Authenticate": "Bearer"}
        )
    
    token = credentials.credentials
    payload = jwt_auth.verify_token(token)
    
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"}
        )
    
    return payload


def optional_jwt_auth(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security)
) -> Optional[Dict]:
    """
    Optional JWT authentication - returns None if token is missing or invalid.
    
    Usage:
        @router.get("/optional")
        async def optional_endpoint(user: Optional[Dict] = Depends(optional_jwt_auth)):
            if user:
                return {"user_id": user["user_id"]}
            return {"anonymous": True}
    """
    if not credentials:
        return None
    
    token = credentials.credentials
    return jwt_auth.verify_token(token)


def get_jwt_auth() -> JWTAuth:
    """Get JWT auth instance."""
    return jwt_auth

