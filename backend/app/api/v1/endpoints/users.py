"""
Users API Endpoints
Handles user management operations
"""

from typing import Any, List, Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, Query, status
from fastapi.security import HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.services.auth import auth_service, security
from app.services.user import user_service
from app.schemas.user import (
    UserCreate,
    UserUpdate,
    UserResponse,
    UserListResponse,
    UserFilters,
    UserPermissions
)
from app.models.user import User, UserRole


router = APIRouter()


@router.get("/", response_model=UserListResponse)
async def list_users(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    role: Optional[UserRole] = None,
    is_active: Optional[bool] = None,
    is_verified: Optional[bool] = None,
    search: Optional[str] = None,
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db)
) -> Any:
    """
    List users with optional filtering
    Requires authentication and appropriate permissions
    """
    # Get current user
    current_user = await auth_service.get_current_user(db, credentials)
    
    # Check permissions
    if current_user.role == UserRole.TENANT_USER:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    # Apply tenant filter for non-super admins
    tenant_id = None if current_user.role == UserRole.SUPER_ADMIN else current_user.tenant_id
    
    # Create filters
    filters = UserFilters(
        role=role,
        is_active=is_active,
        is_verified=is_verified,
        search=search,
        tenant_id=tenant_id
    )
    
    # Get users
    result = await user_service.list_users(db, tenant_id, filters, skip, limit)
    
    # Convert to response format
    users_response = []
    for user in result["users"]:
        users_response.append(UserResponse(
            id=str(user.id),
            email=user.email,
            username=user.username,
            first_name=user.first_name,
            last_name=user.last_name,
            role=user.role.value,
            is_active=user.is_active,
            is_verified=user.is_verified,
            tenant_id=str(user.tenant_id) if user.tenant_id else None,
            created_at=user.created_at.isoformat(),
            last_login=user.last_login.isoformat() if user.last_login else None
        ))
    
    return UserListResponse(
        users=users_response,
        total=result["total"],
        skip=result["skip"],
        limit=result["limit"]
    )


@router.get("/{user_id}", response_model=UserResponse)
async def get_user(
    user_id: UUID,
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db)
) -> Any:
    """
    Get user by ID
    Users can only access their own information unless they have admin permissions
    """
    # Get current user
    current_user = await auth_service.get_current_user(db, credentials)
    
    # Check permissions
    if current_user.role == UserRole.TENANT_USER and current_user.id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    # Apply tenant filter for non-super admins
    tenant_id = None if current_user.role == UserRole.SUPER_ADMIN else current_user.tenant_id
    
    # Get user
    user = await user_service.get_user(db, user_id, tenant_id)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
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
        created_at=user.created_at.isoformat(),
        last_login=user.last_login.isoformat() if user.last_login else None
    )


@router.post("/", response_model=UserResponse)
async def create_user(
    user_create: UserCreate,
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db)
) -> Any:
    """
    Create a new user
    Requires admin permissions
    """
    # Get current user
    current_user = await auth_service.get_current_user(db, credentials)
    
    # Check permissions
    if current_user.role == UserRole.TENANT_USER:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    # Tenant admins can only create users in their tenant
    if current_user.role == UserRole.TENANT_ADMIN:
        user_create.tenant_id = current_user.tenant_id
    
    # Create user
    user = await user_service.create_user(
        db, 
        user_create, 
        user_create.tenant_id,
        current_user.id
    )
    
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
        created_at=user.created_at.isoformat(),
        last_login=user.last_login.isoformat() if user.last_login else None
    )


@router.put("/{user_id}", response_model=UserResponse)
async def update_user(
    user_id: UUID,
    user_update: UserUpdate,
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db)
) -> Any:
    """
    Update user information
    Users can update their own information, admins can update anyone
    """
    # Get current user
    current_user = await auth_service.get_current_user(db, credentials)
    
    # Check permissions
    if current_user.role == UserRole.TENANT_USER and current_user.id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    # Regular users cannot change their role
    if current_user.role == UserRole.TENANT_USER and user_update.role is not None:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Cannot change own role"
        )
    
    # Apply tenant filter for non-super admins
    tenant_id = None if current_user.role == UserRole.SUPER_ADMIN else current_user.tenant_id
    
    # Update user
    user = await user_service.update_user(db, user_id, user_update, tenant_id)
    
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
        created_at=user.created_at.isoformat(),
        last_login=user.last_login.isoformat() if user.last_login else None
    )


@router.delete("/{user_id}")
async def delete_user(
    user_id: UUID,
    hard_delete: bool = Query(False),
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db)
) -> Any:
    """
    Delete user (soft delete by default)
    Requires admin permissions
    """
    # Get current user
    current_user = await auth_service.get_current_user(db, credentials)
    
    # Check permissions
    if current_user.role == UserRole.TENANT_USER:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    # Cannot delete self
    if current_user.id == user_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot delete own account"
        )
    
    # Apply tenant filter for non-super admins
    tenant_id = None if current_user.role == UserRole.SUPER_ADMIN else current_user.tenant_id
    
    # Delete user
    success = await user_service.delete_user(db, user_id, tenant_id, not hard_delete)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete user"
        )
    
    return {"message": "User deleted successfully"}


@router.post("/{user_id}/verify")
async def verify_user(
    user_id: UUID,
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db)
) -> Any:
    """
    Verify user email
    Requires admin permissions
    """
    # Get current user
    current_user = await auth_service.get_current_user(db, credentials)
    
    # Check permissions
    if current_user.role == UserRole.TENANT_USER:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    # Verify user
    user = await user_service.verify_user(db, user_id)
    
    return {"message": "User verified successfully", "user_id": str(user.id)}


@router.get("/{user_id}/permissions", response_model=UserPermissions)
async def get_user_permissions(
    user_id: UUID,
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db)
) -> Any:
    """
    Get user permissions based on their role
    Users can only check their own permissions unless they have admin permissions
    """
    # Get current user
    current_user = await auth_service.get_current_user(db, credentials)
    
    # Check permissions
    if current_user.role == UserRole.TENANT_USER and current_user.id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    # Get permissions
    permissions = await user_service.get_user_permissions(db, user_id)
    
    return UserPermissions(
        user_id=str(user_id),
        permissions=permissions
    )