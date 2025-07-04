"""
Webhook Models
Manages webhook notifications and event tracking
"""

import enum
from datetime import datetime, timedelta
from typing import Optional
from uuid import uuid4

from sqlalchemy import Column, String, Boolean, DateTime, Enum, ForeignKey, Text, Integer, JSON
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.core.database import Base


class WebhookEventType(enum.Enum):
    """Webhook event types"""
    CALL_STARTED = "call.started"
    CALL_ANSWERED = "call.answered"
    CALL_ENDED = "call.ended"
    CALL_FAILED = "call.failed"
    TRANSCRIPT_READY = "transcript.ready"
    ANALYTICS_READY = "analytics.ready"
    KNOWLEDGE_DOCUMENT_PROCESSED = "knowledge_document.processed"
    BILLING_INVOICE_CREATED = "billing.invoice_created"
    TENANT_LIMIT_REACHED = "tenant.limit_reached"
    USER_CREATED = "user.created"
    USER_UPDATED = "user.updated"


class WebhookStatus(enum.Enum):
    """Webhook status enumeration"""
    ACTIVE = "active"
    INACTIVE = "inactive"
    SUSPENDED = "suspended"
    FAILED = "failed"


class EventStatus(enum.Enum):
    """Event delivery status"""
    PENDING = "pending"
    DELIVERED = "delivered"
    FAILED = "failed"
    RETRYING = "retrying"
    EXPIRED = "expired"


class Webhook(Base):
    """Webhook configuration model"""
    
    __tablename__ = "webhooks"
    
    # Primary identification
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4, index=True)
    tenant_id = Column(UUID(as_uuid=True), ForeignKey("tenants.id"), nullable=False, index=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True)
    
    # Webhook details
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    url = Column(String(500), nullable=False)
    
    # Configuration
    secret = Column(String(255), nullable=False)  # For signature verification
    event_types = Column(JSON, default=list, nullable=False)  # List of subscribed events
    is_active = Column(Boolean, default=True, nullable=False)
    status = Column(Enum(WebhookStatus), default=WebhookStatus.ACTIVE, nullable=False)
    
    # HTTP configuration
    timeout_seconds = Column(Integer, default=30, nullable=False)
    retry_attempts = Column(Integer, default=3, nullable=False)
    retry_delay_seconds = Column(Integer, default=60, nullable=False)
    
    # Headers and authentication
    custom_headers = Column(JSON, nullable=True)
    auth_type = Column(String(50), nullable=True)  # bearer, basic, none
    auth_credentials = Column(JSON, nullable=True)  # Encrypted
    
    # SSL configuration
    verify_ssl = Column(Boolean, default=True, nullable=False)
    
    # Statistics
    total_events = Column(Integer, default=0, nullable=False)
    successful_deliveries = Column(Integer, default=0, nullable=False)
    failed_deliveries = Column(Integer, default=0, nullable=False)
    last_delivery_at = Column(DateTime(timezone=True), nullable=True)
    last_success_at = Column(DateTime(timezone=True), nullable=True)
    last_failure_at = Column(DateTime(timezone=True), nullable=True)
    
    # Failure handling
    consecutive_failures = Column(Integer, default=0, nullable=False)
    max_consecutive_failures = Column(Integer, default=10, nullable=False)
    failure_reason = Column(Text, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    
    # Relationships
    tenant = relationship("Tenant", back_populates="webhooks")
    user = relationship("User", back_populates="webhooks")
    events = relationship("WebhookEvent", back_populates="webhook", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Webhook(id={self.id}, name={self.name}, url={self.url})>"
    
    @property
    def success_rate(self) -> float:
        """Calculate webhook success rate"""
        if self.total_events == 0:
            return 1.0
        return self.successful_deliveries / self.total_events
    
    @property
    def is_healthy(self) -> bool:
        """Check if webhook is healthy"""
        return (
            self.is_active and
            self.status == WebhookStatus.ACTIVE and
            self.consecutive_failures < self.max_consecutive_failures
        )
    
    def should_suspend(self) -> bool:
        """Check if webhook should be suspended due to failures"""
        return self.consecutive_failures >= self.max_consecutive_failures
    
    def subscribes_to_event(self, event_type: str) -> bool:
        """Check if webhook subscribes to specific event type"""
        return event_type in self.event_types


class WebhookEvent(Base):
    """Webhook event delivery tracking"""
    
    __tablename__ = "webhook_events"
    
    # Primary identification
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4, index=True)
    webhook_id = Column(UUID(as_uuid=True), ForeignKey("webhooks.id"), nullable=False, index=True)
    
    # Event identification
    event_id = Column(String(255), nullable=False, unique=True, index=True)
    event_type = Column(Enum(WebhookEventType), nullable=False, index=True)
    
    # Event data
    payload = Column(JSON, nullable=False)
    payload_size_bytes = Column(Integer, nullable=False)
    
    # Delivery information
    status = Column(Enum(EventStatus), default=EventStatus.PENDING, nullable=False, index=True)
    attempts = Column(Integer, default=0, nullable=False)
    max_attempts = Column(Integer, default=3, nullable=False)
    
    # Response information
    response_status_code = Column(Integer, nullable=True)
    response_headers = Column(JSON, nullable=True)
    response_body = Column(Text, nullable=True)
    response_time_ms = Column(Integer, nullable=True)
    
    # Error information
    error_message = Column(Text, nullable=True)
    error_type = Column(String(100), nullable=True)
    
    # Timing
    scheduled_at = Column(DateTime(timezone=True), nullable=False)
    first_attempt_at = Column(DateTime(timezone=True), nullable=True)
    last_attempt_at = Column(DateTime(timezone=True), nullable=True)
    delivered_at = Column(DateTime(timezone=True), nullable=True)
    expires_at = Column(DateTime(timezone=True), nullable=True)
    
    # Retry configuration
    next_retry_at = Column(DateTime(timezone=True), nullable=True)
    retry_delay_seconds = Column(Integer, nullable=True)
    
    # Source information
    source_id = Column(String(255), nullable=True)  # Call ID, User ID, etc.
    source_type = Column(String(100), nullable=True)  # call, user, tenant, etc.
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    
    # Relationships
    webhook = relationship("Webhook", back_populates="events")
    
    def __repr__(self):
        return f"<WebhookEvent(id={self.id}, type={self.event_type.value}, status={self.status.value})>"
    
    @property
    def is_deliverable(self) -> bool:
        """Check if event can be delivered"""
        return (
            self.status in [EventStatus.PENDING, EventStatus.RETRYING] and
            self.attempts < self.max_attempts and
            (self.expires_at is None or datetime.utcnow() < self.expires_at)
        )
    
    @property
    def should_retry(self) -> bool:
        """Check if event should be retried"""
        return (
            self.status == EventStatus.FAILED and
            self.attempts < self.max_attempts and
            (self.expires_at is None or datetime.utcnow() < self.expires_at) and
            (self.next_retry_at is None or datetime.utcnow() >= self.next_retry_at)
        )
    
    @property
    def is_expired(self) -> bool:
        """Check if event has expired"""
        return (
            self.expires_at is not None and
            datetime.utcnow() > self.expires_at
        )
    
    def calculate_next_retry(self, base_delay_seconds: int = 60) -> datetime:
        """Calculate next retry time with exponential backoff"""
        delay = base_delay_seconds * (2 ** self.attempts)
        return datetime.utcnow() + timedelta(seconds=delay)