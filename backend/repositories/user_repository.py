# backend/repositories/user_repository.py
"""
User Repository for Database Operations
Handles all user-related database queries and operations
"""

from typing import Optional, List, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import or_, and_, desc
from datetime import datetime, timedelta

from models.user import User, UserSession, UserLoginLog
from core.auth import PasswordManager
from repositories.base_repository import BaseRepository

class UserRepository(BaseRepository[User]):
    def __init__(self, db: Session):
        super().__init__(User, db)
    
    def get_by_username(self, username: str) -> Optional[User]:
        """Get user by username"""
        return self.db.query(User).filter(User.username == username).first()
    
    def get_by_email(self, email: str) -> Optional[User]:
        """Get user by email"""
        return self.db.query(User).filter(User.email == email).first()
    
    def get_by_employee_id(self, employee_id: str) -> Optional[User]:
        """Get user by employee ID"""
        return self.db.query(User).filter(User.employee_id == employee_id).first()
    
    def get_by_username_or_email(self, identifier: str) -> Optional[User]:
        """Get user by username or email"""
        return self.db.query(User).filter(
            or_(User.username == identifier, User.email == identifier)
        ).first()
    
    def create_user(self, user_data: dict) -> User:
        """Create a new user with hashed password"""
        # Hash password before storing
        if 'password' in user_data:
            user_data['hashed_password'] = PasswordManager.hash_password(user_data.pop('password'))
        
        user = User(**user_data)
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        return user
    
    def update_password(self, user_id: int, new_password: str) -> bool:
        """Update user password"""
        user = self.get_by_id(user_id)
        if user:
            user.hashed_password = PasswordManager.hash_password(new_password)
            user.password_changed_at = datetime.utcnow()
            user.failed_login_attempts = 0  # Reset failed attempts
            self.db.commit()
            return True
        return False
    
    def verify_password(self, user: User, password: str) -> bool:
        """Verify user password"""
        return PasswordManager.verify_password(password, user.hashed_password)
    
    def update_last_login(self, user_id: int) -> bool:
        """Update user's last login timestamp"""
        user = self.get_by_id(user_id)
        if user:
            user.last_login = datetime.utcnow()
            user.failed_login_attempts = 0  # Reset failed attempts on successful login
            self.db.commit()
            return True
        return False
    
    def increment_failed_login(self, user_id: int) -> int:
        """Increment failed login attempts"""
        user = self.get_by_id(user_id)
        if user:
            user.failed_login_attempts = (user.failed_login_attempts or 0) + 1
            
            # Lock account after 5 failed attempts for 30 minutes
            if user.failed_login_attempts >= 5:
                user.locked_until = datetime.utcnow() + timedelta(minutes=30)
            
            self.db.commit()
            return user.failed_login_attempts
        return 0
    
    def unlock_user(self, user_id: int) -> bool:
        """Unlock user account"""
        user = self.get_by_id(user_id)
        if user:
            user.locked_until = None
            user.failed_login_attempts = 0
            self.db.commit()
            return True
        return False
    
    def is_user_locked(self, user: User) -> bool:
        """Check if user account is locked"""
        if user.locked_until:
            if datetime.utcnow() < user.locked_until:
                return True
            else:
                # Auto-unlock if lock period has expired
                user.locked_until = None
                user.failed_login_attempts = 0
                self.db.commit()
        return False
    
    def get_users_with_role(self, role: str) -> List[User]:
        """Get all users with specific role"""
        return self.db.query(User).filter(
            User.roles.contains([role])
        ).all()
    
    def search_users(self, query: str, limit: int = 20) -> List[User]:
        """Search users by username, email, or full name"""
        return self.db.query(User).filter(
            or_(
                User.username.ilike(f"%{query}%"),
                User.email.ilike(f"%{query}%"),
                User.full_name.ilike(f"%{query}%"),
                User.employee_id.ilike(f"%{query}%")
            )
        ).limit(limit).all()
    
    def get_users_paginated(
        self, 
        page: int = 1, 
        per_page: int = 20,
        role_filter: Optional[str] = None,
        active_only: bool = False
    ) -> Tuple[List[User], int]:
        """Get paginated list of users"""
        query = self.db.query(User)
        
        if role_filter:
            query = query.filter(User.roles.contains([role_filter]))
        
        if active_only:
            query = query.filter(User.is_active == True)
        
        total = query.count()
        users = query.offset((page - 1) * per_page).limit(per_page).all()
        
        return users, total
    
    def update_user_preferences(self, user_id: int, preferences: dict) -> bool:
        """Update user preferences"""
        user = self.get_by_id(user_id)
        if user:
            current_preferences = user.preferences or {}
            current_preferences.update(preferences)
            user.preferences = current_preferences
            self.db.commit()
            return True
        return False

class UserSessionRepository:
    def __init__(self, db: Session):
        self.db = db
    
    def create_session(
        self, 
        user_id: int, 
        token_jti: str, 
        expires_at: datetime,
        user_agent: Optional[str] = None,
        ip_address: Optional[str] = None
    ) -> UserSession:
        """Create a new user session"""
        session = UserSession(
            user_id=user_id,
            token_jti=token_jti,
            expires_at=expires_at,
            user_agent=user_agent,
            ip_address=ip_address
        )
        self.db.add(session)
        self.db.commit()
        self.db.refresh(session)
        return session
    
    def get_session_by_jti(self, token_jti: str) -> Optional[UserSession]:
        """Get session by JWT ID"""
        return self.db.query(UserSession).filter(
            UserSession.token_jti == token_jti
        ).first()
    
    def revoke_session(self, token_jti: str) -> bool:
        """Revoke a session"""
        session = self.get_session_by_jti(token_jti)
        if session:
            session.is_revoked = True
            self.db.commit()
            return True
        return False
    
    def revoke_user_sessions(self, user_id: int, except_jti: Optional[str] = None) -> int:
        """Revoke all sessions for a user (except optionally one)"""
        query = self.db.query(UserSession).filter(
            UserSession.user_id == user_id,
            UserSession.is_revoked == False
        )
        
        if except_jti:
            query = query.filter(UserSession.token_jti != except_jti)
        
        count = query.count()
        query.update({"is_revoked": True})
        self.db.commit()
        
        return count
    
    def get_user_sessions(self, user_id: int, active_only: bool = True) -> List[UserSession]:
        """Get user's sessions"""
        query = self.db.query(UserSession).filter(UserSession.user_id == user_id)
        
        if active_only:
            query = query.filter(
                UserSession.is_revoked == False,
                UserSession.expires_at > datetime.utcnow()
            )
        
        return query.order_by(desc(UserSession.created_at)).all()
    
    def cleanup_expired_sessions(self) -> int:
        """Remove expired sessions"""
        count = self.db.query(UserSession).filter(
            UserSession.expires_at < datetime.utcnow()
        ).count()
        
        self.db.query(UserSession).filter(
            UserSession.expires_at < datetime.utcnow()
        ).delete()
        
        self.db.commit()
        return count

class UserLoginLogRepository:
    def __init__(self, db: Session):
        self.db = db
    
    def log_login_attempt(
        self,
        username: str,
        success: bool,
        user_id: Optional[int] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
        failure_reason: Optional[str] = None
    ) -> UserLoginLog:
        """Log a login attempt"""
        log_entry = UserLoginLog(
            user_id=user_id,
            username=username,
            success=success,
            ip_address=ip_address,
            user_agent=user_agent,
            failure_reason=failure_reason
        )
        self.db.add(log_entry)
        self.db.commit()
        self.db.refresh(log_entry)
        return log_entry
    
    def get_user_login_history(
        self, 
        user_id: int, 
        limit: int = 50
    ) -> List[UserLoginLog]:
        """Get user's login history"""
        return self.db.query(UserLoginLog).filter(
            UserLoginLog.user_id == user_id
        ).order_by(desc(UserLoginLog.login_time)).limit(limit).all()
    
    def get_failed_login_attempts(
        self,
        username: str,
        since: datetime
    ) -> int:
        """Get count of failed login attempts since timestamp"""
        return self.db.query(UserLoginLog).filter(
            UserLoginLog.username == username,
            UserLoginLog.success == False,
            UserLoginLog.login_time >= since
        ).count()
    
    def cleanup_old_logs(self, days_to_keep: int = 90) -> int:
        """Remove login logs older than specified days"""
        cutoff_date = datetime.utcnow() - timedelta(days=days_to_keep)
        
        count = self.db.query(UserLoginLog).filter(
            UserLoginLog.login_time < cutoff_date
        ).count()
        
        self.db.query(UserLoginLog).filter(
            UserLoginLog.login_time < cutoff_date
        ).delete()
        
        self.db.commit()
        return count