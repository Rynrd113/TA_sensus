# backend/api/v1/auth_router.py
"""
Authentication API Endpoints
FastAPI router for user authentication and authorization
"""

from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.security import HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from typing import List

from database.session import get_db
from core.auth import get_current_user_token, require_admin, security
from services.auth_service import AuthService
from schemas.user import (
    LoginRequest, LoginResponse, PasswordChangeRequest,
    UserCreate, UserResponse, UserListResponse, UserUpdate,
    UserSessionResponse, UserLoginLogResponse, UserPreferencesUpdate
)

router = APIRouter(prefix="/auth", tags=["Authentication"])

@router.post("/login", response_model=LoginResponse)
async def login(
    login_request: LoginRequest,
    request: Request,
    db: Session = Depends(get_db)
):
    """User login endpoint"""
    auth_service = AuthService(db)
    
    # Get client info
    ip_address = request.client.host
    user_agent = request.headers.get("user-agent")
    
    response, error_message = await auth_service.authenticate_user(
        login_request=login_request,
        ip_address=ip_address,
        user_agent=user_agent
    )
    
    if not response:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=error_message,
            headers={"WWW-Authenticate": "Bearer"}
        )
    
    return response

@router.post("/logout")
async def logout(
    current_user: dict = Depends(get_current_user_token),
    db: Session = Depends(get_db)
):
    """User logout endpoint"""
    auth_service = AuthService(db)
    token_jti = current_user.get("jti")
    
    if token_jti:
        success = await auth_service.logout_user(token_jti)
        if success:
            return {"message": "Successfully logged out"}
    
    return {"message": "Logout completed"}

@router.post("/logout-all")
async def logout_all_devices(
    current_user: dict = Depends(get_current_user_token),
    db: Session = Depends(get_db)
):
    """Logout from all devices"""
    auth_service = AuthService(db)
    user_id = current_user.get("user_id")
    current_jti = current_user.get("jti")
    
    count = await auth_service.logout_all_sessions(user_id, except_jti=current_jti)
    
    return {
        "message": f"Logged out from {count} other devices",
        "sessions_revoked": count
    }

@router.get("/me", response_model=UserResponse)
async def get_current_user(
    current_user: dict = Depends(get_current_user_token),
    db: Session = Depends(get_db)
):
    """Get current user profile"""
    auth_service = AuthService(db)
    user_id = current_user.get("user_id")
    
    user_profile = await auth_service.get_user_profile(user_id)
    if not user_profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    return user_profile

@router.put("/me", response_model=UserResponse)
async def update_current_user(
    user_update: UserUpdate,
    current_user: dict = Depends(get_current_user_token),
    db: Session = Depends(get_db)
):
    """Update current user profile"""
    from ...repositories.user_repository import UserRepository
    
    user_repo = UserRepository(db)
    user_id = current_user.get("user_id")
    
    # Get current user
    user = user_repo.get_by_id(user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Update user
    update_data = user_update.model_dump(exclude_unset=True)
    
    # Remove roles from regular user update (only admin can change roles)
    if "roles" in update_data and not current_user.get("roles", []).count("admin"):
        del update_data["roles"]
    
    updated_user = user_repo.update(user_id, update_data)
    
    return UserResponse.model_validate(updated_user)

@router.post("/change-password")
async def change_password(
    password_request: PasswordChangeRequest,
    current_user: dict = Depends(get_current_user_token),
    db: Session = Depends(get_db)
):
    """Change user password"""
    auth_service = AuthService(db)
    user_id = current_user.get("user_id")
    
    success = await auth_service.change_password(
        user_id=user_id,
        current_password=password_request.current_password,
        new_password=password_request.new_password
    )
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Current password is incorrect"
        )
    
    return {"message": "Password changed successfully"}

@router.put("/preferences")
async def update_preferences(
    preferences: UserPreferencesUpdate,
    current_user: dict = Depends(get_current_user_token),
    db: Session = Depends(get_db)
):
    """Update user preferences"""
    auth_service = AuthService(db)
    user_id = current_user.get("user_id")
    
    preferences_dict = preferences.model_dump(exclude_unset=True)
    
    success = await auth_service.update_user_preferences(user_id, preferences_dict)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed to update preferences"
        )
    
    return {"message": "Preferences updated successfully"}

@router.get("/sessions", response_model=List[UserSessionResponse])
async def get_my_sessions(
    current_user: dict = Depends(get_current_user_token),
    db: Session = Depends(get_db)
):
    """Get user's active sessions"""
    auth_service = AuthService(db)
    user_id = current_user.get("user_id")
    current_jti = current_user.get("jti")
    
    sessions = await auth_service.get_user_sessions(user_id)
    
    session_responses = []
    for session in sessions:
        session_data = UserSessionResponse.model_validate(session)
        session_data.is_current = (session.token_jti == current_jti)
        session_responses.append(session_data)
    
    return session_responses

@router.get("/login-history", response_model=List[UserLoginLogResponse])
async def get_my_login_history(
    limit: int = 20,
    current_user: dict = Depends(get_current_user_token),
    db: Session = Depends(get_db)
):
    """Get user's login history"""
    auth_service = AuthService(db)
    user_id = current_user.get("user_id")
    
    history = await auth_service.get_user_login_history(user_id, limit)
    
    return [UserLoginLogResponse.model_validate(log) for log in history]

# Admin endpoints
@router.post("/users", response_model=UserResponse, dependencies=[Depends(require_admin)])
async def create_user(
    user_data: UserCreate,
    current_user: dict = Depends(get_current_user_token),
    db: Session = Depends(get_db)
):
    """Create new user (Admin only)"""
    auth_service = AuthService(db)
    created_by = current_user.get("user_id")
    
    user = await auth_service.create_user(user_data, created_by)
    return user

@router.get("/users", response_model=UserListResponse, dependencies=[Depends(require_admin)])
async def list_users(
    page: int = 1,
    per_page: int = 20,
    role_filter: str = None,
    active_only: bool = False,
    db: Session = Depends(get_db)
):
    """List all users (Admin only)"""
    from ...repositories.user_repository import UserRepository
    
    user_repo = UserRepository(db)
    users, total = user_repo.get_users_paginated(page, per_page, role_filter, active_only)
    
    return UserListResponse(
        users=[UserResponse.model_validate(user) for user in users],
        total=total,
        page=page,
        per_page=per_page,
        pages=(total + per_page - 1) // per_page
    )

@router.get("/users/{user_id}", response_model=UserResponse, dependencies=[Depends(require_admin)])
async def get_user(
    user_id: int,
    db: Session = Depends(get_db)
):
    """Get user by ID (Admin only)"""
    from ...repositories.user_repository import UserRepository
    
    user_repo = UserRepository(db)
    user = user_repo.get_by_id(user_id)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    return UserResponse.model_validate(user)

@router.put("/users/{user_id}", response_model=UserResponse, dependencies=[Depends(require_admin)])
async def update_user(
    user_id: int,
    user_update: UserUpdate,
    db: Session = Depends(get_db)
):
    """Update user (Admin only)"""
    from ...repositories.user_repository import UserRepository
    
    user_repo = UserRepository(db)
    
    # Check if user exists
    user = user_repo.get_by_id(user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Update user
    update_data = user_update.model_dump(exclude_unset=True)
    updated_user = user_repo.update(user_id, update_data)
    
    return UserResponse.model_validate(updated_user)

@router.post("/users/{user_id}/unlock", dependencies=[Depends(require_admin)])
async def unlock_user(
    user_id: int,
    current_user: dict = Depends(get_current_user_token),
    db: Session = Depends(get_db)
):
    """Unlock user account (Admin only)"""
    auth_service = AuthService(db)
    admin_id = current_user.get("user_id")
    
    success = await auth_service.unlock_user_account(user_id, admin_id)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed to unlock user"
        )
    
    return {"message": "User account unlocked successfully"}

@router.post("/users/{user_id}/reset-password", dependencies=[Depends(require_admin)])
async def admin_reset_password(
    user_id: int,
    new_password: str,
    current_user: dict = Depends(get_current_user_token),
    db: Session = Depends(get_db)
):
    """Reset user password (Admin only)"""
    auth_service = AuthService(db)
    admin_id = current_user.get("user_id")
    
    success = await auth_service.reset_user_password(user_id, new_password, admin_id)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed to reset password"
        )
    
    return {"message": "Password reset successfully"}

@router.get("/validate-token")
async def validate_token(
    current_user: dict = Depends(get_current_user_token),
    db: Session = Depends(get_db)
):
    """Validate current token"""
    auth_service = AuthService(db)
    token_jti = current_user.get("jti")
    
    if token_jti:
        is_valid = await auth_service.validate_session(token_jti)
        return {
            "valid": is_valid,
            "user": current_user
        }
    
    return {"valid": False}