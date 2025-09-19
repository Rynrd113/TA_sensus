# backend/core/auth.py
"""
JWT Authentication System for Sensus RS
Implements secure token-based authentication with role management
"""

from datetime import datetime, timedelta
from typing import Optional, List
import jwt
from passlib.context import CryptContext
from passlib.hash import bcrypt
from fastapi import HTTPException, status, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import secrets

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# JWT Configuration
JWT_SECRET_KEY = "your-super-secret-jwt-key-change-in-production"  # Change in production!
JWT_ALGORITHM = "HS256"
JWT_EXPIRATION_HOURS = 24

# Security scheme
security = HTTPBearer()

class AuthConfig:
    """Authentication configuration constants"""
    SECRET_KEY = JWT_SECRET_KEY
    ALGORITHM = JWT_ALGORITHM
    ACCESS_TOKEN_EXPIRE_HOURS = JWT_EXPIRATION_HOURS
    
    # User roles
    ROLES = {
        "admin": "Administrator - Full system access",
        "doctor": "Doctor - Medical data access", 
        "nurse": "Nurse - Data entry and viewing",
        "viewer": "Viewer - Read-only access"
    }

class PasswordManager:
    """Handle password hashing and verification"""
    
    @staticmethod
    def hash_password(password: str) -> str:
        """Hash a password for storing in database"""
        return pwd_context.hash(password)
    
    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        """Verify a password against its hash"""
        return pwd_context.verify(plain_password, hashed_password)
    
    @staticmethod
    def generate_random_password(length: int = 12) -> str:
        """Generate a secure random password"""
        return secrets.token_urlsafe(length)

class JWTManager:
    """Handle JWT token creation and validation"""
    
    @staticmethod
    def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
        """Create a JWT access token"""
        to_encode = data.copy()
        
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(hours=AuthConfig.ACCESS_TOKEN_EXPIRE_HOURS)
        
        to_encode.update({"exp": expire, "iat": datetime.utcnow()})
        
        encoded_jwt = jwt.encode(
            to_encode, 
            AuthConfig.SECRET_KEY, 
            algorithm=AuthConfig.ALGORITHM
        )
        
        return encoded_jwt
    
    @staticmethod
    def verify_token(token: str) -> dict:
        """Verify and decode a JWT token"""
        try:
            payload = jwt.decode(
                token, 
                AuthConfig.SECRET_KEY, 
                algorithms=[AuthConfig.ALGORITHM]
            )
            
            # Check if token has expired
            if datetime.fromtimestamp(payload.get("exp", 0)) < datetime.utcnow():
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Token has expired",
                    headers={"WWW-Authenticate": "Bearer"}
                )
            
            return payload
            
        except jwt.InvalidTokenError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token",
                headers={"WWW-Authenticate": "Bearer"}
            )

class RoleManager:
    """Handle user role validation and permissions"""
    
    @staticmethod
    def has_role(user_roles: List[str], required_role: str) -> bool:
        """Check if user has required role"""
        role_hierarchy = {
            "viewer": 1,
            "nurse": 2, 
            "doctor": 3,
            "admin": 4
        }
        
        user_level = max([role_hierarchy.get(role, 0) for role in user_roles])
        required_level = role_hierarchy.get(required_role, 0)
        
        return user_level >= required_level
    
    @staticmethod
    def can_access_resource(user_roles: List[str], resource: str) -> bool:
        """Check if user can access specific resource"""
        permissions = {
            "dashboard": ["viewer", "nurse", "doctor", "admin"],
            "sensus_data": ["nurse", "doctor", "admin"],
            "indicators": ["viewer", "nurse", "doctor", "admin"],
            "predictions": ["doctor", "admin"],
            "user_management": ["admin"],
            "system_settings": ["admin"],
            "export_data": ["doctor", "admin"],
            "bulk_import": ["admin"]
        }
        
        allowed_roles = permissions.get(resource, [])
        return any(role in allowed_roles for role in user_roles)

# Dependency functions for FastAPI
async def get_current_user_token(credentials: HTTPAuthorizationCredentials = Depends(security)) -> dict:
    """Extract and verify current user from JWT token"""
    token = credentials.credentials
    payload = JWTManager.verify_token(token)
    
    if not payload.get("sub"):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token payload"
        )
    
    return payload

# Alias for compatibility
async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> dict:
    """Alias for get_current_user_token for compatibility"""
    return await get_current_user_token(credentials)

def require_role(required_role: str):
    """Dependency factory for role-based access control"""
    def role_checker(current_user: dict = Depends(get_current_user_token)) -> dict:
        user_roles = current_user.get("roles", [])
        
        if not RoleManager.has_role(user_roles, required_role):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Insufficient permissions. Required: {required_role}"
            )
        
        return current_user
    
    return role_checker

def require_resource_access(resource: str):
    """Dependency factory for resource-based access control"""
    def resource_checker(current_user: dict = Depends(get_current_user_token)) -> dict:
        user_roles = current_user.get("roles", [])
        
        if not RoleManager.can_access_resource(user_roles, resource):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"No access to resource: {resource}"
            )
        
        return current_user
    
    return resource_checker

# Common role dependencies (these are functions that return dependencies)
def require_admin():
    return require_role("admin")()

def require_doctor():
    return require_role("doctor")()

def require_nurse():
    return require_role("nurse")()

def require_viewer():
    return require_role("viewer")()

# Common resource dependencies (these are functions that return dependencies)
def require_dashboard_access():
    return require_resource_access("dashboard")()

def require_data_entry():
    return require_resource_access("sensus_data")()

def require_prediction_access():
    return require_resource_access("predictions")()

def require_user_management():
    return require_resource_access("user_management")()