"""
Billing Models
Manages billing, usage tracking, and analytics
"""

import enum
from datetime import datetime
from decimal import Decimal
from typing import Optional
from uuid import uuid4

from sqlalchemy import Column, String, Boolean, DateTime, Enum, ForeignKey, Text, Integer, JSON, Numeric, Date
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.core.database import Base


class BillingStatus(enum.Enum):
    """Billing record status"""
    PENDING = "pending"
    PAID = "paid"
    FAILED = "failed"
    CANCELLED = "cancelled"
    REFUNDED = "refunded"
    DISPUTED = "disputed"


class UsageType(enum.Enum):
    """Usage metric types"""
    CALLS = "calls"
    MINUTES = "minutes"
    TRANSCRIPTION = "transcription"
    AI_REQUESTS = "ai_requests"
    STORAGE = "storage"
    KNOWLEDGE_DOCS = "knowledge_docs"
    WEBHOOKS = "webhooks"
    API_REQUESTS = "api_requests"


class BillingPeriod(enum.Enum):
    """Billing period types"""
    MONTHLY = "monthly"
    QUARTERLY = "quarterly"
    ANNUALLY = "annually"
    ONE_TIME = "one_time"


class BillingRecord(Base):
    """Billing record model for tracking charges and payments"""
    
    __tablename__ = "billing_records"
    
    # Primary identification
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4, index=True)
    tenant_id = Column(UUID(as_uuid=True), ForeignKey("tenants.id"), nullable=False, index=True)
    
    # Billing identification
    invoice_number = Column(String(100), nullable=False, unique=True, index=True)
    stripe_invoice_id = Column(String(255), nullable=True, unique=True)
    stripe_payment_intent_id = Column(String(255), nullable=True)
    
    # Billing period
    billing_period = Column(Enum(BillingPeriod), default=BillingPeriod.MONTHLY, nullable=False)
    period_start = Column(Date, nullable=False, index=True)
    period_end = Column(Date, nullable=False, index=True)
    
    # Amounts
    subtotal_usd = Column(Numeric(10, 2), nullable=False, default=0.00)
    tax_usd = Column(Numeric(10, 2), nullable=False, default=0.00)
    total_usd = Column(Numeric(10, 2), nullable=False, default=0.00)
    
    # Usage-based charges
    base_charge_usd = Column(Numeric(10, 2), nullable=False, default=0.00)  # Subscription base
    usage_charges_usd = Column(Numeric(10, 2), nullable=False, default=0.00)  # Usage-based
    
    # Discount and credits
    discount_usd = Column(Numeric(10, 2), nullable=False, default=0.00)
    credits_applied_usd = Column(Numeric(10, 2), nullable=False, default=0.00)
    
    # Status and payment
    status = Column(Enum(BillingStatus), default=BillingStatus.PENDING, nullable=False)
    payment_status = Column(String(50), nullable=True)
    payment_method = Column(String(50), nullable=True)
    
    # Usage summary
    total_calls = Column(Integer, default=0, nullable=False)
    total_minutes = Column(Numeric(10, 2), default=0.00, nullable=False)
    total_storage_mb = Column(Integer, default=0, nullable=False)
    total_ai_requests = Column(Integer, default=0, nullable=False)
    
    # Line items (detailed breakdown)
    line_items = Column(JSON, nullable=True)
    
    # Payment information
    paid_at = Column(DateTime(timezone=True), nullable=True)
    due_date = Column(Date, nullable=True)
    
    # Failure information
    failure_reason = Column(Text, nullable=True)
    failure_code = Column(String(100), nullable=True)
    retry_count = Column(Integer, default=0, nullable=False)
    next_retry_at = Column(DateTime(timezone=True), nullable=True)
    
    # Currency and locale
    currency = Column(String(3), default="USD", nullable=False)
    tax_rate = Column(Numeric(5, 4), default=0.0000, nullable=False)
    
    # Metadata
    metadata = Column(JSON, nullable=True)
    notes = Column(Text, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    
    # Relationships
    tenant = relationship("Tenant", back_populates="billing_records")
    
    def __repr__(self):
        return f"<BillingRecord(id={self.id}, invoice={self.invoice_number}, total=${self.total_usd})>"
    
    @property
    def is_paid(self) -> bool:
        """Check if billing record is paid"""
        return self.status == BillingStatus.PAID
    
    @property
    def is_overdue(self) -> bool:
        """Check if payment is overdue"""
        if not self.due_date or self.is_paid:
            return False
        return datetime.utcnow().date() > self.due_date
    
    @property
    def days_overdue(self) -> int:
        """Get number of days overdue"""
        if not self.is_overdue:
            return 0
        return (datetime.utcnow().date() - self.due_date).days
    
    @property
    def usage_percentage(self) -> float:
        """Calculate percentage of total that is usage-based"""
        if self.total_usd == 0:
            return 0.0
        return float(self.usage_charges_usd / self.total_usd * 100)


class UsageMetric(Base):
    """Usage metric model for tracking detailed usage data"""
    
    __tablename__ = "usage_metrics"
    
    # Primary identification
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4, index=True)
    tenant_id = Column(UUID(as_uuid=True), ForeignKey("tenants.id"), nullable=False, index=True)
    
    # Metric identification
    metric_type = Column(Enum(UsageType), nullable=False, index=True)
    metric_name = Column(String(100), nullable=False)
    metric_description = Column(Text, nullable=True)
    
    # Time period
    date = Column(Date, nullable=False, index=True)
    hour = Column(Integer, nullable=True)  # For hourly tracking
    
    # Usage values
    count = Column(Integer, default=0, nullable=False)
    duration_seconds = Column(Integer, nullable=True)
    size_bytes = Column(Integer, nullable=True)
    cost_usd = Column(Numeric(10, 4), nullable=True)
    
    # Rate information
    unit_price_usd = Column(Numeric(10, 6), nullable=True)
    billing_unit = Column(String(50), nullable=True)  # per_call, per_minute, per_mb, etc.
    
    # Source information
    source_id = Column(String(255), nullable=True)  # Call ID, User ID, etc.
    source_type = Column(String(100), nullable=True)  # call, user, document, etc.
    
    # Aggregation level
    aggregation_level = Column(String(50), default="daily", nullable=False)  # hourly, daily, monthly
    
    # Metadata
    metadata = Column(JSON, nullable=True)
    tags = Column(JSON, default=list, nullable=True)
    
    # Quality metrics
    success_rate = Column(Numeric(5, 4), nullable=True)  # 0.0000 to 1.0000
    error_rate = Column(Numeric(5, 4), nullable=True)
    average_duration = Column(Numeric(10, 2), nullable=True)
    
    # Geographic information
    country_code = Column(String(3), nullable=True)
    region = Column(String(100), nullable=True)
    
    # Billing status
    is_billable = Column(Boolean, default=True, nullable=False)
    is_billed = Column(Boolean, default=False, nullable=False)
    billing_record_id = Column(UUID(as_uuid=True), ForeignKey("billing_records.id"), nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    
    # Relationships
    tenant = relationship("Tenant", back_populates="usage_metrics")
    billing_record = relationship("BillingRecord")
    
    def __repr__(self):
        return f"<UsageMetric(id={self.id}, type={self.metric_type.value}, count={self.count}, date={self.date})>"
    
    @property
    def display_value(self) -> str:
        """Get formatted display value based on metric type"""
        if self.metric_type == UsageType.CALLS:
            return f"{self.count} calls"
        elif self.metric_type == UsageType.MINUTES:
            minutes = self.duration_seconds / 60 if self.duration_seconds else 0
            return f"{minutes:.1f} minutes"
        elif self.metric_type == UsageType.STORAGE:
            mb = self.size_bytes / (1024 * 1024) if self.size_bytes else 0
            return f"{mb:.1f} MB"
        else:
            return f"{self.count} {self.billing_unit or 'units'}"
    
    @property
    def unit_cost_display(self) -> str:
        """Get formatted unit cost"""
        if self.unit_price_usd:
            return f"${self.unit_price_usd:.4f} per {self.billing_unit or 'unit'}"
        return "Free"
    
    def calculate_cost(self) -> Decimal:
        """Calculate total cost for this usage metric"""
        if not self.unit_price_usd:
            return Decimal('0.0000')
        
        if self.metric_type == UsageType.MINUTES and self.duration_seconds:
            minutes = Decimal(str(self.duration_seconds)) / Decimal('60')
            return minutes * self.unit_price_usd
        elif self.metric_type == UsageType.STORAGE and self.size_bytes:
            mb = Decimal(str(self.size_bytes)) / Decimal('1048576')  # 1024^2
            return mb * self.unit_price_usd
        else:
            return Decimal(str(self.count)) * self.unit_price_usd