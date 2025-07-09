"""
Tenant Model
Multi-tenant architecture support
"""

import enum
from datetime import datetime
from decimal import Decimal
from typing import Optional
from uuid import uuid4

from sqlalchemy import (
    Column,
    String,
    Boolean,
    DateTime,
    Enum,
    Integer,
    Text,
    JSON,
    Numeric,
    ForeignKey,
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.core.database import Base
from app.core.types import GUID


class TenantStatus(enum.Enum):
    """Tenant status enumeration"""
    ACTIVE = "active"
    SUSPENDED = "suspended"
    CANCELLED = "cancelled"
    TRIAL = "trial"


class SubscriptionPlan(enum.Enum):
    """Subscription plan enumeration"""
    FREE = "free"
    BASIC = "basic"
    PROFESSIONAL = "professional"
    ENTERPRISE = "enterprise"


class Tenant(Base):
    """Tenant model for multi-tenant architecture"""
    
    __tablename__ = "tenants"
    
    # Primary identification
    id = Column(GUID(), primary_key=True, default=uuid4, index=True)
    name = Column(String(255), nullable=False, index=True)
    subdomain = Column(String(100), unique=True, nullable=True, index=True)
    domain = Column(String(255), nullable=True)
    
    # Contact information
    email = Column(String(255), nullable=False)
    phone = Column(String(20), nullable=True)
    address = Column(Text, nullable=True)
    
    # Business information
    company_size = Column(String(50), nullable=True)
    industry = Column(String(100), nullable=True)
    description = Column(Text, nullable=True)
    logo_url = Column(String(500), nullable=True)
    
    # Status and configuration
    status = Column(Enum(TenantStatus), default=TenantStatus.TRIAL, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    
    # Voice agent configuration
    agent_name = Column(String(255), default="AI Assistant", nullable=False)
    agent_voice_id = Column(String(255), nullable=True)
    agent_personality = Column(Text, nullable=True)
    agent_instructions = Column(Text, nullable=True)
    
    # Telephony configuration
    phone_numbers = Column(JSON, default=list, nullable=True)
    twilio_config = Column(JSON, nullable=True)
    
    # AI configuration
    openai_config = Column(JSON, nullable=True)
    elevenlabs_config = Column(JSON, nullable=True)
    
    # Limits and quotas
    max_monthly_calls = Column(Integer, default=100, nullable=False)
    max_concurrent_calls = Column(Integer, default=5, nullable=False)
    max_knowledge_docs = Column(Integer, default=50, nullable=False)
    max_storage_mb = Column(Integer, default=1000, nullable=False)
    
    # Usage tracking
    current_month_calls = Column(Integer, default=0, nullable=False)
    current_concurrent_calls = Column(Integer, default=0, nullable=False)
    total_calls = Column(Integer, default=0, nullable=False)
    storage_used_mb = Column(Integer, default=0, nullable=False)
    
    # Webhooks configuration
    webhook_url = Column(String(500), nullable=True)
    webhook_secret = Column(String(255), nullable=True)
    webhook_events = Column(JSON, default=list, nullable=True)
    
    # Billing information
    stripe_customer_id = Column(String(255), nullable=True)
    billing_email = Column(String(255), nullable=True)
    
    # Trial information
    trial_starts_at = Column(DateTime(timezone=True), nullable=True)
    trial_ends_at = Column(DateTime(timezone=True), nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    
    # Relationships
    users = relationship("User", back_populates="tenant")
    subscription = relationship("TenantSubscription", back_populates="tenant", uselist=False)
    knowledge_bases = relationship("KnowledgeBase", back_populates="tenant")
    calls = relationship("Call", back_populates="tenant")
    webhooks = relationship("Webhook", back_populates="tenant")
    billing_records = relationship("BillingRecord", back_populates="tenant")
    usage_metrics = relationship("UsageMetric", back_populates="tenant")
    
    def __repr__(self):
        return f"<Tenant(id={self.id}, name={self.name}, status={self.status.value})>"
    
    @property
    def is_trial(self) -> bool:
        """Check if tenant is in trial period"""
        return self.status == TenantStatus.TRIAL
    
    @property
    def is_trial_expired(self) -> bool:
        """Check if trial period has expired"""
        if not self.is_trial or not self.trial_ends_at:
            return False
        return datetime.utcnow() > self.trial_ends_at
    
    @property
    def calls_remaining(self) -> int:
        """Get remaining calls for current month"""
        return max(0, self.max_monthly_calls - self.current_month_calls)
    
    @property
    def storage_remaining_mb(self) -> int:
        """Get remaining storage in MB"""
        return max(0, self.max_storage_mb - self.storage_used_mb)
    
    def can_make_call(self) -> bool:
        """Check if tenant can make a new call"""
        if not self.is_active or self.status == TenantStatus.SUSPENDED:
            return False
        
        if self.is_trial_expired:
            return False
        
        if self.current_month_calls >= self.max_monthly_calls:
            return False
        
        if self.current_concurrent_calls >= self.max_concurrent_calls:
            return False
        
        return True


class TenantSubscription(Base):
    """Tenant subscription model"""
    
    __tablename__ = "tenant_subscriptions"
    
    # Primary identification
    id = Column(GUID(), primary_key=True, default=uuid4, index=True)
    tenant_id = Column(GUID(), ForeignKey("tenants.id"), nullable=False, unique=True)
    
    # Subscription details
    plan = Column(Enum(SubscriptionPlan), default=SubscriptionPlan.FREE, nullable=False)
    status = Column(String(50), default="active", nullable=False)
    
    # Pricing
    monthly_price = Column(Numeric(10, 2), default=0.00, nullable=False)
    price_per_call = Column(Numeric(10, 4), default=0.00, nullable=False)
    
    # Stripe integration
    stripe_subscription_id = Column(String(255), nullable=True)
    stripe_price_id = Column(String(255), nullable=True)
    
    # Subscription period
    current_period_start = Column(DateTime(timezone=True), nullable=True)
    current_period_end = Column(DateTime(timezone=True), nullable=True)
    
    # Cancellation
    cancel_at_period_end = Column(Boolean, default=False, nullable=False)
    cancelled_at = Column(DateTime(timezone=True), nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    
    # Relationships
    tenant = relationship("Tenant", back_populates="subscription")
    
    def __repr__(self):
        return f"<TenantSubscription(id={self.id}, tenant_id={self.tenant_id}, plan={self.plan.value})>"