"""
User Model
Handles user authentication and authorization
"""

import enum
from datetime import datetime
from typing import Optional
from uuid import uuid4

from sqlalchemy import Column, String, Boolean, DateTime, Enum, ForeignKey, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.core.database import Base


class UserRole(enum.Enum):
    """User roles enumeration"""
    SUPER_ADMIN = "super_admin"  # Platform administrator
    TENANT_ADMIN = "tenant_admin"  # Tenant administrator
    TENANT_USER = "tenant_user"  # Regular tenant user
    AGENT = "agent"  # AI agent (system user)


class User(Base):
    """User model for authentication and authorization"""
    
    __tablename__ = "users"
    
    # Primary identification
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    username = Column(String(100), unique=True, index=True, nullable=True)
    
    # Authentication
    hashed_password = Column(String(255), nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    is_verified = Column(Boolean, default=False, nullable=False)
    
    # Profile information
    first_name = Column(String(100), nullable=True)
    last_name = Column(String(100), nullable=True)
    phone_number = Column(String(20), nullable=True)
    avatar_url = Column(String(500), nullable=True)
    
    # Role and permissions
    role = Column(Enum(UserRole), default=UserRole.TENANT_USER, nullable=False)
    
    # Multi-tenant relationship
    tenant_id = Column(UUID(as_uuid=True), ForeignKey("tenants.id"), nullable=True)
    
    # Security and session management
    last_login = Column(DateTime(timezone=True), nullable=True)
    password_reset_token = Column(String(255), nullable=True)
    password_reset_expires = Column(DateTime(timezone=True), nullable=True)
    email_verification_token = Column(String(255), nullable=True)
    email_verification_expires = Column(DateTime(timezone=True), nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    
    # Relationships
    tenant = relationship("Tenant", back_populates="users")
    calls = relationship("Call", back_populates="user", foreign_keys="[Call.user_id]")
    webhooks = relationship("Webhook", back_populates="user")
    
    def __repr__(self):
        return f"<User(id={self.id}, email={self.email}, role={self.role.value})>"
    
    @property
    def full_name(self) -> str:
        """Get user's full name"""
        if self.first_name and self.last_name:
            return f"{self.first_name} {self.last_name}"
        return self.first_name or self.last_name or self.email
    
    @property
    def is_admin(self) -> bool:
        """Check if user is an administrator"""
        return self.role in [UserRole.SUPER_ADMIN, UserRole.TENANT_ADMIN]
    
    @property
    def is_super_admin(self) -> bool:
        """Check if user is a super administrator"""
        return self.role == UserRole.SUPER_ADMIN
    
    def has_permission(self, action: str, resource: str = None) -> bool:
        """Check user permissions"""
        if self.role == UserRole.SUPER_ADMIN:
            return True
        
        if self.role == UserRole.TENANT_ADMIN:
            # Tenant admins can manage their own tenant resources
            return action in ["read", "create", "update", "delete"]
        
        if self.role == UserRole.TENANT_USER:
            # Regular users can only read their own data
            return action == "read"
        
        return False