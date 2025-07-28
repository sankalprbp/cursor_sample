"""
Authentication Service
Handles user authentication, JWT tokens, and session management
"""

import secrets
import uuid
from datetime import datetime, timedelta, timezone
from typing import Optional, Union
from fastapi import HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError, jwt
from passlib.context import CryptContext
import bcrypt
from types import SimpleNamespace
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

# ---------------------------------------------------------------------------
# Ensure compatibility between `passlib` and modern versions of `bcrypt`.
# Newer `bcrypt` releases (>=4.0) removed the ``__about__`` module which
# older versions of ``passlib`` expect when checking the backend version.
# If missing, create a lightweight substitute so `passlib` doesn't emit
# noisy warnings or stack traces when initializing.
if not hasattr(bcrypt, "__about__"):
    bcrypt.__about__ = SimpleNamespace(
        __version__=getattr(bcrypt, "__version__", "")
    )

from app.core.config import settings
from app.core.redis_client import redis_client
from app.models.user import User, UserRole
from app.schemas.auth import TokenData, UserCreate, UserLogin


# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# HTTP Bearer token scheme
security = HTTPBearer()


class AuthService:
    """Authentication service for handling user auth operations"""
    
    def __init__(self):
        self.pwd_context = pwd_context
        self.redis = redis_client
    
    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """Verify a plain password against hashed password"""
        return self.pwd_context.verify(plain_password, hashed_password)
    
    def get_password_hash(self, password: str) -> str:
        """Generate password hash"""
        return self.pwd_context.hash(password)
    
    def generate_password_reset_token(self) -> str:
        """Generate a secure password reset token"""
        return secrets.token_urlsafe(32)
    
    def generate_email_verification_token(self) -> str:
        """Generate a secure email verification token"""
        return secrets.token_urlsafe(32)
    
    async def authenticate_user(
        self, 
        db: AsyncSession, 
        email: str, 
        password: str
    ) -> Optional[User]:
        """Authenticate user with email and password"""
        # Get user by email
        stmt = select(User).where(User.email == email, User.is_active == True)
        result = await db.execute(stmt)
        user = result.scalar_one_or_none()
        
        if not user:
            return None
        
        if not self.verify_password(password, user.hashed_password):
            return None
            
        # Update last login
        user.last_login = datetime.now(timezone.utc)
        await db.commit()
            
        return user
    
    def create_access_token(
        self, 
        data: dict, 
        expires_delta: Optional[timedelta] = None
    ) -> str:
        """Create JWT access token"""
        to_encode = data.copy()
        
        if expires_delta:
            expire = datetime.now(timezone.utc) + expires_delta
        else:
            expire = datetime.now(timezone.utc) + timedelta(
                minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
            )
        
        # Add unique token ID for blacklisting
        jti = str(uuid.uuid4())
        to_encode.update({
            "exp": expire,
            "jti": jti,
            "type": "access"
        })
        
        encoded_jwt = jwt.encode(
            to_encode, 
            settings.SECRET_KEY, 
            algorithm=settings.ALGORITHM
        )
        return encoded_jwt
    
    def create_refresh_token(
        self, 
        data: dict, 
        expires_delta: Optional[timedelta] = None
    ) -> str:
        """Create JWT refresh token"""
        to_encode = data.copy()
        
        if expires_delta:
            expire = datetime.now(timezone.utc) + expires_delta
        else:
            expire = datetime.now(timezone.utc) + timedelta(
                days=settings.REFRESH_TOKEN_EXPIRE_DAYS
            )
        
        # Add unique token ID for blacklisting
        jti = str(uuid.uuid4())
        to_encode.update({
            "exp": expire, 
            "jti": jti,
            "type": "refresh"
        })
        
        encoded_jwt = jwt.encode(
            to_encode, 
            settings.SECRET_KEY, 
            algorithm=settings.ALGORITHM
        )
        return encoded_jwt
    
    async def is_token_blacklisted(self, jti: str) -> bool:
        """Check if token is blacklisted"""
        blacklist_key = f"blacklist:token:{jti}"
        return await self.redis.exists(blacklist_key)
    
    async def blacklist_token(self, jti: str, exp: datetime) -> bool:
        """Add token to blacklist"""
        blacklist_key = f"blacklist:token:{jti}"
        # Calculate TTL until token expires
        ttl = int((exp - datetime.now(timezone.utc)).total_seconds())
        if ttl > 0:
            return await self.redis.set(blacklist_key, "true", expire=ttl)
        return True
    
    async def verify_token(self, token: str) -> Optional[TokenData]:
        """Verify and decode JWT token"""
        try:
            payload = jwt.decode(
                token,
                settings.SECRET_KEY,
                algorithms=[settings.ALGORITHM]
            )

            user_id: str = payload.get("sub")
            jti: str = payload.get("jti")

            if user_id is None or jti is None:
                return None

            # Check if token is blacklisted
            if await self.is_token_blacklisted(jti):
                return None

            # Check if user requested logout from all sessions
            logout_all_key = f"logout_all:{user_id}"
            if await self.redis.exists(logout_all_key):
                return None

            token_data = TokenData(user_id=user_id)
            return token_data

        except JWTError:
            return None
    
    async def get_current_user(
        self, 
        db: AsyncSession, 
        credentials: HTTPAuthorizationCredentials
    ) -> User:
        """Get current user from JWT token"""
        credentials_exception = HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
        
        try:
            token_data = await self.verify_token(credentials.credentials)
            if token_data is None:
                raise credentials_exception
                
        except JWTError:
            raise credentials_exception
        
        # Get user from database
        stmt = select(User).where(
            User.id == token_data.user_id, 
            User.is_active == True
        )
        result = await db.execute(stmt)
        user = result.scalar_one_or_none()
        
        if user is None:
            raise credentials_exception
            
        return user
    
    async def logout_user(self, token: str) -> bool:
        """Logout user by blacklisting token"""
        try:
            payload = jwt.decode(
                token,
                settings.SECRET_KEY,
                algorithms=[settings.ALGORITHM]
            )
            
            jti = payload.get("jti")
            exp = payload.get("exp")
            
            if jti and exp:
                exp_datetime = datetime.fromtimestamp(exp, tz=timezone.utc)
                return await self.blacklist_token(jti, exp_datetime)

        except JWTError:
            return False

        return False

    async def logout_all_sessions(self, user_id: str) -> bool:
        """Logout user from all sessions by setting a logout flag"""
        ttl = settings.REFRESH_TOKEN_EXPIRE_DAYS * 24 * 60 * 60
        key = f"logout_all:{user_id}"
        await self.redis.set(key, "true", expire=ttl)
        return True
    
    async def create_user(
        self, 
        db: AsyncSession, 
        user_create: UserCreate,
        tenant_id: Optional[str] = None,
        send_verification_email: bool = True
    ) -> User:
        """Create a new user"""
        # Check if user already exists
        stmt = select(User).where(User.email == user_create.email)
        result = await db.execute(stmt)
        existing_user = result.scalar_one_or_none()
        
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )
        
        # Hash password
        hashed_password = self.get_password_hash(user_create.password)
        
        # Generate email verification token
        email_verification_token = self.generate_email_verification_token()
        email_verification_expires = datetime.now(timezone.utc) + timedelta(hours=24)
        
        # Create user
        user = User(
            email=user_create.email,
            username=user_create.username,
            hashed_password=hashed_password,
            first_name=user_create.first_name,
            last_name=user_create.last_name,
            role=UserRole.TENANT_USER,  # Default role
            tenant_id=tenant_id,
            is_active=True,
            is_verified=False,
            email_verification_token=email_verification_token,
            email_verification_expires=email_verification_expires
        )
        
        db.add(user)
        await db.commit()
        await db.refresh(user)
        
        # Store verification token in Redis for quick lookup
        if send_verification_email:
            verification_key = f"verification:email:{email_verification_token}"
            await self.redis.set(
                verification_key, 
                str(user.id), 
                expire=24 * 60 * 60  # 24 hours
            )
            
            # Send verification email
            from app.services.email import email_service
            await email_service.send_verification_email(
                user.email, 
                email_verification_token, 
                user.username or user.first_name
            )
        
        return user
    
    async def verify_email(self, db: AsyncSession, token: str) -> bool:
        """Verify user email with token"""
        # Check token in Redis first
        verification_key = f"verification:email:{token}"
        user_id = await self.redis.get(verification_key)
        
        if not user_id:
            return False
        
        # Get user from database
        stmt = select(User).where(
            User.id == user_id,
            User.email_verification_token == token,
            User.email_verification_expires > datetime.now(timezone.utc)
        )
        result = await db.execute(stmt)
        user = result.scalar_one_or_none()
        
        if not user:
            return False
        
        # Mark user as verified
        user.is_verified = True
        user.email_verification_token = None
        user.email_verification_expires = None
        
        await db.commit()
        
        # Remove token from Redis
        await self.redis.delete(verification_key)
        
        # Send welcome email
        from app.services.email import email_service
        await email_service.send_welcome_email(
            user.email, 
            user.username or user.first_name
        )
        
        return True
    
    async def initiate_password_reset(self, db: AsyncSession, email: str) -> bool:
        """Initiate password reset process"""
        # Get user by email
        stmt = select(User).where(User.email == email, User.is_active == True)
        result = await db.execute(stmt)
        user = result.scalar_one_or_none()
        
        if not user:
            # Don't reveal if email exists or not
            return True
        
        # Generate reset token
        reset_token = self.generate_password_reset_token()
        reset_expires = datetime.now(timezone.utc) + timedelta(hours=1)  # 1 hour expiry
        
        # Update user with reset token
        user.password_reset_token = reset_token
        user.password_reset_expires = reset_expires
        
        await db.commit()
        
        # Store reset token in Redis for quick lookup
        reset_key = f"reset:password:{reset_token}"
        await self.redis.set(
            reset_key, 
            str(user.id), 
            expire=60 * 60  # 1 hour
        )
        
        # Send password reset email
        from app.services.email import email_service
        await email_service.send_password_reset_email(
            user.email, 
            reset_token, 
            user.username or user.first_name
        )
        
        return True
    
    async def reset_password(
        self, 
        db: AsyncSession, 
        token: str, 
        new_password: str
    ) -> bool:
        """Reset user password with token"""
        # Check token in Redis first
        reset_key = f"reset:password:{token}"
        user_id = await self.redis.get(reset_key)
        
        if not user_id:
            return False
        
        # Get user from database
        stmt = select(User).where(
            User.id == user_id,
            User.password_reset_token == token,
            User.password_reset_expires > datetime.now(timezone.utc)
        )
        result = await db.execute(stmt)
        user = result.scalar_one_or_none()
        
        if not user:
            return False
        
        # Update password
        user.hashed_password = self.get_password_hash(new_password)
        user.password_reset_token = None
        user.password_reset_expires = None
        
        await db.commit()
        
        # Remove token from Redis
        await self.redis.delete(reset_key)
        
        return True
    
    def check_permissions(self, user: User, required_role: UserRole) -> bool:
        """Check if user has required role/permissions"""
        role_hierarchy = {
            UserRole.TENANT_USER: 1,
            UserRole.AGENT: 1,
            UserRole.TENANT_ADMIN: 2,
            UserRole.SUPER_ADMIN: 3
        }
        
        user_level = role_hierarchy.get(user.role, 0)
        required_level = role_hierarchy.get(required_role, 0)
        
        return user_level >= required_level


# Global auth service instance
auth_service = AuthService()