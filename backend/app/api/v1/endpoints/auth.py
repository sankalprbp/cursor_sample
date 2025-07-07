"""
Authentication API Endpoints
Handles user authentication, registration, and token management
"""

from datetime import timedelta
from typing import Any
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.config import settings
from app.services.auth import auth_service, security
from app.schemas.auth import (
    UserLogin, 
    UserCreate, 
    UserResponse, 
    Token, 
    RefreshTokenRequest,
    ChangePassword
)
from app.models.user import User


router = APIRouter()


@router.post("/login", response_model=Token)
async def login(
    user_login: UserLogin,
    db: AsyncSession = Depends(get_db)
) -> Any:
    """
    User login endpoint
    Returns JWT access and refresh tokens
    """
    # Authenticate user
    user = await auth_service.authenticate_user(
        db, user_login.email, user_login.password
    )
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User account is disabled"
        )
    
    # Create tokens
    access_token_expires = timedelta(
        minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
    )
    
    access_token = auth_service.create_access_token(
        data={"sub": str(user.id), "username": user.username},
        expires_delta=access_token_expires,
    )
    
    refresh_token = auth_service.create_refresh_token(
        data={"sub": str(user.id), "username": user.username}
    )
    
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
        "expires_in": settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60
    }


@router.post("/register", response_model=UserResponse)
async def register(
    user_create: UserCreate,
    db: AsyncSession = Depends(get_db)
) -> Any:
    """
    User registration endpoint
    Creates a new user account
    """
    user = await auth_service.create_user(db, user_create)
    
    return UserResponse(
        id=str(user.id),
        email=user.email,
        username=user.username,
        first_name=user.first_name,
        last_name=user.last_name,
        role=user.role,
        is_active=user.is_active,
        is_verified=user.is_verified,
        tenant_id=str(user.tenant_id) if user.tenant_id else None,
        created_at=user.created_at.isoformat()
    )


@router.post("/refresh", response_model=Token)
async def refresh_token(
    refresh_request: RefreshTokenRequest,
    db: AsyncSession = Depends(get_db)
) -> Any:
    """
    Refresh access token using refresh token
    """
    try:
        # Verify refresh token
        token_data = await auth_service.verify_token(refresh_request.refresh_token)
        if not token_data:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid refresh token"
            )
        
        # Get user
        from sqlalchemy import select
        stmt = select(User).where(User.id == token_data.user_id)
        result = await db.execute(stmt)
        user = result.scalar_one_or_none()
        
        if not user or not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found or inactive"
            )
        
        # Create new tokens
        access_token_expires = timedelta(
            minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
        )
        
        access_token = auth_service.create_access_token(
            data={"sub": str(user.id), "username": user.username},
            expires_delta=access_token_expires,
        )
        
        refresh_token = auth_service.create_refresh_token(
            data={"sub": str(user.id), "username": user.username}
        )
        
        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer",
            "expires_in": settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60
        }
        
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token"
        )


@router.get("/me", response_model=UserResponse)
async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db)
) -> Any:
    """
    Get current user information
    """
    user = await auth_service.get_current_user(db, credentials)
    
    return UserResponse(
        id=str(user.id),
        email=user.email,
        username=user.username,
        first_name=user.first_name,
        last_name=user.last_name,
        role=user.role,
        is_active=user.is_active,
        is_verified=user.is_verified,
        tenant_id=str(user.tenant_id) if user.tenant_id else None,
        created_at=user.created_at.isoformat()
    )


@router.post("/change-password")
async def change_password(
    password_data: ChangePassword,
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db)
) -> Any:
    """
    Change user password
    """
    user = await auth_service.get_current_user(db, credentials)
    
    # Verify current password
    if not auth_service.verify_password(
        password_data.current_password, 
        user.hashed_password
    ):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Incorrect current password"
        )
    
    # Update password
    user.hashed_password = auth_service.get_password_hash(
        password_data.new_password
    )
    
    await db.commit()
    
    return {"message": "Password updated successfully"}


@router.post("/logout")
async def logout(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db)
) -> Any:
    """
    Logout user (invalidate token)
    Note: In a production environment, you might want to implement token blacklisting
    """
    # Verify user is authenticated
    await auth_service.get_current_user(db, credentials)
    
    return {"message": "Successfully logged out"}