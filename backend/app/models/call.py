"""
Call Models
Manages voice agent calls, transcripts, and analytics
"""

import enum
from datetime import datetime
from decimal import Decimal
from typing import Optional
from uuid import uuid4

from sqlalchemy import Column, String, Boolean, DateTime, Enum, ForeignKey, Text, Integer, JSON, Numeric, Float
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.core.database import Base
from app.core.types import GUID


class CallStatus(enum.Enum):
    """Call status enumeration"""
    INITIATED = "initiated"
    RINGING = "ringing"
    ANSWERED = "answered"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    MISSED = "missed"
    BUSY = "busy"
    NO_ANSWER = "no_answer"
    CANCELLED = "cancelled"


class CallDirection(enum.Enum):
    """Call direction enumeration"""
    INBOUND = "inbound"
    OUTBOUND = "outbound"


class CallEndReason(enum.Enum):
    """Call end reason enumeration"""
    CALLER_HANGUP = "caller_hangup"
    AGENT_HANGUP = "agent_hangup"
    SYSTEM_HANGUP = "system_hangup"
    ERROR = "error"
    TIMEOUT = "timeout"
    TRANSFER = "transfer"


class SentimentType(enum.Enum):
    """Sentiment analysis types"""
    POSITIVE = "positive"
    NEUTRAL = "neutral"
    NEGATIVE = "negative"
    MIXED = "mixed"


class Call(Base):
    """Call model for tracking voice agent interactions"""
    
    __tablename__ = "calls"
    
    # Primary identification
    id = Column(GUID(), primary_key=True, default=uuid4, index=True)
    tenant_id = Column(GUID(), ForeignKey("tenants.id"), nullable=False, index=True)
    user_id = Column(GUID(), ForeignKey("users.id"), nullable=True, index=True)
    
    # Call identification
    call_sid = Column(String(255), nullable=True, unique=True, index=True)  # Twilio call SID
    session_id = Column(String(255), nullable=False, unique=True, index=True)
    
    # Call details
    direction = Column(Enum(CallDirection), nullable=False)
    status = Column(Enum(CallStatus), default=CallStatus.INITIATED, nullable=False)
    
    # Contact information
    caller_number = Column(String(20), nullable=True)
    caller_name = Column(String(255), nullable=True)
    called_number = Column(String(20), nullable=True)
    
    # Geographic information
    caller_country = Column(String(3), nullable=True)  # ISO country code
    caller_city = Column(String(100), nullable=True)
    caller_region = Column(String(100), nullable=True)
    
    # Timing information
    started_at = Column(DateTime(timezone=True), nullable=True)
    answered_at = Column(DateTime(timezone=True), nullable=True)
    ended_at = Column(DateTime(timezone=True), nullable=True)
    duration_seconds = Column(Integer, nullable=True)
    
    # End information
    end_reason = Column(Enum(CallEndReason), nullable=True)
    hangup_cause = Column(String(100), nullable=True)
    
    # AI agent information
    agent_name = Column(String(255), nullable=True)
    agent_voice_id = Column(String(255), nullable=True)
    
    # Audio information
    audio_url = Column(String(500), nullable=True)
    audio_duration_seconds = Column(Integer, nullable=True)
    audio_size_bytes = Column(Integer, nullable=True)
    audio_s3_key = Column(String(500), nullable=True)
    
    # Cost and billing
    cost_usd = Column(Numeric(10, 4), nullable=True)
    twilio_cost_usd = Column(Numeric(10, 4), nullable=True)
    openai_cost_usd = Column(Numeric(10, 4), nullable=True)
    elevenlabs_cost_usd = Column(Numeric(10, 4), nullable=True)
    
    # Quality metrics
    audio_quality_score = Column(Float, nullable=True)  # 0.0 to 1.0
    connection_quality = Column(String(50), nullable=True)
    
    # Call summary
    summary = Column(Text, nullable=True)
    call_purpose = Column(String(255), nullable=True)
    resolution_status = Column(String(100), nullable=True)
    
    # Call metadata (renamed from 'metadata' to avoid SQLAlchemy conflict)
    call_metadata = Column(JSON, nullable=True)
    tags = Column(JSON, default=list, nullable=True)
    
    # Analytics flags
    needs_followup = Column(Boolean, default=False, nullable=False)
    escalation_required = Column(Boolean, default=False, nullable=False)
    customer_satisfied = Column(Boolean, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    
    # Relationships
    tenant = relationship("Tenant", back_populates="calls")
    user = relationship("User", back_populates="calls", foreign_keys=[user_id])
    transcript = relationship("CallTranscript", back_populates="call", uselist=False)
    analytics = relationship("CallAnalytics", back_populates="call", uselist=False)
    
    def __repr__(self):
        return f"<Call(id={self.id}, status={self.status.value}, caller={self.caller_number})>"
    
    @property
    def is_active(self) -> bool:
        """Check if call is currently active"""
        return self.status in [CallStatus.RINGING, CallStatus.ANSWERED, CallStatus.IN_PROGRESS]
    
    @property
    def is_completed(self) -> bool:
        """Check if call is completed"""
        return self.status in [CallStatus.COMPLETED, CallStatus.FAILED, CallStatus.MISSED, CallStatus.CANCELLED]
    
    @property
    def duration_minutes(self) -> float:
        """Get call duration in minutes"""
        if self.duration_seconds:
            return self.duration_seconds / 60.0
        return 0.0
    
    @property
    def total_cost_usd(self) -> Decimal:
        """Calculate total cost in USD"""
        total = Decimal('0.00')
        if self.cost_usd:
            total += self.cost_usd
        if self.twilio_cost_usd:
            total += self.twilio_cost_usd
        if self.openai_cost_usd:
            total += self.openai_cost_usd
        if self.elevenlabs_cost_usd:
            total += self.elevenlabs_cost_usd
        return total


class CallTranscript(Base):
    """Call transcript model for storing conversation details"""
    
    __tablename__ = "call_transcripts"
    
    # Primary identification
    id = Column(GUID(), primary_key=True, default=uuid4, index=True)
    call_id = Column(GUID(), ForeignKey("calls.id"), nullable=False, unique=True, index=True)
    
    # Transcript content
    full_transcript = Column(Text, nullable=True)
    conversation_json = Column(JSON, nullable=True)  # Structured conversation data
    
    # Speaker information
    speakers_detected = Column(Integer, default=2, nullable=False)
    speaker_labels = Column(JSON, nullable=True)  # Speaker identification
    
    # Processing information
    transcription_engine = Column(String(100), nullable=True)
    confidence_score = Column(Float, nullable=True)  # Average confidence
    processing_time_seconds = Column(Float, nullable=True)
    
    # Language detection
    primary_language = Column(String(10), nullable=True)
    language_confidence = Column(Float, nullable=True)
    
    # Content analysis
    word_count = Column(Integer, nullable=True)
    unique_words = Column(Integer, nullable=True)
    speaking_rate_wpm = Column(Float, nullable=True)  # Words per minute
    
    # Key phrases and entities
    key_phrases = Column(JSON, default=list, nullable=True)
    entities = Column(JSON, default=list, nullable=True)
    topics = Column(JSON, default=list, nullable=True)
    
    # Processing status
    is_processed = Column(Boolean, default=False, nullable=False)
    processing_error = Column(Text, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    processed_at = Column(DateTime(timezone=True), nullable=True)
    
    # Relationships
    call = relationship("Call", back_populates="transcript")
    
    def __repr__(self):
        return f"<CallTranscript(id={self.id}, call_id={self.call_id}, words={self.word_count})>"


class CallAnalytics(Base):
    """Call analytics model for storing AI-generated insights"""
    
    __tablename__ = "call_analytics"
    
    # Primary identification
    id = Column(GUID(), primary_key=True, default=uuid4, index=True)
    call_id = Column(GUID(), ForeignKey("calls.id"), nullable=False, unique=True, index=True)
    
    # Sentiment analysis
    overall_sentiment = Column(Enum(SentimentType), nullable=True)
    sentiment_score = Column(Float, nullable=True)  # -1.0 to 1.0
    customer_sentiment = Column(Enum(SentimentType), nullable=True)
    agent_sentiment = Column(Enum(SentimentType), nullable=True)
    
    # Call classification
    call_category = Column(String(100), nullable=True)
    call_intent = Column(String(255), nullable=True)
    issue_resolved = Column(Boolean, nullable=True)
    resolution_time_seconds = Column(Integer, nullable=True)
    
    # Performance metrics
    agent_response_time_avg = Column(Float, nullable=True)  # Average response time in seconds
    customer_wait_time_total = Column(Float, nullable=True)
    interruptions_count = Column(Integer, default=0, nullable=False)
    dead_air_seconds = Column(Float, default=0.0, nullable=False)
    
    # Quality scores
    conversation_quality_score = Column(Float, nullable=True)  # 0.0 to 1.0
    agent_performance_score = Column(Float, nullable=True)  # 0.0 to 1.0
    customer_experience_score = Column(Float, nullable=True)  # 0.0 to 1.0
    
    # Behavioral analysis
    talk_time_ratio = Column(Float, nullable=True)  # Customer talk time / Total talk time
    agent_talk_time_seconds = Column(Float, nullable=True)
    customer_talk_time_seconds = Column(Float, nullable=True)
    
    # Issues and actions
    issues_identified = Column(JSON, default=list, nullable=True)
    action_items = Column(JSON, default=list, nullable=True)
    follow_up_required = Column(Boolean, default=False, nullable=False)
    escalation_reasons = Column(JSON, default=list, nullable=True)
    
    # Knowledge base usage
    kb_queries_count = Column(Integer, default=0, nullable=False)
    kb_successful_matches = Column(Integer, default=0, nullable=False)
    kb_documents_referenced = Column(JSON, default=list, nullable=True)
    
    # AI model performance
    ai_response_relevance = Column(Float, nullable=True)  # 0.0 to 1.0
    ai_accuracy_score = Column(Float, nullable=True)  # 0.0 to 1.0
    hallucination_detected = Column(Boolean, default=False, nullable=False)
    
    # Processing information
    analysis_model = Column(String(100), nullable=True)
    analysis_version = Column(String(50), nullable=True)
    processing_time_seconds = Column(Float, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    analyzed_at = Column(DateTime(timezone=True), nullable=True)
    
    # Relationships
    call = relationship("Call", back_populates="analytics")
    
    def __repr__(self):
        return f"<CallAnalytics(id={self.id}, call_id={self.call_id}, sentiment={self.overall_sentiment})>"