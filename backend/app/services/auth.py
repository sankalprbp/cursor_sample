"""
Authentication Service
Handles user authentication, JWT tokens, and session management
"""

from datetime import datetime, timedelta, timezone
from typing import Optional, Union
from fastapi import HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.config import settings
from app.models.user import User
from app.schemas.auth import TokenData, UserCreate, UserLogin


# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# HTTP Bearer token scheme
security = HTTPBearer()


class AuthService:
    """Authentication service for handling user auth operations"""
    
    def __init__(self):
        self.pwd_context = pwd_context
    
    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """Verify a plain password against hashed password"""
        return self.pwd_context.verify(plain_password, hashed_password)
    
    def get_password_hash(self, password: str) -> str:
        """Generate password hash"""
        return self.pwd_context.hash(password)
    
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
        
        to_encode.update({"exp": expire})
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
        
        to_encode.update({"exp": expire, "type": "refresh"})
        encoded_jwt = jwt.encode(
            to_encode, 
            settings.SECRET_KEY, 
            algorithm=settings.ALGORITHM
        )
        return encoded_jwt
    
    async def verify_token(self, token: str) -> Optional[TokenData]:
        """Verify and decode JWT token"""
        try:
            payload = jwt.decode(
                token, 
                settings.SECRET_KEY, 
                algorithms=[settings.ALGORITHM]
            )
            user_id: str = payload.get("sub")
            if user_id is None:
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
    
    async def create_user(
        self, 
        db: AsyncSession, 
        user_create: UserCreate,
        tenant_id: Optional[str] = None
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
        
        # Create user
        user = User(
            email=user_create.email,
            username=user_create.username,
            hashed_password=hashed_password,
            first_name=user_create.first_name,
            last_name=user_create.last_name,
            role=user_create.role or "user",
            tenant_id=tenant_id,
            is_active=True,
            is_verified=False
        )
        
        db.add(user)
        await db.commit()
        await db.refresh(user)
        
        return user
    
    def check_permissions(self, user: User, required_role: str) -> bool:
        """Check if user has required role/permissions"""
        role_hierarchy = {
            "user": 1,
            "tenant_admin": 2,
            "super_admin": 3
        }
        
        user_level = role_hierarchy.get(user.role, 0)
        required_level = role_hierarchy.get(required_role, 0)
        
        return user_level >= required_level


# Global auth service instance
auth_service = AuthService()