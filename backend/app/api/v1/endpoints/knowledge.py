"""
Knowledge Base API Endpoints - Basic Implementation
"""

from fastapi import APIRouter

router = APIRouter()

@router.get("/")
async def list_knowledge_bases():
    """List knowledge bases - placeholder implementation"""
    return {"message": "Knowledge endpoint - coming soon"}