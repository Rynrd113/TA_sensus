# backend/services/auth_service.py
"""
Authentication Service Layer
Business logic for user authentication and authorization
"""

from typing import Optional, Tuple, Dict, Any
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
import uuid

from core.auth import JWTManager, PasswordManager, RoleManager
from models.user import User
from repositories.user_repository import UserRepository, UserSessionRepository, UserLoginLogRepository
from schemas.user import LoginRequest, LoginResponse, UserCreate, UserResponse

class AuthService:
    def __init__(self, db: Session):
        self.db = db
        self.user_repo = UserRepository(db)
        self.session_repo = UserSessionRepository(db)
        self.login_log_repo = UserLoginLogRepository(db)
    
    async def authenticate_user(
        self,
        login_request: LoginRequest,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None
    ) -> Tuple[Optional[LoginResponse], str]:
        """
        Authenticate user login
        Returns: (LoginResponse, error_message)
        """
        username = login_request.username
        password = login_request.password
        
        # Find user by username or email
        user = self.user_repo.get_by_username_or_email(username)
        
        if not user:
            # Log failed attempt
            self.login_log_repo.log_login_attempt(
                username=username,
                success=False,
                ip_address=ip_address,
                user_agent=user_agent,
                failure_reason="User not found"
            )
            return None, "Invalid username or password"
        
        # Check if account is locked
        if self.user_repo.is_user_locked(user):
            self.login_log_repo.log_login_attempt(
                username=username,
                success=False,
                user_id=user.id,
                ip_address=ip_address,
                user_agent=user_agent,
                failure_reason="Account locked"
            )
            return None, "Account is temporarily locked due to multiple failed login attempts"
        
        # Check if account is active
        if not user.is_active:
            self.login_log_repo.log_login_attempt(
                username=username,
                success=False,
                user_id=user.id,
                ip_address=ip_address,
                user_agent=user_agent,
                failure_reason="Account inactive"
            )
            return None, "Account is deactivated"
        
        # Verify password
        if not self.user_repo.verify_password(user, password):
            # Increment failed attempts
            failed_count = self.user_repo.increment_failed_login(user.id)
            
            self.login_log_repo.log_login_attempt(
                username=username,
                success=False,
                user_id=user.id,
                ip_address=ip_address,
                user_agent=user_agent,
                failure_reason="Invalid password"
            )
            
            if failed_count >= 5:
                return None, "Account locked due to multiple failed attempts"
            
            return None, "Invalid username or password"
        
        # Successful authentication
        # Update last login
        self.user_repo.update_last_login(user.id)
        
        # Create JWT token
        token_jti = str(uuid.uuid4())
        token_expiry = timedelta(
            hours=48 if login_request.remember_me else 24
        )
        
        token_data = {
            "sub": user.username,
            "user_id": user.id,
            "roles": user.roles or [],
            "jti": token_jti
        }
        
        access_token = JWTManager.create_access_token(
            data=token_data,
            expires_delta=token_expiry
        )
        
        # Store session
        expires_at = datetime.utcnow() + token_expiry
        self.session_repo.create_session(
            user_id=user.id,
            token_jti=token_jti,
            expires_at=expires_at,
            user_agent=user_agent,
            ip_address=ip_address
        )
        
        # Log successful login
        self.login_log_repo.log_login_attempt(
            username=username,
            success=True,
            user_id=user.id,
            ip_address=ip_address,
            user_agent=user_agent
        )
        
        # Return login response
        response = LoginResponse(
            access_token=access_token,
            token_type="bearer",
            expires_in=int(token_expiry.total_seconds()),
            user=UserResponse.model_validate(user)
        )
        
        return response, ""
    
    async def logout_user(self, token_jti: str) -> bool:
        """Logout user by revoking session"""
        return self.session_repo.revoke_session(token_jti)
    
    async def logout_all_sessions(self, user_id: int, except_jti: Optional[str] = None) -> int:
        """Logout user from all devices"""
        return self.session_repo.revoke_user_sessions(user_id, except_jti)
    
    async def validate_session(self, token_jti: str) -> bool:
        """Validate if session is still active"""
        session = self.session_repo.get_session_by_jti(token_jti)
        return session and session.is_valid()
    
    async def create_user(
        self,
        user_data: UserCreate,
        created_by_user_id: Optional[int] = None
    ) -> UserResponse:
        """Create a new user"""
        
        # Check if username already exists
        if self.user_repo.get_by_username(user_data.username):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username already registered"
            )
        
        # Check if email already exists
        if self.user_repo.get_by_email(user_data.email):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )
        
        # Check if employee_id already exists (if provided)
        if user_data.employee_id and self.user_repo.get_by_employee_id(user_data.employee_id):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Employee ID already exists"
            )
        
        # Create user
        user_dict = user_data.model_dump()
        user = self.user_repo.create_user(user_dict)
        
        return UserResponse.model_validate(user)
    
    async def change_password(
        self,
        user_id: int,
        current_password: str,
        new_password: str
    ) -> bool:
        """Change user password"""
        user = self.user_repo.get_by_id(user_id)
        if not user:
            return False
        
        # Verify current password
        if not self.user_repo.verify_password(user, current_password):
            return False
        
        # Update password
        return self.user_repo.update_password(user_id, new_password)
    
    async def reset_user_password(
        self,
        user_id: int,
        new_password: str,
        admin_user_id: int
    ) -> bool:
        """Admin reset user password"""
        admin_user = self.user_repo.get_by_id(admin_user_id)
        if not admin_user or not admin_user.is_admin():
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Admin access required"
            )
        
        return self.user_repo.update_password(user_id, new_password)
    
    async def get_user_profile(self, user_id: int) -> Optional[UserResponse]:
        """Get user profile"""
        user = self.user_repo.get_by_id(user_id)
        if user:
            return UserResponse.model_validate(user)
        return None
    
    async def update_user_preferences(
        self,
        user_id: int,
        preferences: Dict[str, Any]
    ) -> bool:
        """Update user preferences"""
        return self.user_repo.update_user_preferences(user_id, preferences)
    
    async def check_permission(
        self,
        user_id: int,
        resource: str,
        action: str = "read"
    ) -> bool:
        """Check if user has permission for resource/action"""
        user = self.user_repo.get_by_id(user_id)
        if not user or not user.is_active:
            return False
        
        user_roles = user.roles or []
        
        # Check resource access
        if not RoleManager.can_access_resource(user_roles, resource):
            return False
        
        # Check action-specific permissions
        if action == "write" and not RoleManager.has_role(user_roles, "nurse"):
            return False
        
        if action == "admin" and not RoleManager.has_role(user_roles, "admin"):
            return False
        
        return True
    
    async def get_user_sessions(self, user_id: int):
        """Get active sessions for user"""
        return self.session_repo.get_user_sessions(user_id, active_only=True)
    
    async def get_user_login_history(self, user_id: int, limit: int = 20):
        """Get user's login history"""
        return self.login_log_repo.get_user_login_history(user_id, limit)
    
    async def unlock_user_account(self, user_id: int, admin_user_id: int) -> bool:
        """Admin unlock user account"""
        admin_user = self.user_repo.get_by_id(admin_user_id)
        if not admin_user or not admin_user.is_admin():
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Admin access required"
            )
        
        return self.user_repo.unlock_user(user_id)

class TokenService:
    """Service for token-specific operations"""
    
    @staticmethod
    def extract_user_from_token(token_payload: dict) -> Dict[str, Any]:
        """Extract user info from token payload"""
        return {
            "user_id": token_payload.get("user_id"),
            "username": token_payload.get("sub"),
            "roles": token_payload.get("roles", []),
            "token_jti": token_payload.get("jti")
        }
    
    @staticmethod
    def create_password_reset_token(user_id: int) -> str:
        """Create password reset token (short expiry)"""
        token_data = {
            "sub": f"password_reset:{user_id}",
            "type": "password_reset"
        }
        
        return JWTManager.create_access_token(
            data=token_data,
            expires_delta=timedelta(hours=1)  # 1 hour expiry
        )
    
    @staticmethod
    def verify_password_reset_token(token: str) -> Optional[int]:
        """Verify password reset token and extract user ID"""
        try:
            payload = JWTManager.verify_token(token)
            
            if payload.get("type") != "password_reset":
                return None
            
            sub = payload.get("sub", "")
            if not sub.startswith("password_reset:"):
                return None
            
            user_id = int(sub.split(":", 1)[1])
            return user_id
            
        except (ValueError, HTTPException):
            return None