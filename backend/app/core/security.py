"""
Security and Role-Based Access Control
Provides decorators and utilities for managing user permissions and roles
"""

from functools import wraps
from typing import List, Optional, Callable, Any
from fastapi import HTTPException, status, Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.models.user import User, UserRole
from app.api.deps import get_db


class Permission:
    """Permission constants"""
    READ = "read"
    CREATE = "create"
    UPDATE = "update"
    DELETE = "delete"
    ADMIN = "admin"
    MANAGE_USERS = "manage_users"
    MANAGE_TENANTS = "manage_tenants"
    MANAGE_BILLING = "manage_billing"
    VIEW_ANALYTICS = "view_analytics"


class ResourceType:
    """Resource type constants"""
    USER = "user"
    TENANT = "tenant"
    CALL = "call"
    WEBHOOK = "webhook"
    KNOWLEDGE_BASE = "knowledge_base"
    VOICE_AGENT = "voice_agent"
    BILLING = "billing"


def require_role(required_role: UserRole):
    """
    Decorator to require a specific role or higher
    
    Args:
        required_role: Minimum role required
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Extract user from dependencies if not already provided
            user = None
            for arg in args:
                if isinstance(arg, User):
                    user = arg
                    break
            
            if not user:
                # Try to get from kwargs
                user = kwargs.get('current_user')
            
            if not user:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Authentication required"
                )
            
            role_hierarchy = {
                UserRole.TENANT_USER: 1,
                UserRole.AGENT: 1,
                UserRole.TENANT_ADMIN: 2,
                UserRole.SUPER_ADMIN: 3
            }
            
            user_level = role_hierarchy.get(user.role, 0)
            required_level = role_hierarchy.get(required_role, 0)
            
            if user_level < required_level:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"Insufficient permissions. {required_role.value} role required"
                )
            
            return await func(*args, **kwargs)
        
        return wrapper
    return decorator


def require_permission(permission: str, resource_type: Optional[str] = None):
    """
    Decorator to require a specific permission
    
    Args:
        permission: Permission required (e.g., 'read', 'write', 'admin')
        resource_type: Optional resource type for context
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Extract user from dependencies
            user = None
            for arg in args:
                if isinstance(arg, User):
                    user = arg
                    break
            
            if not user:
                user = kwargs.get('current_user')
            
            if not user:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Authentication required"
                )
            
            if not user.has_permission(permission, resource_type):
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"Permission denied: {permission} on {resource_type or 'resource'}"
                )
            
            return await func(*args, **kwargs)
        
        return wrapper
    return decorator


def require_verified_email():
    """Decorator to require verified email"""
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(*args, **kwargs):
            user = None
            for arg in args:
                if isinstance(arg, User):
                    user = arg
                    break
            
            if not user:
                user = kwargs.get('current_user')
            
            if not user:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Authentication required"
                )
            
            if not user.is_verified:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Email verification required"
                )
            
            return await func(*args, **kwargs)
        
        return wrapper
    return decorator


def require_tenant_access(allow_super_admin: bool = True):
    """
    Decorator to ensure user has access to tenant resources
    
    Args:
        allow_super_admin: Whether super admins can access any tenant
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(*args, **kwargs):
            user = None
            tenant_id = None
            
            # Extract user and tenant_id from arguments
            for arg in args:
                if isinstance(arg, User):
                    user = arg
                elif isinstance(arg, str):
                    # Assume it's tenant_id if it's a string
                    tenant_id = arg
            
            if not user:
                user = kwargs.get('current_user')
            
            if not tenant_id:
                tenant_id = kwargs.get('tenant_id')
            
            if not user:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Authentication required"
                )
            
            # Super admins can access any tenant if allowed
            if allow_super_admin and user.role == UserRole.SUPER_ADMIN:
                return await func(*args, **kwargs)
            
            # Check if user belongs to the tenant
            if tenant_id and str(user.tenant_id) != str(tenant_id):
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Access denied: user does not belong to this tenant"
                )
            
            return await func(*args, **kwargs)
        
        return wrapper
    return decorator


# FastAPI dependency factories for role-based access control

def require_super_admin_dependency():
    """FastAPI dependency that requires super admin role"""
    async def dependency(
        credentials: HTTPAuthorizationCredentials = Depends(HTTPBearer()),
        db = Depends(get_db)
    ) -> User:
        from app.services.auth import auth_service
        user = await auth_service.get_current_user(db, credentials)
        
        if user.role != UserRole.SUPER_ADMIN:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Super admin privileges required"
            )
        
        return user
    
    return dependency


def require_admin_dependency():
    """FastAPI dependency that requires admin role (tenant or super admin)"""
    async def dependency(
        credentials: HTTPAuthorizationCredentials = Depends(HTTPBearer()),
        db = Depends(get_db)
    ) -> User:
        from app.services.auth import auth_service
        user = await auth_service.get_current_user(db, credentials)
        
        if user.role not in [UserRole.SUPER_ADMIN, UserRole.TENANT_ADMIN]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Admin privileges required"
            )
        
        return user
    
    return dependency


def require_tenant_admin_dependency():
    """FastAPI dependency that requires tenant admin role for the user's tenant"""
    async def dependency(
        credentials: HTTPAuthorizationCredentials = Depends(HTTPBearer()),
        db = Depends(get_db)
    ) -> User:
        from app.services.auth import auth_service
        user = await auth_service.get_current_user(db, credentials)
        
        if user.role == UserRole.SUPER_ADMIN:
            return user
        
        if user.role != UserRole.TENANT_ADMIN:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Tenant admin privileges required"
            )
        
        return user
    
    return dependency


def require_verified_user_dependency():
    """FastAPI dependency that requires verified email"""
    async def dependency(
        credentials: HTTPAuthorizationCredentials = Depends(HTTPBearer()),
        db = Depends(get_db)
    ) -> User:
        from app.services.auth import auth_service
        user = await auth_service.get_current_user(db, credentials)
        
        if not user.is_verified:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Email verification required"
            )
        
        return user
    
    return dependency


def check_resource_access(
    user: User, 
    resource_tenant_id: str, 
    required_permission: str = Permission.READ
) -> bool:
    """
    Check if user has access to a resource
    
    Args:
        user: Current user
        resource_tenant_id: Tenant ID of the resource
        required_permission: Permission required
    
    Returns:
        True if user has access, False otherwise
    """
    # Super admins have access to everything
    if user.role == UserRole.SUPER_ADMIN:
        return True
    
    # Users can only access resources from their tenant
    if str(user.tenant_id) != str(resource_tenant_id):
        return False
    
    # Check specific permission
    return user.has_permission(required_permission)


def validate_resource_ownership(
    user: User,
    resource_user_id: str,
    allow_admin_override: bool = True
) -> bool:
    """
    Validate that user owns a resource or has admin privileges
    
    Args:
        user: Current user
        resource_user_id: User ID that owns the resource
        allow_admin_override: Whether admins can access any user's resources
    
    Returns:
        True if user has access, False otherwise
    """
    # User owns the resource
    if str(user.id) == str(resource_user_id):
        return True
    
    # Admin override
    if allow_admin_override and user.is_admin:
        return True
    
    return False


class RoleChecker:
    """Utility class for role checking"""
    
    def __init__(self, allowed_roles: List[UserRole]):
        self.allowed_roles = allowed_roles
    
    def __call__(self, current_user: User = Depends(require_verified_user_dependency())) -> User:
        if current_user.role not in self.allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Access denied. Required roles: {[role.value for role in self.allowed_roles]}"
            )
        return current_user


class PermissionChecker:
    """Utility class for permission checking"""
    
    def __init__(self, required_permission: str, resource_type: Optional[str] = None):
        self.required_permission = required_permission
        self.resource_type = resource_type
    
    def __call__(self, current_user: User = Depends(require_verified_user_dependency())) -> User:
        if not current_user.has_permission(self.required_permission, self.resource_type):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Permission denied: {self.required_permission} on {self.resource_type or 'resource'}"
            )
        return current_user


# Pre-configured dependency instances
require_super_admin = require_super_admin_dependency()
require_admin = require_admin_dependency()
require_tenant_admin = require_tenant_admin_dependency()
require_verified_user = require_verified_user_dependency()

# Role-based checkers
allow_super_admin_only = RoleChecker([UserRole.SUPER_ADMIN])
allow_admin_roles = RoleChecker([UserRole.SUPER_ADMIN, UserRole.TENANT_ADMIN])
allow_all_roles = RoleChecker([UserRole.SUPER_ADMIN, UserRole.TENANT_ADMIN, UserRole.TENANT_USER, UserRole.AGENT])

# Permission-based checkers
require_user_management = PermissionChecker(Permission.MANAGE_USERS, ResourceType.USER)
require_tenant_management = PermissionChecker(Permission.MANAGE_TENANTS, ResourceType.TENANT)
require_billing_access = PermissionChecker(Permission.MANAGE_BILLING, ResourceType.BILLING)