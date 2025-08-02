"""
Authentication API Endpoints
Handles user authentication, registration, and token management
"""

from datetime import timedelta
from typing import Any
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession
from jose.exceptions import JWTError

from app.api.deps import get_db
from app.core.config import settings
from app.core.security import require_verified_user, require_admin
from app.services.auth import auth_service
from app.api.deps import security
from app.schemas.auth import (
    UserLogin, 
    UserCreate, 
    UserResponse, 
    Token, 
    RefreshTokenRequest,
    ChangePassword,
    PasswordReset,
    PasswordResetConfirm,
    EmailVerification,
    ResendVerification,
    LogoutRequest,
    AuthResponse,
    UserRegistrationResponse,
    UpdateUserRole,
    UpdateUserTenant
)
from app.models.user import User
from app.models.user import UserRole


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


@router.post("/register", response_model=UserRegistrationResponse)
async def register(
    user_create: UserCreate,
    db: AsyncSession = Depends(get_db)
) -> Any:
    """
    User registration endpoint
    Creates a new user account and sends verification email
    """
    user = await auth_service.create_user(
        db, 
        user_create, 
        send_verification_email=True
    )
    
    user_response = UserResponse(
        id=str(user.id),
        email=user.email,
        username=user.username,
        first_name=user.first_name,
        last_name=user.last_name,
        role=user.role.value,
        is_active=user.is_active,
        is_verified=user.is_verified,
        tenant_id=str(user.tenant_id) if user.tenant_id else None,
        created_at=user.created_at.isoformat()
    )
    
    return UserRegistrationResponse(
        user=user_response,
        message="User registered successfully. Please check your email for verification instructions.",
        verification_required=True
    )


@router.post("/verify-email", response_model=AuthResponse)
async def verify_email(
    verification: EmailVerification,
    db: AsyncSession = Depends(get_db)
) -> Any:
    """
    Verify user email with token
    """
    success = await auth_service.verify_email(db, verification.token)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired verification token"
        )
    
    return AuthResponse(
        message="Email verified successfully",
        success=True
    )


@router.post("/resend-verification", response_model=AuthResponse)
async def resend_verification(
    resend_request: ResendVerification,
    db: AsyncSession = Depends(get_db)
) -> Any:
    """
    Resend email verification
    """
    from sqlalchemy import select
    
    # Get user by email
    stmt = select(User).where(User.email == resend_request.email)
    result = await db.execute(stmt)
    user = result.scalar_one_or_none()
    
    if not user:
        # Don't reveal if email exists
        return AuthResponse(
            message="If the email exists, a verification link has been sent",
            success=True
        )
    
    if user.is_verified:
        return AuthResponse(
            message="Email is already verified",
            success=True
        )
    
    # Generate new verification token
    from datetime import datetime, timezone, timedelta
    verification_token = auth_service.generate_email_verification_token()
    verification_expires = datetime.now(timezone.utc) + timedelta(hours=24)
    
    user.email_verification_token = verification_token
    user.email_verification_expires = verification_expires
    
    await db.commit()
    
    # Store in Redis
    verification_key = f"verification:email:{verification_token}"
    await auth_service.redis.set(
        verification_key, 
        str(user.id), 
        expire=24 * 60 * 60
    )
    
    return AuthResponse(
        message="Verification email sent successfully",
        success=True
    )


@router.post("/forgot-password", response_model=AuthResponse)
async def forgot_password(
    password_reset: PasswordReset,
    db: AsyncSession = Depends(get_db)
) -> Any:
    """
    Initiate password reset process
    """
    await auth_service.initiate_password_reset(db, password_reset.email)
    
    return AuthResponse(
        message="If the email exists, a password reset link has been sent",
        success=True
    )


@router.post("/reset-password", response_model=AuthResponse)
async def reset_password(
    reset_confirm: PasswordResetConfirm,
    db: AsyncSession = Depends(get_db)
) -> Any:
    """
    Reset password with token
    """
    success = await auth_service.reset_password(
        db, 
        reset_confirm.token, 
        reset_confirm.new_password
    )
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired reset token"
        )
    
    return AuthResponse(
        message="Password reset successfully",
        success=True
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
        token_data = await auth_service.verify_token(
            refresh_request.refresh_token,
            token_type="refresh",
        )
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
        
    except (JWTError, ValueError) as e:
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
        role=user.role.value,
        is_active=user.is_active,
        is_verified=user.is_verified,
        tenant_id=str(user.tenant_id) if user.tenant_id else None,
        created_at=user.created_at.isoformat()
    )


@router.post("/change-password", response_model=AuthResponse)
async def change_password(
    password_data: ChangePassword,
    current_user: User = Depends(require_verified_user),
    db: AsyncSession = Depends(get_db)
) -> Any:
    """
    Change user password (requires verified email)
    """
    # Verify current password
    if not auth_service.verify_password(
        password_data.current_password, 
        current_user.hashed_password
    ):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Incorrect current password"
        )
    
    # Update password
    current_user.hashed_password = auth_service.get_password_hash(
        password_data.new_password
    )
    
    await db.commit()
    
    return AuthResponse(
        message="Password updated successfully",
        success=True
    )


@router.post("/logout", response_model=AuthResponse)
async def logout(
    logout_request: LogoutRequest,
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db)
) -> Any:
    """
    Logout user by blacklisting the current token
    """
    # Verify user is authenticated
    await auth_service.get_current_user(db, credentials)
    
    # Blacklist the token
    token = logout_request.token or credentials.credentials
    success = await auth_service.logout_user(token)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed to logout"
        )
    
    return AuthResponse(
        message="Successfully logged out",
        success=True
    )


@router.post("/logout-all", response_model=AuthResponse)
async def logout_all_sessions(
    current_user: User = Depends(require_verified_user),
    db: AsyncSession = Depends(get_db)
) -> Any:
    """
    Logout from all sessions by blacklisting all user tokens
    Note: This is a simplified implementation. In production, you might want
    to track active sessions more granularly.
    """
    # In a full implementation, you would:
    # 1. Get all active tokens for the user
    # 2. Blacklist them all
    # 3. Optionally, increment a user session version to invalidate all tokens
    
    # Implement basic session management by setting a logout-all flag in Redis
    try:
        await auth_service.logout_all_sessions(str(current_user.id))
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error during logout process"
        )
    
    return AuthResponse(
        message="Logged out from all sessions successfully",
        success=True
    )


# Admin endpoints
@router.get("/admin/users", response_model=list[UserResponse])
async def list_users(
    current_user: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
    skip: int = 0,
    limit: int = 100
) -> Any:
    """
    List all users (admin only)
    """
    from sqlalchemy import select
    
    stmt = select(User)
    if current_user.role != UserRole.SUPER_ADMIN:
        # Tenant admins can only see users from their tenant
        stmt = stmt.where(User.tenant_id == current_user.tenant_id)
    
    stmt = stmt.offset(skip).limit(limit)
    result = await db.execute(stmt)
    users = result.scalars().all()
    
    return [
        UserResponse(
            id=str(user.id),
            email=user.email,
            username=user.username,
            first_name=user.first_name,
            last_name=user.last_name,
            role=user.role.value,
            is_active=user.is_active,
            is_verified=user.is_verified,
            tenant_id=str(user.tenant_id) if user.tenant_id else None,
            created_at=user.created_at.isoformat()
        )
        for user in users
    ]


@router.patch("/admin/users/{user_id}/activate", response_model=AuthResponse)
async def activate_user(
    user_id: str,
    current_user: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db)
) -> Any:
    """
    Activate/deactivate user (admin only)
    """
    from sqlalchemy import select
    
    stmt = select(User).where(User.id == user_id)
    if current_user.role != UserRole.SUPER_ADMIN:
        # Tenant admins can only manage users from their tenant
        stmt = stmt.where(User.tenant_id == current_user.tenant_id)
    
    result = await db.execute(stmt)
    user = result.scalar_one_or_none()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    user.is_active = not user.is_active
    await db.commit()
    
    return AuthResponse(
        message=f"User {'activated' if user.is_active else 'deactivated'} successfully",
        success=True
    )


@router.patch("/admin/users/{user_id}/role", response_model=AuthResponse)
async def update_user_role(
    user_id: str,
    role_update: UpdateUserRole,
    current_user: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db)
) -> Any:
    """Promote or demote a user's role"""
    from sqlalchemy import select

    stmt = select(User).where(User.id == user_id)
    if current_user.role != UserRole.SUPER_ADMIN:
        stmt = stmt.where(User.tenant_id == current_user.tenant_id)

    result = await db.execute(stmt)
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    if current_user.role != UserRole.SUPER_ADMIN and role_update.role == UserRole.SUPER_ADMIN:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Cannot promote to super admin")

    user.role = role_update.role
    await db.commit()

    return AuthResponse(message="User role updated successfully", success=True)


@router.patch("/admin/users/{user_id}/tenant", response_model=AuthResponse)
async def update_user_tenant(
    user_id: str,
    tenant_update: UpdateUserTenant,
    current_user: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db)
) -> Any:
    """Change a user's tenant membership"""
    from sqlalchemy import select

    stmt = select(User).where(User.id == user_id)
    if current_user.role != UserRole.SUPER_ADMIN:
        stmt = stmt.where(User.tenant_id == current_user.tenant_id)

    result = await db.execute(stmt)
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    if current_user.role != UserRole.SUPER_ADMIN and tenant_update.tenant_id and str(current_user.tenant_id) != str(tenant_update.tenant_id):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Cannot move user to another tenant")

    user.tenant_id = tenant_update.tenant_id
    await db.commit()

    return AuthResponse(message="User tenant updated successfully", success=True)