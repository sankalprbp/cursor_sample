"""
API Dependencies
Common dependencies for authentication, database, and permissions
"""

from typing import Optional, Generator
from uuid import UUID

from fastapi import Depends, HTTPException, status, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.database import get_db as get_database_session
from app.models.user import User, UserRole
from app.models.tenant import Tenant
from app.services.auth import auth_service
from app.services.user import UserService
from app.services.tenant import TenantService

# Security scheme
security = HTTPBearer()


async def get_db() -> AsyncSession:
    """Get database session"""
    async for session in get_database_session():
        yield session


async def get_current_user(
    db: AsyncSession = Depends(get_db)
) -> User:
    """
    Get a default user to bypass authentication for public dashboard.
    This function will fetch the 'admin@demo.com' user and return it.
    """
    
    # Fetch the default tenant admin user
    user_service = UserService()
    user = await user_service.get_user_by_email(db, "admin@demo.com")
    
    if user is None:
        # This might happen if sample data hasn't been created yet.
        # In a real scenario, we might want to create it here, but for now,
        # we'll raise an exception to make it clear that the default user is missing.
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Default user 'admin@demo.com' not found. Please ensure sample data is loaded.",
        )
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Default user is not active."
        )
    
    return user


async def get_current_active_user(
    current_user: User = Depends(get_current_user)
) -> User:
    """Get current active user (additional check for active status)"""
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user"
        )
    return current_user


async def get_current_tenant(
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
) -> Tenant:
    """Get current user's tenant"""
    if not current_user.tenant_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User is not associated with any tenant"
        )
    
    tenant_service = TenantService()
    tenant = await tenant_service.get_tenant(db, current_user.tenant_id)
    
    if not tenant:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tenant not found"
        )
    
    if not tenant.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Tenant is not active"
        )
    
    return tenant


async def get_super_admin_user(
    current_user: User = Depends(get_current_active_user)
) -> User:
    """Require super admin privileges"""
    if not current_user.is_super_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Super admin privileges required"
        )
    return current_user


async def get_admin_user(
    current_user: User = Depends(get_current_active_user)
) -> User:
    """Require admin privileges (super admin or tenant admin)"""
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin privileges required"
        )
    return current_user


async def get_tenant_admin_user(
    current_user: User = Depends(get_current_active_user),
    tenant: Tenant = Depends(get_current_tenant)
) -> User:
    """Require tenant admin privileges within current tenant"""
    if current_user.role not in [UserRole.SUPER_ADMIN, UserRole.TENANT_ADMIN]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Tenant admin privileges required"
        )
    
    if current_user.role == UserRole.TENANT_ADMIN and current_user.tenant_id != tenant.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied for this tenant"
        )
    
    return current_user


def require_permission(action: str, resource: str = None):
    """Permission dependency factory"""
    async def check_permission(
        current_user: User = Depends(get_current_active_user)
    ) -> User:
        if not current_user.has_permission(action, resource):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Permission denied: {action} on {resource or 'resource'}"
            )
        return current_user
    
    return check_permission


async def get_optional_user(
    request: Request,
    db: AsyncSession = Depends(get_db)
) -> Optional[User]:
    """Get current user if authenticated, otherwise None"""
    
    authorization = request.headers.get("Authorization")
    if not authorization or not authorization.startswith("Bearer "):
        return None
    
    token = authorization.split("Bearer ")[1]
    
    try:
        token_data = await auth_service.verify_token(
            token,
            token_type="access",
        )
        if not token_data:
            return None
        user_id = token_data.user_id
    except JWTError:
        return None
    
    try:
        user_service = UserService(db)
        user = await user_service.get_by_id(UUID(user_id))
        return user if user and user.is_active else None
    except (ValueError, Exception):
        return None


class TenantScopedDependency:
    """Dependency to ensure operations are scoped to user's tenant"""
    
    def __init__(self, require_admin: bool = False):
        self.require_admin = require_admin
    
    async def __call__(
        self,
        current_user: User = Depends(get_current_active_user),
        tenant: Tenant = Depends(get_current_tenant)
    ) -> tuple[User, Tenant]:
        
        if self.require_admin and not current_user.is_admin:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Admin privileges required"
            )
        
        return current_user, tenant


# Pre-configured dependency instances
tenant_scoped = TenantScopedDependency(require_admin=False)
tenant_admin_scoped = TenantScopedDependency(require_admin=True)


def validate_tenant_resource(resource_tenant_id: UUID):
    """Validate that a resource belongs to the current user's tenant"""
    async def check_tenant_access(
        current_user: User = Depends(get_current_active_user)
    ) -> User:
        if current_user.role == UserRole.SUPER_ADMIN:
            return current_user
        
        if current_user.tenant_id != resource_tenant_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied: resource belongs to different tenant"
            )
        
        return current_user
    
    return check_tenant_access


async def check_tenant_limits(
    tenant: Tenant = Depends(get_current_tenant)
) -> Tenant:
    """Check if tenant has not exceeded their limits"""
    if not tenant.can_make_call():
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Tenant has reached usage limits or account is not active"
        )
    
    return tenant


async def validate_api_key(
    request: Request,
    db: AsyncSession = Depends(get_db)
) -> Optional[User]:
    """Validate API key for public endpoints"""
    api_key = request.headers.get("X-API-Key")
    if not api_key:
        return None
    
    # Implement API key validation logic
    # This would typically involve checking against a database of API keys
    # For now, return None (not implemented)
    return None