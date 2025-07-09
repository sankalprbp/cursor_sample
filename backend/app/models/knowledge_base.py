"""
Knowledge Base Models
Manages tenant-specific knowledge bases for AI responses
"""

import enum
from datetime import datetime
from typing import Optional
from uuid import uuid4

from sqlalchemy import Column, String, Boolean, DateTime, Enum, ForeignKey, Text, Integer, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.core.database import Base
from app.core.types import GUID


class DocumentType(enum.Enum):
    """Document type enumeration"""
    PDF = "pdf"
    TEXT = "text"
    DOCX = "docx"
    MARKDOWN = "markdown"
    CSV = "csv"
    JSON = "json"
    WEB_PAGE = "web_page"


class DocumentStatus(enum.Enum):
    """Document processing status"""
    UPLOADING = "uploading"
    PROCESSING = "processing"
    PROCESSED = "processed"
    FAILED = "failed"
    ARCHIVED = "archived"


class KnowledgeBase(Base):
    """Knowledge base model for tenant-specific knowledge management"""
    
    __tablename__ = "knowledge_bases"
    
    # Primary identification
    id = Column(GUID(), primary_key=True, default=uuid4, index=True)
    tenant_id = Column(GUID(), ForeignKey("tenants.id"), nullable=False, index=True)
    
    # Basic information
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    
    # Configuration
    is_active = Column(Boolean, default=True, nullable=False)
    is_default = Column(Boolean, default=False, nullable=False)
    
    # Metadata
    tags = Column(JSON, default=list, nullable=True)
    category = Column(String(100), nullable=True)
    priority = Column(Integer, default=1, nullable=False)  # 1=highest, 10=lowest
    
    # Statistics
    document_count = Column(Integer, default=0, nullable=False)
    total_size_bytes = Column(Integer, default=0, nullable=False)
    last_updated = Column(DateTime(timezone=True), nullable=True)
    
    # AI configuration
    embedding_model = Column(String(100), default="text-embedding-ada-002", nullable=True)
    chunk_size = Column(Integer, default=1000, nullable=False)
    chunk_overlap = Column(Integer, default=200, nullable=False)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    
    # Relationships
    tenant = relationship("Tenant", back_populates="knowledge_bases")
    documents = relationship("KnowledgeDocument", back_populates="knowledge_base", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<KnowledgeBase(id={self.id}, name={self.name}, tenant_id={self.tenant_id})>"
    
    @property
    def size_mb(self) -> float:
        """Get size in megabytes"""
        return self.total_size_bytes / (1024 * 1024)
    
    def can_add_document(self, file_size_bytes: int) -> bool:
        """Check if document can be added based on tenant limits"""
        if not self.tenant:
            return False
        
        # Check document count limit
        if self.document_count >= self.tenant.max_knowledge_docs:
            return False
        
        # Check storage limit
        new_total_mb = (self.total_size_bytes + file_size_bytes) / (1024 * 1024)
        if new_total_mb > self.tenant.max_storage_mb:
            return False
        
        return True


class KnowledgeDocument(Base):
    """Knowledge document model for storing and processing documents"""
    
    __tablename__ = "knowledge_documents"
    
    # Primary identification
    id = Column(GUID(), primary_key=True, default=uuid4, index=True)
    knowledge_base_id = Column(GUID(), ForeignKey("knowledge_bases.id"), nullable=False, index=True)
    
    # File information
    filename = Column(String(255), nullable=False)
    original_filename = Column(String(255), nullable=False)
    file_type = Column(Enum(DocumentType), nullable=False)
    file_size_bytes = Column(Integer, nullable=False)
    file_hash = Column(String(64), nullable=False, index=True)  # SHA-256 hash
    
    # Storage information
    storage_path = Column(String(500), nullable=False)
    s3_bucket = Column(String(255), nullable=True)
    s3_key = Column(String(500), nullable=True)
    
    # Content and processing
    title = Column(String(500), nullable=True)
    content = Column(Text, nullable=True)  # Extracted text content
    summary = Column(Text, nullable=True)  # AI-generated summary
    status = Column(Enum(DocumentStatus), default=DocumentStatus.UPLOADING, nullable=False)
    
    # Processing metadata
    processing_error = Column(Text, nullable=True)
    chunk_count = Column(Integer, default=0, nullable=False)
    embedding_status = Column(String(50), default="pending", nullable=False)
    
    # Content metadata
    language = Column(String(10), nullable=True)
    word_count = Column(Integer, nullable=True)
    page_count = Column(Integer, nullable=True)
    
    # AI-extracted metadata
    keywords = Column(JSON, default=list, nullable=True)
    topics = Column(JSON, default=list, nullable=True)
    entities = Column(JSON, default=list, nullable=True)
    
    # Usage statistics
    access_count = Column(Integer, default=0, nullable=False)
    last_accessed = Column(DateTime(timezone=True), nullable=True)
    
    # User information
    uploaded_by = Column(GUID(), ForeignKey("users.id"), nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    processed_at = Column(DateTime(timezone=True), nullable=True)
    
    # Relationships
    knowledge_base = relationship("KnowledgeBase", back_populates="documents")
    uploader = relationship("User", foreign_keys=[uploaded_by])
    
    def __repr__(self):
        return f"<KnowledgeDocument(id={self.id}, filename={self.filename}, status={self.status.value})>"
    
    @property
    def size_mb(self) -> float:
        """Get file size in megabytes"""
        return self.file_size_bytes / (1024 * 1024)
    
    @property
    def is_processed(self) -> bool:
        """Check if document is fully processed"""
        return self.status == DocumentStatus.PROCESSED
    
    @property
    def can_be_searched(self) -> bool:
        """Check if document can be used for search"""
        return (
            self.status == DocumentStatus.PROCESSED and
            self.embedding_status == "completed" and
            self.content is not None
        )
    
    def mark_accessed(self):
        """Mark document as accessed (for analytics)"""
        self.access_count += 1
        self.last_accessed = func.now()