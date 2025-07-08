"""
Knowledge Base API Endpoints
Handles knowledge base and document management
"""

from typing import Any, List, Optional
from uuid import UUID
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, Query, status, UploadFile, File, Form
from fastapi.security import HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession
import hashlib
from pathlib import Path

from app.core.database import get_db
from app.services.auth import auth_service, security
from app.services.knowledge import knowledge_service
from app.schemas.knowledge import (
    KnowledgeBaseCreate,
    KnowledgeBaseUpdate,
    KnowledgeBaseResponse,
    KnowledgeBaseListResponse,
    KnowledgeBaseFilters,
    DocumentResponse,
    DocumentListResponse,
    DocumentFilters,
    SearchQuery,
    SearchResponse,
    KnowledgeBaseStatistics
)
from app.models.user import UserRole
from app.models.knowledge_base import DocumentType, DocumentStatus


router = APIRouter()


@router.get("/bases", response_model=KnowledgeBaseListResponse)
async def list_knowledge_bases(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    is_active: Optional[bool] = None,
    is_default: Optional[bool] = None,
    category: Optional[str] = None,
    search: Optional[str] = None,
    tags: Optional[List[str]] = Query(None),
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db)
) -> Any:
    """
    List knowledge bases for the current tenant
    """
    # Get current user
    current_user = await auth_service.get_current_user(db, credentials)
    
    if not current_user.tenant_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User is not associated with any tenant"
        )
    
    # Create filters
    filters = KnowledgeBaseFilters(
        is_active=is_active,
        is_default=is_default,
        category=category,
        search=search,
        tags=tags
    )
    
    # Get knowledge bases
    result = await knowledge_service.list_knowledge_bases(
        db, current_user.tenant_id, filters, skip, limit
    )
    
    # Convert to response format
    kb_responses = []
    for kb in result["knowledge_bases"]:
        kb_responses.append(KnowledgeBaseResponse(
            id=str(kb.id),
            tenant_id=str(kb.tenant_id),
            name=kb.name,
            description=kb.description,
            is_active=kb.is_active,
            is_default=kb.is_default,
            tags=kb.tags or [],
            category=kb.category,
            priority=kb.priority,
            document_count=kb.document_count,
            total_size_bytes=kb.total_size_bytes,
            size_mb=kb.size_mb,
            last_updated=kb.last_updated.isoformat() if kb.last_updated else None,
            embedding_model=kb.embedding_model,
            chunk_size=kb.chunk_size,
            chunk_overlap=kb.chunk_overlap,
            created_at=kb.created_at.isoformat(),
            updated_at=kb.updated_at.isoformat()
        ))
    
    return KnowledgeBaseListResponse(
        knowledge_bases=kb_responses,
        total=result["total"],
        skip=result["skip"],
        limit=result["limit"]
    )


@router.get("/bases/{knowledge_base_id}", response_model=KnowledgeBaseResponse)
async def get_knowledge_base(
    knowledge_base_id: UUID,
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db)
) -> Any:
    """
    Get knowledge base by ID
    """
    # Get current user
    current_user = await auth_service.get_current_user(db, credentials)
    
    # Get knowledge base
    kb = await knowledge_service.get_knowledge_base(
        db, knowledge_base_id, current_user.tenant_id
    )
    
    if not kb:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Knowledge base not found"
        )
    
    return KnowledgeBaseResponse(
        id=str(kb.id),
        tenant_id=str(kb.tenant_id),
        name=kb.name,
        description=kb.description,
        is_active=kb.is_active,
        is_default=kb.is_default,
        tags=kb.tags or [],
        category=kb.category,
        priority=kb.priority,
        document_count=kb.document_count,
        total_size_bytes=kb.total_size_bytes,
        size_mb=kb.size_mb,
        last_updated=kb.last_updated.isoformat() if kb.last_updated else None,
        embedding_model=kb.embedding_model,
        chunk_size=kb.chunk_size,
        chunk_overlap=kb.chunk_overlap,
        created_at=kb.created_at.isoformat(),
        updated_at=kb.updated_at.isoformat()
    )


@router.post("/bases", response_model=KnowledgeBaseResponse)
async def create_knowledge_base(
    kb_create: KnowledgeBaseCreate,
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db)
) -> Any:
    """
    Create a new knowledge base
    Requires admin permissions
    """
    # Get current user
    current_user = await auth_service.get_current_user(db, credentials)
    
    # Check permissions
    if current_user.role == UserRole.USER:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    if not current_user.tenant_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User is not associated with any tenant"
        )
    
    # Create knowledge base
    kb = await knowledge_service.create_knowledge_base(
        db, kb_create, current_user.tenant_id
    )
    
    return KnowledgeBaseResponse(
        id=str(kb.id),
        tenant_id=str(kb.tenant_id),
        name=kb.name,
        description=kb.description,
        is_active=kb.is_active,
        is_default=kb.is_default,
        tags=kb.tags or [],
        category=kb.category,
        priority=kb.priority,
        document_count=kb.document_count,
        total_size_bytes=kb.total_size_bytes,
        size_mb=kb.size_mb,
        last_updated=kb.last_updated.isoformat() if kb.last_updated else None,
        embedding_model=kb.embedding_model,
        chunk_size=kb.chunk_size,
        chunk_overlap=kb.chunk_overlap,
        created_at=kb.created_at.isoformat(),
        updated_at=kb.updated_at.isoformat()
    )


@router.put("/bases/{knowledge_base_id}", response_model=KnowledgeBaseResponse)
async def update_knowledge_base(
    knowledge_base_id: UUID,
    kb_update: KnowledgeBaseUpdate,
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db)
) -> Any:
    """
    Update knowledge base
    Requires admin permissions
    """
    # Get current user
    current_user = await auth_service.get_current_user(db, credentials)
    
    # Check permissions
    if current_user.role == UserRole.USER:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    # Update knowledge base
    kb = await knowledge_service.update_knowledge_base(
        db, knowledge_base_id, kb_update, current_user.tenant_id
    )
    
    return KnowledgeBaseResponse(
        id=str(kb.id),
        tenant_id=str(kb.tenant_id),
        name=kb.name,
        description=kb.description,
        is_active=kb.is_active,
        is_default=kb.is_default,
        tags=kb.tags or [],
        category=kb.category,
        priority=kb.priority,
        document_count=kb.document_count,
        total_size_bytes=kb.total_size_bytes,
        size_mb=kb.size_mb,
        last_updated=kb.last_updated.isoformat() if kb.last_updated else None,
        embedding_model=kb.embedding_model,
        chunk_size=kb.chunk_size,
        chunk_overlap=kb.chunk_overlap,
        created_at=kb.created_at.isoformat(),
        updated_at=kb.updated_at.isoformat()
    )


@router.delete("/bases/{knowledge_base_id}")
async def delete_knowledge_base(
    knowledge_base_id: UUID,
    hard_delete: bool = Query(False),
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db)
) -> Any:
    """
    Delete knowledge base
    Requires admin permissions
    """
    # Get current user
    current_user = await auth_service.get_current_user(db, credentials)
    
    # Check permissions
    if current_user.role == UserRole.USER:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    # Delete knowledge base
    success = await knowledge_service.delete_knowledge_base(
        db, knowledge_base_id, current_user.tenant_id, hard_delete
    )
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete knowledge base"
        )
    
    return {"message": "Knowledge base deleted successfully"}


@router.get("/bases/{knowledge_base_id}/documents", response_model=DocumentListResponse)
async def list_documents(
    knowledge_base_id: UUID,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    file_type: Optional[DocumentType] = None,
    status: Optional[DocumentStatus] = None,
    search: Optional[str] = None,
    uploaded_after: Optional[datetime] = None,
    uploaded_before: Optional[datetime] = None,
    tags: Optional[List[str]] = Query(None),
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db)
) -> Any:
    """
    List documents in a knowledge base
    """
    # Get current user
    current_user = await auth_service.get_current_user(db, credentials)
    
    # Create filters
    filters = DocumentFilters(
        file_type=file_type,
        status=status,
        search=search,
        uploaded_after=uploaded_after,
        uploaded_before=uploaded_before,
        tags=tags
    )
    
    # Get documents
    result = await knowledge_service.list_documents(
        db, knowledge_base_id, current_user.tenant_id, filters, skip, limit
    )
    
    # Convert to response format
    doc_responses = []
    for doc in result["documents"]:
        doc_responses.append(DocumentResponse(
            id=str(doc.id),
            knowledge_base_id=str(doc.knowledge_base_id),
            filename=doc.filename,
            original_filename=doc.original_filename,
            file_type=doc.file_type.value,
            file_size_bytes=doc.file_size_bytes,
            size_mb=doc.size_mb,
            file_hash=doc.file_hash,
            title=doc.title,
            summary=doc.summary,
            status=doc.status.value,
            processing_error=doc.processing_error,
            chunk_count=doc.chunk_count,
            embedding_status=doc.embedding_status,
            language=doc.language,
            word_count=doc.word_count,
            page_count=doc.page_count,
            keywords=doc.keywords or [],
            topics=doc.topics or [],
            entities=doc.entities or [],
            access_count=doc.access_count,
            last_accessed=doc.last_accessed.isoformat() if doc.last_accessed else None,
            uploaded_by=str(doc.uploaded_by) if doc.uploaded_by else None,
            created_at=doc.created_at.isoformat(),
            updated_at=doc.updated_at.isoformat(),
            processed_at=doc.processed_at.isoformat() if doc.processed_at else None
        ))
    
    return DocumentListResponse(
        documents=doc_responses,
        total=result["total"],
        skip=result["skip"],
        limit=result["limit"]
    )


@router.post("/bases/{knowledge_base_id}/documents/upload")
async def upload_document(
    knowledge_base_id: UUID,
    file: UploadFile = File(...),
    title: Optional[str] = Form(None),
    tags: Optional[List[str]] = Form(None),
    language: Optional[str] = Form(None),
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db)
) -> Any:
    """
    Upload a document to a knowledge base
    """
    # Get current user
    current_user = await auth_service.get_current_user(db, credentials)
    
    # Validate file type
    file_extension = Path(file.filename).suffix.lower()
    supported_extensions = {
        '.pdf': DocumentType.PDF,
        '.txt': DocumentType.TEXT,
        '.docx': DocumentType.DOCX,
        '.md': DocumentType.MARKDOWN,
        '.csv': DocumentType.CSV,
        '.json': DocumentType.JSON
    }
    
    if file_extension not in supported_extensions:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unsupported file type: {file_extension}"
        )
    
    # Read file content
    content = await file.read()
    file_hash = hashlib.sha256(content).hexdigest()
    
    # Create document
    document = await knowledge_service.upload_document(
        db=db,
        knowledge_base_id=knowledge_base_id,
        tenant_id=current_user.tenant_id,
        filename=file.filename,
        content=content,
        file_type=supported_extensions[file_extension],
        file_hash=file_hash,
        title=title,
        tags=tags,
        language=language,
        uploaded_by=current_user.id
    )
    
    return {
        "message": "Document uploaded successfully",
        "document_id": str(document.id),
        "status": document.status.value
    }


@router.delete("/documents/{document_id}")
async def delete_document(
    document_id: UUID,
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db)
) -> Any:
    """
    Delete a document
    """
    # Get current user
    current_user = await auth_service.get_current_user(db, credentials)
    
    # Delete document
    success = await knowledge_service.delete_document(
        db, document_id, current_user.tenant_id
    )
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found or access denied"
        )
    
    return {"message": "Document deleted successfully"}


@router.post("/search", response_model=SearchResponse)
async def search_knowledge_base(
    search_query: SearchQuery,
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db)
) -> Any:
    """
    Search across knowledge bases
    """
    # Get current user
    current_user = await auth_service.get_current_user(db, credentials)
    
    # Perform search
    results = await knowledge_service.search_knowledge_bases(
        db=db,
        tenant_id=current_user.tenant_id,
        query=search_query.query,
        knowledge_base_ids=search_query.knowledge_base_ids,
        limit=search_query.limit,
        include_summary=search_query.include_summary,
        include_metadata=search_query.include_metadata,
        min_relevance_score=search_query.min_relevance_score
    )
    
    return SearchResponse(**results)


@router.get("/bases/{knowledge_base_id}/statistics", response_model=KnowledgeBaseStatistics)
async def get_knowledge_base_statistics(
    knowledge_base_id: UUID,
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db)
) -> Any:
    """
    Get knowledge base statistics
    """
    # Get current user
    current_user = await auth_service.get_current_user(db, credentials)
    
    # Get statistics
    stats = await knowledge_service.get_knowledge_base_statistics(
        db, knowledge_base_id, current_user.tenant_id
    )
    
    return KnowledgeBaseStatistics(**stats)