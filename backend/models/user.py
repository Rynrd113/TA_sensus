# backend/models/user.py
"""
User Model for Authentication System
SQLAlchemy models for user management with role-based access control
"""

from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, JSON
from sqlalchemy.orm import relationship
from datetime import datetime
from .base import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True, nullable=False)
    email = Column(String(100), unique=True, index=True, nullable=False)
    full_name = Column(String(100), nullable=False)
    hashed_password = Column(String(255), nullable=False)
    
    # User status and roles
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)
    roles = Column(JSON, default=list)  # Store roles as JSON array
    
    # Professional information
    employee_id = Column(String(20), unique=True, index=True)
    department = Column(String(100))
    position = Column(String(100))
    phone = Column(String(20))
    
    # Account management
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_login = Column(DateTime, nullable=True)
    password_changed_at = Column(DateTime, default=datetime.utcnow)
    
    # Security and preferences
    failed_login_attempts = Column(Integer, default=0)
    locked_until = Column(DateTime, nullable=True)
    preferences = Column(JSON, default=dict)  # Store user preferences
    
    def __repr__(self):
        return f"<User(id={self.id}, username='{self.username}', email='{self.email}')>"
    
    def to_dict(self):
        """Convert user object to dictionary (excluding sensitive data)"""
        return {
            "id": self.id,
            "username": self.username,
            "email": self.email,
            "full_name": self.full_name,
            "is_active": self.is_active,
            "is_verified": self.is_verified,
            "roles": self.roles,
            "employee_id": self.employee_id,
            "department": self.department,
            "position": self.position,
            "phone": self.phone,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "last_login": self.last_login.isoformat() if self.last_login else None
        }
    
    def has_role(self, role: str) -> bool:
        """Check if user has specific role"""
        return role in (self.roles or [])
    
    def has_any_role(self, roles: list) -> bool:
        """Check if user has any of the specified roles"""
        user_roles = self.roles or []
        return any(role in user_roles for role in roles)
    
    def is_admin(self) -> bool:
        """Check if user is admin"""
        return self.has_role("admin")
    
    def can_access_dashboard(self) -> bool:
        """Check if user can access dashboard"""
        return self.has_any_role(["viewer", "nurse", "doctor", "admin"])
    
    def can_modify_data(self) -> bool:
        """Check if user can modify sensus data"""
        return self.has_any_role(["nurse", "doctor", "admin"])

class UserSession(Base):
    __tablename__ = "user_sessions"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, nullable=False, index=True)
    token_jti = Column(String(255), unique=True, index=True)  # JWT ID
    created_at = Column(DateTime, default=datetime.utcnow)
    expires_at = Column(DateTime, nullable=False)
    is_revoked = Column(Boolean, default=False)
    user_agent = Column(String(500))
    ip_address = Column(String(45))  # Support IPv6
    
    def __repr__(self):
        return f"<UserSession(id={self.id}, user_id={self.user_id}, expires_at='{self.expires_at}')>"
    
    def is_expired(self) -> bool:
        """Check if session is expired"""
        return datetime.utcnow() > self.expires_at
    
    def is_valid(self) -> bool:
        """Check if session is valid (not revoked and not expired)"""
        return not self.is_revoked and not self.is_expired()

class UserLoginLog(Base):
    __tablename__ = "user_login_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, nullable=True, index=True)  # Null for failed attempts
    username = Column(String(50), index=True)
    login_time = Column(DateTime, default=datetime.utcnow)
    success = Column(Boolean, nullable=False)
    ip_address = Column(String(45))
    user_agent = Column(String(500))
    failure_reason = Column(String(255), nullable=True)
    
    def __repr__(self):
        return f"<UserLoginLog(id={self.id}, username='{self.username}', success={self.success})>"