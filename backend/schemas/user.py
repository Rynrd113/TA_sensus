# backend/schemas/user.py
"""
User Pydantic Schemas for API Request/Response
Authentication and user management data validation
"""

from pydantic import BaseModel, EmailStr, Field, validator
from typing import Optional, List, Dict, Any
from datetime import datetime

# Authentication Schemas
class LoginRequest(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    password: str = Field(..., min_length=6)
    remember_me: bool = False

class LoginResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int  # seconds
    user: "UserResponse"

class TokenRefreshRequest(BaseModel):
    refresh_token: str

class PasswordChangeRequest(BaseModel):
    current_password: str
    new_password: str = Field(..., min_length=8)
    confirm_password: str

    @validator('confirm_password')
    def passwords_match(cls, v, values, **kwargs):
        if 'new_password' in values and v != values['new_password']:
            raise ValueError('passwords do not match')
        return v

class PasswordResetRequest(BaseModel):
    email: EmailStr

class PasswordResetConfirm(BaseModel):
    token: str
    new_password: str = Field(..., min_length=8)
    confirm_password: str

    @validator('confirm_password')
    def passwords_match(cls, v, values, **kwargs):
        if 'new_password' in values and v != values['new_password']:
            raise ValueError('passwords do not match')
        return v

# User CRUD Schemas
class UserBase(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr
    full_name: str = Field(..., min_length=2, max_length=100)
    employee_id: Optional[str] = Field(None, max_length=20)
    department: Optional[str] = Field(None, max_length=100)
    position: Optional[str] = Field(None, max_length=100)
    phone: Optional[str] = Field(None, max_length=20)
    roles: List[str] = []

    @validator('roles')
    def validate_roles(cls, v):
        valid_roles = ["admin", "doctor", "nurse", "viewer"]
        for role in v:
            if role not in valid_roles:
                raise ValueError(f'Invalid role: {role}. Valid roles: {valid_roles}')
        return v

class UserCreate(UserBase):
    password: str = Field(..., min_length=8)
    is_active: bool = True
    is_verified: bool = False

class UserUpdate(BaseModel):
    email: Optional[EmailStr] = None
    full_name: Optional[str] = Field(None, min_length=2, max_length=100)
    employee_id: Optional[str] = Field(None, max_length=20)
    department: Optional[str] = Field(None, max_length=100)
    position: Optional[str] = Field(None, max_length=100)
    phone: Optional[str] = Field(None, max_length=20)
    roles: Optional[List[str]] = None
    is_active: Optional[bool] = None
    is_verified: Optional[bool] = None

    @validator('roles')
    def validate_roles(cls, v):
        if v is not None:
            valid_roles = ["admin", "doctor", "nurse", "viewer"]
            for role in v:
                if role not in valid_roles:
                    raise ValueError(f'Invalid role: {role}. Valid roles: {valid_roles}')
        return v

class UserResponse(BaseModel):
    id: int
    username: str
    email: EmailStr
    full_name: str
    employee_id: Optional[str]
    department: Optional[str]
    position: Optional[str]
    phone: Optional[str]
    roles: List[str]
    is_active: bool
    is_verified: bool
    created_at: datetime
    last_login: Optional[datetime]

    class Config:
        from_attributes = True

class UserListResponse(BaseModel):
    users: List[UserResponse]
    total: int
    page: int
    per_page: int
    pages: int

# Session and Security Schemas
class UserSessionResponse(BaseModel):
    id: int
    user_id: int
    created_at: datetime
    expires_at: datetime
    user_agent: Optional[str]
    ip_address: Optional[str]
    is_current: bool = False

    class Config:
        from_attributes = True

class UserLoginLogResponse(BaseModel):
    id: int
    username: str
    login_time: datetime
    success: bool
    ip_address: Optional[str]
    user_agent: Optional[str]
    failure_reason: Optional[str]

    class Config:
        from_attributes = True

# Profile and Preferences Schemas
class UserProfileResponse(UserResponse):
    preferences: Dict[str, Any] = {}
    password_changed_at: Optional[datetime]
    failed_login_attempts: int
    locked_until: Optional[datetime]

class UserPreferencesUpdate(BaseModel):
    theme: Optional[str] = Field(None, pattern="^(light|dark|auto)$")
    language: Optional[str] = Field(None, max_length=10)
    dashboard_layout: Optional[str] = None
    notification_settings: Optional[Dict[str, bool]] = None
    chart_preferences: Optional[Dict[str, Any]] = None

# Role and Permission Schemas
class RoleInfo(BaseModel):
    role: str
    description: str
    permissions: List[str]

class PermissionCheck(BaseModel):
    resource: str
    action: str = "read"  # read, write, delete, admin

class PermissionResponse(BaseModel):
    allowed: bool
    reason: Optional[str] = None

# Update LoginResponse to avoid circular reference
LoginResponse.model_rebuild()