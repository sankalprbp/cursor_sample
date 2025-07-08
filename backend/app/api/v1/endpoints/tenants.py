"""
Tenants API Endpoints
Handles tenant management operations
"""

from typing import Any, List, Optional
from uuid import UUID
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, Query, status
from fastapi.security import HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.services.auth import auth_service, security
from app.services.tenant import tenant_service
from app.schemas.tenant import (
    TenantCreate,
    TenantUpdate,
    TenantResponse,
    TenantListResponse,
    TenantFilters,
    TenantStatistics,
    TenantApiKeyResponse
)
from app.models.user import UserRole
from app.models.tenant import TenantStatus


router = APIRouter()


@router.get("/", response_model=TenantListResponse)
async def list_tenants(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    status: Optional[TenantStatus] = None,
    search: Optional[str] = None,
    created_after: Optional[datetime] = None,
    created_before: Optional[datetime] = None,
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db)
) -> Any:
    """
    List tenants with optional filtering
    Only accessible by super admins
    """
    # Get current user
    current_user = await auth_service.get_current_user(db, credentials)
    
    # Check permissions - only super admins can list all tenants
    if current_user.role != UserRole.SUPER_ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    # Create filters
    filters = TenantFilters(
        status=status,
        search=search,
        created_after=created_after,
        created_before=created_before
    )
    
    # Get tenants
    result = await tenant_service.list_tenants(db, filters, skip, limit)
    
    # Convert to response format
    tenants_response = []
    for tenant in result["tenants"]:
        tenant_resp = TenantResponse(
            id=str(tenant.id),
            name=tenant.name,
            company_name=tenant.company_name,
            contact_email=tenant.contact_email,
            contact_phone=tenant.contact_phone,
            industry=tenant.industry,
            size=tenant.size,
            status=tenant.status.value,
            api_key=tenant.api_key,  # Only shown to super admins
            created_at=tenant.created_at.isoformat(),
            settings=tenant.settings.__dict__ if tenant.settings else None,
            subscription={
                "plan": tenant.subscription.plan.name if tenant.subscription and hasattr(tenant.subscription, 'plan') else None,
                "status": tenant.subscription.status if tenant.subscription else None
            } if tenant.subscription else None
        )
        tenants_response.append(tenant_resp)
    
    return TenantListResponse(
        tenants=tenants_response,
        total=result["total"],
        skip=result["skip"],
        limit=result["limit"]
    )


@router.get("/current", response_model=TenantResponse)
async def get_current_tenant(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db)
) -> Any:
    """
    Get current user's tenant information
    """
    # Get current user
    current_user = await auth_service.get_current_user(db, credentials)
    
    if not current_user.tenant_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User is not associated with any tenant"
        )
    
    # Get tenant
    tenant = await tenant_service.get_tenant(db, current_user.tenant_id)
    
    if not tenant:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tenant not found"
        )
    
    # Don't show API key to non-admins
    show_api_key = current_user.role in [UserRole.SUPER_ADMIN, UserRole.TENANT_ADMIN]
    
    return TenantResponse(
        id=str(tenant.id),
        name=tenant.name,
        company_name=tenant.company_name,
        contact_email=tenant.contact_email,
        contact_phone=tenant.contact_phone,
        industry=tenant.industry,
        size=tenant.size,
        status=tenant.status.value,
        api_key=tenant.api_key if show_api_key else None,
        created_at=tenant.created_at.isoformat(),
        settings=tenant.settings.__dict__ if tenant.settings else None,
        subscription={
            "plan": tenant.subscription.plan.name if tenant.subscription and hasattr(tenant.subscription, 'plan') else None,
            "status": tenant.subscription.status if tenant.subscription else None
        } if tenant.subscription else None
    )


@router.get("/{tenant_id}", response_model=TenantResponse)
async def get_tenant(
    tenant_id: UUID,
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db)
) -> Any:
    """
    Get tenant by ID
    Tenant admins can only access their own tenant
    """
    # Get current user
    current_user = await auth_service.get_current_user(db, credentials)
    
    # Check permissions
    if current_user.role == UserRole.TENANT_ADMIN and current_user.tenant_id != tenant_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    elif current_user.role == UserRole.TENANT_USER:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    # Get tenant
    tenant = await tenant_service.get_tenant(db, tenant_id)
    
    if not tenant:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tenant not found"
        )
    
    # Don't show API key to tenant admins of other tenants
    show_api_key = (current_user.role == UserRole.SUPER_ADMIN or 
                   (current_user.role == UserRole.TENANT_ADMIN and current_user.tenant_id == tenant_id))
    
    return TenantResponse(
        id=str(tenant.id),
        name=tenant.name,
        company_name=tenant.company_name,
        contact_email=tenant.contact_email,
        contact_phone=tenant.contact_phone,
        industry=tenant.industry,
        size=tenant.size,
        status=tenant.status.value,
        api_key=tenant.api_key if show_api_key else None,
        created_at=tenant.created_at.isoformat(),
        settings=tenant.settings.__dict__ if tenant.settings else None,
        subscription={
            "plan": tenant.subscription.plan.name if tenant.subscription and hasattr(tenant.subscription, 'plan') else None,
            "status": tenant.subscription.status if tenant.subscription else None
        } if tenant.subscription else None
    )


@router.post("/", response_model=TenantResponse)
async def create_tenant(
    tenant_create: TenantCreate,
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db)
) -> Any:
    """
    Create a new tenant
    Only accessible by super admins
    """
    # Get current user
    current_user = await auth_service.get_current_user(db, credentials)
    
    # Check permissions
    if current_user.role != UserRole.SUPER_ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    # Create tenant
    tenant = await tenant_service.create_tenant(db, tenant_create, current_user.id)
    
    return TenantResponse(
        id=str(tenant.id),
        name=tenant.name,
        company_name=tenant.company_name,
        contact_email=tenant.contact_email,
        contact_phone=tenant.contact_phone,
        industry=tenant.industry,
        size=tenant.size,
        status=tenant.status.value,
        api_key=tenant.api_key,
        created_at=tenant.created_at.isoformat(),
        settings=tenant.settings.__dict__ if tenant.settings else None,
        subscription={
            "plan": tenant.subscription.plan.name if tenant.subscription and hasattr(tenant.subscription, 'plan') else None,
            "status": tenant.subscription.status if tenant.subscription else None
        } if tenant.subscription else None
    )


@router.put("/{tenant_id}", response_model=TenantResponse)
async def update_tenant(
    tenant_id: UUID,
    tenant_update: TenantUpdate,
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db)
) -> Any:
    """
    Update tenant information
    Super admins can update any tenant, tenant admins can update their own
    """
    # Get current user
    current_user = await auth_service.get_current_user(db, credentials)
    
    # Check permissions
    if current_user.role == UserRole.TENANT_ADMIN and current_user.tenant_id != tenant_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    elif current_user.role == UserRole.TENANT_USER:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    # Tenant admins cannot change status
    if current_user.role == UserRole.TENANT_ADMIN and tenant_update.status is not None:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Cannot change tenant status"
        )
    
    # Update tenant
    tenant = await tenant_service.update_tenant(db, tenant_id, tenant_update)
    
    show_api_key = (current_user.role == UserRole.SUPER_ADMIN or 
                   (current_user.role == UserRole.TENANT_ADMIN and current_user.tenant_id == tenant_id))
    
    return TenantResponse(
        id=str(tenant.id),
        name=tenant.name,
        company_name=tenant.company_name,
        contact_email=tenant.contact_email,
        contact_phone=tenant.contact_phone,
        industry=tenant.industry,
        size=tenant.size,
        status=tenant.status.value,
        api_key=tenant.api_key if show_api_key else None,
        created_at=tenant.created_at.isoformat(),
        settings=tenant.settings.__dict__ if tenant.settings else None,
        subscription={
            "plan": tenant.subscription.plan.name if tenant.subscription and hasattr(tenant.subscription, 'plan') else None,
            "status": tenant.subscription.status if tenant.subscription else None
        } if tenant.subscription else None
    )


@router.delete("/{tenant_id}")
async def delete_tenant(
    tenant_id: UUID,
    hard_delete: bool = Query(False),
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db)
) -> Any:
    """
    Delete tenant (soft delete by default)
    Only accessible by super admins
    """
    # Get current user
    current_user = await auth_service.get_current_user(db, credentials)
    
    # Check permissions
    if current_user.role != UserRole.SUPER_ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    # Delete tenant
    success = await tenant_service.delete_tenant(db, tenant_id, not hard_delete)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete tenant"
        )
    
    return {"message": "Tenant deleted successfully"}


@router.post("/{tenant_id}/suspend")
async def suspend_tenant(
    tenant_id: UUID,
    reason: Optional[str] = Query(None, description="Reason for suspension"),
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db)
) -> Any:
    """
    Suspend tenant account
    Only accessible by super admins
    """
    # Get current user
    current_user = await auth_service.get_current_user(db, credentials)
    
    # Check permissions
    if current_user.role != UserRole.SUPER_ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    # Suspend tenant
    tenant = await tenant_service.suspend_tenant(db, tenant_id, reason)
    
    return {"message": "Tenant suspended successfully", "tenant_id": str(tenant.id)}


@router.post("/{tenant_id}/reactivate")
async def reactivate_tenant(
    tenant_id: UUID,
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db)
) -> Any:
    """
    Reactivate suspended tenant
    Only accessible by super admins
    """
    # Get current user
    current_user = await auth_service.get_current_user(db, credentials)
    
    # Check permissions
    if current_user.role != UserRole.SUPER_ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    # Reactivate tenant
    tenant = await tenant_service.reactivate_tenant(db, tenant_id)
    
    return {"message": "Tenant reactivated successfully", "tenant_id": str(tenant.id)}


@router.post("/{tenant_id}/regenerate-api-key", response_model=TenantApiKeyResponse)
async def regenerate_api_key(
    tenant_id: UUID,
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db)
) -> Any:
    """
    Regenerate tenant API key
    Super admins can regenerate any tenant's key, tenant admins can regenerate their own
    """
    # Get current user
    current_user = await auth_service.get_current_user(db, credentials)
    
    # Check permissions
    if current_user.role == UserRole.TENANT_ADMIN and current_user.tenant_id != tenant_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    elif current_user.role == UserRole.TENANT_USER:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    # Regenerate API key
    new_api_key = await tenant_service.regenerate_api_key(db, tenant_id)
    
    return TenantApiKeyResponse(api_key=new_api_key)


@router.get("/{tenant_id}/statistics", response_model=TenantStatistics)
async def get_tenant_statistics(
    tenant_id: UUID,
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db)
) -> Any:
    """
    Get tenant usage statistics
    Super admins can view any tenant's stats, tenant admins can view their own
    """
    # Get current user
    current_user = await auth_service.get_current_user(db, credentials)
    
    # Check permissions
    if current_user.role == UserRole.TENANT_ADMIN and current_user.tenant_id != tenant_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    elif current_user.role == UserRole.TENANT_USER:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    # Get statistics
    stats = await tenant_service.get_tenant_statistics(db, tenant_id)
    
    return TenantStatistics(**stats)