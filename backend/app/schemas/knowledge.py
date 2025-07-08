"""
Knowledge Base Schemas
Pydantic models for knowledge base API operations
"""

from typing import Optional, List, Dict, Any
from datetime import datetime
from uuid import UUID
from pydantic import BaseModel, constr, Field
from enum import Enum

from app.models.knowledge_base import DocumentType, DocumentStatus


class KnowledgeBaseBase(BaseModel):
    """Base knowledge base schema"""
    name: constr(min_length=1, max_length=255)
    description: Optional[str] = None
    is_active: Optional[bool] = True
    is_default: Optional[bool] = False
    tags: Optional[List[str]] = []
    category: Optional[str] = None
    priority: Optional[int] = Field(1, ge=1, le=10)
    embedding_model: Optional[str] = "text-embedding-ada-002"
    chunk_size: Optional[int] = Field(1000, ge=100, le=10000)
    chunk_overlap: Optional[int] = Field(200, ge=0, le=1000)


class KnowledgeBaseCreate(KnowledgeBaseBase):
    """Schema for creating a knowledge base"""
    pass


class KnowledgeBaseUpdate(BaseModel):
    """Schema for updating a knowledge base"""
    name: Optional[constr(min_length=1, max_length=255)] = None
    description: Optional[str] = None
    is_active: Optional[bool] = None
    is_default: Optional[bool] = None
    tags: Optional[List[str]] = None
    category: Optional[str] = None
    priority: Optional[int] = Field(None, ge=1, le=10)
    embedding_model: Optional[str] = None
    chunk_size: Optional[int] = Field(None, ge=100, le=10000)
    chunk_overlap: Optional[int] = Field(None, ge=0, le=1000)


class KnowledgeBaseResponse(BaseModel):
    """Schema for knowledge base responses"""
    id: str
    tenant_id: str
    name: str
    description: Optional[str] = None
    is_active: bool
    is_default: bool
    tags: List[str]
    category: Optional[str] = None
    priority: int
    document_count: int
    total_size_bytes: int
    size_mb: float
    last_updated: Optional[str] = None
    embedding_model: str
    chunk_size: int
    chunk_overlap: int
    created_at: str
    updated_at: str
    
    class Config:
        from_attributes = True


class KnowledgeBaseListResponse(BaseModel):
    """Schema for paginated knowledge base list"""
    knowledge_bases: List[KnowledgeBaseResponse]
    total: int
    skip: int
    limit: int


class DocumentUpload(BaseModel):
    """Schema for document upload request"""
    title: Optional[str] = None
    tags: Optional[List[str]] = []
    language: Optional[str] = None


class DocumentResponse(BaseModel):
    """Schema for document responses"""
    id: str
    knowledge_base_id: str
    filename: str
    original_filename: str
    file_type: str
    file_size_bytes: int
    size_mb: float
    file_hash: str
    title: Optional[str] = None
    summary: Optional[str] = None
    status: str
    processing_error: Optional[str] = None
    chunk_count: int
    embedding_status: str
    language: Optional[str] = None
    word_count: Optional[int] = None
    page_count: Optional[int] = None
    keywords: List[str]
    topics: List[str]
    entities: List[str]
    access_count: int
    last_accessed: Optional[str] = None
    uploaded_by: Optional[str] = None
    created_at: str
    updated_at: str
    processed_at: Optional[str] = None
    
    class Config:
        from_attributes = True


class DocumentListResponse(BaseModel):
    """Schema for paginated document list"""
    documents: List[DocumentResponse]
    total: int
    skip: int
    limit: int


class DocumentFilters(BaseModel):
    """Schema for document filtering"""
    file_type: Optional[DocumentType] = None
    status: Optional[DocumentStatus] = None
    search: Optional[str] = None
    uploaded_after: Optional[datetime] = None
    uploaded_before: Optional[datetime] = None
    tags: Optional[List[str]] = None


class KnowledgeBaseFilters(BaseModel):
    """Schema for knowledge base filtering"""
    is_active: Optional[bool] = None
    is_default: Optional[bool] = None
    category: Optional[str] = None
    search: Optional[str] = None
    tags: Optional[List[str]] = None


class SearchQuery(BaseModel):
    """Schema for searching knowledge base"""
    query: str
    knowledge_base_ids: Optional[List[UUID]] = None
    limit: Optional[int] = Field(10, ge=1, le=100)
    include_summary: Optional[bool] = True
    include_metadata: Optional[bool] = False
    min_relevance_score: Optional[float] = Field(0.7, ge=0.0, le=1.0)


class SearchResult(BaseModel):
    """Schema for search result"""
    document_id: str
    document_title: str
    chunk_text: str
    relevance_score: float
    page_number: Optional[int] = None
    metadata: Optional[Dict[str, Any]] = None


class SearchResponse(BaseModel):
    """Schema for search response"""
    query: str
    results: List[SearchResult]
    total_results: int
    processing_time_ms: float


class KnowledgeBaseStatistics(BaseModel):
    """Schema for knowledge base statistics"""
    knowledge_base_id: str
    name: str
    document_count: int
    total_size_mb: float
    average_document_size_mb: float
    document_types: Dict[str, int]
    status_breakdown: Dict[str, int]
    last_updated: Optional[str] = None
    most_accessed_documents: List[Dict[str, Any]]
    recent_uploads: List[Dict[str, Any]]