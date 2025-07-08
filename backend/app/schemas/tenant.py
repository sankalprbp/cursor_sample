"""
Tenant Schemas
Pydantic models for tenant-related API operations
"""

from typing import Optional, List, Dict, Any
from datetime import datetime
from uuid import UUID
from pydantic import BaseModel, EmailStr, constr, validator
from enum import Enum

from app.models.tenant import TenantStatus


class TenantSettingsSchema(BaseModel):
    """Schema for tenant settings"""
    business_hours: Optional[Dict[str, Any]] = {}
    timezone: Optional[str] = "UTC"
    language: Optional[str] = "en"
    voice_settings: Optional[Dict[str, Any]] = {}
    call_settings: Optional[Dict[str, Any]] = {}
    integration_settings: Optional[Dict[str, Any]] = {}


class TenantBase(BaseModel):
    """Base tenant schema with common fields"""
    name: constr(min_length=3, max_length=100, regex="^[a-zA-Z0-9_-]+$")
    company_name: constr(min_length=1, max_length=200)
    contact_email: EmailStr
    contact_phone: Optional[constr(max_length=20)] = None
    industry: Optional[str] = None
    size: Optional[str] = None


class TenantCreate(TenantBase):
    """Schema for creating a new tenant"""
    plan_id: Optional[UUID] = None
    business_hours: Optional[Dict[str, Any]] = {}
    timezone: Optional[str] = "UTC"
    language: Optional[str] = "en"
    voice_settings: Optional[Dict[str, Any]] = {}
    call_settings: Optional[Dict[str, Any]] = {}
    integration_settings: Optional[Dict[str, Any]] = {}


class TenantUpdate(BaseModel):
    """Schema for updating tenant information"""
    company_name: Optional[constr(min_length=1, max_length=200)] = None
    contact_email: Optional[EmailStr] = None
    contact_phone: Optional[constr(max_length=20)] = None
    industry: Optional[str] = None
    size: Optional[str] = None
    status: Optional[TenantStatus] = None
    settings: Optional[TenantSettingsSchema] = None


class TenantResponse(BaseModel):
    """Schema for tenant responses"""
    id: str
    name: str
    company_name: str
    contact_email: str
    contact_phone: Optional[str] = None
    industry: Optional[str] = None
    size: Optional[str] = None
    status: str
    api_key: Optional[str] = None  # Only show to admins
    created_at: str
    settings: Optional[TenantSettingsSchema] = None
    subscription: Optional[Dict[str, Any]] = None
    
    class Config:
        orm_mode = True


class TenantListResponse(BaseModel):
    """Schema for paginated tenant list"""
    tenants: List[TenantResponse]
    total: int
    skip: int
    limit: int


class TenantFilters(BaseModel):
    """Schema for tenant list filtering"""
    status: Optional[TenantStatus] = None
    search: Optional[str] = None
    created_after: Optional[datetime] = None
    created_before: Optional[datetime] = None


class TenantStatistics(BaseModel):
    """Schema for tenant statistics"""
    tenant_id: str
    name: str
    status: str
    user_count: int
    created_at: str
    subscription: Dict[str, Any]
    # Additional stats can be added here
    call_count: Optional[int] = 0
    knowledge_base_size: Optional[int] = 0
    monthly_usage: Optional[Dict[str, Any]] = {}


class TenantApiKeyResponse(BaseModel):
    """Schema for API key regeneration response"""
    api_key: str
    message: str = "API key regenerated successfully"


class TenantSubscriptionUpdate(BaseModel):
    """Schema for updating tenant subscription"""
    plan_id: UUID
    payment_method_id: Optional[str] = None
    cancel_at_period_end: Optional[bool] = False