"""
User Schemas
Pydantic models for user-related API operations
"""

from typing import Optional, List
from datetime import datetime
from uuid import UUID
from pydantic import BaseModel, EmailStr, constr, validator
from enum import Enum

from app.models.user import UserRole


class UserBase(BaseModel):
    """Base user schema with common fields"""
    email: EmailStr
    username: constr(min_length=3, max_length=50, regex="^[a-zA-Z0-9_-]+$")
    first_name: constr(min_length=1, max_length=100)
    last_name: constr(min_length=1, max_length=100)
    role: Optional[UserRole] = UserRole.USER
    tenant_id: Optional[UUID] = None


class UserCreate(UserBase):
    """Schema for creating a new user"""
    password: constr(min_length=8, max_length=100)
    is_active: Optional[bool] = True
    
    @validator('password')
    def validate_password(cls, v):
        """Ensure password meets complexity requirements"""
        if not any(char.isdigit() for char in v):
            raise ValueError('Password must contain at least one digit')
        if not any(char.isupper() for char in v):
            raise ValueError('Password must contain at least one uppercase letter')
        if not any(char.islower() for char in v):
            raise ValueError('Password must contain at least one lowercase letter')
        return v


class UserUpdate(BaseModel):
    """Schema for updating user information"""
    email: Optional[EmailStr] = None
    username: Optional[constr(min_length=3, max_length=50, regex="^[a-zA-Z0-9_-]+$")] = None
    first_name: Optional[constr(min_length=1, max_length=100)] = None
    last_name: Optional[constr(min_length=1, max_length=100)] = None
    role: Optional[UserRole] = None
    is_active: Optional[bool] = None
    is_verified: Optional[bool] = None
    password: Optional[constr(min_length=8, max_length=100)] = None


class UserResponse(BaseModel):
    """Schema for user responses"""
    id: str
    email: str
    username: str
    first_name: str
    last_name: str
    role: str
    is_active: bool
    is_verified: bool
    tenant_id: Optional[str] = None
    created_at: str
    last_login: Optional[str] = None
    
    class Config:
        orm_mode = True


class UserListResponse(BaseModel):
    """Schema for paginated user list"""
    users: List[UserResponse]
    total: int
    skip: int
    limit: int


class UserFilters(BaseModel):
    """Schema for user list filtering"""
    role: Optional[UserRole] = None
    is_active: Optional[bool] = None
    is_verified: Optional[bool] = None
    search: Optional[str] = None
    tenant_id: Optional[UUID] = None


class UserPermissions(BaseModel):
    """Schema for user permissions response"""
    user_id: str
    permissions: List[str]


class UserStatistics(BaseModel):
    """Schema for user statistics"""
    total_users: int
    active_users: int
    verified_users: int
    users_by_role: dict
    recent_signups: int
    recent_logins: int