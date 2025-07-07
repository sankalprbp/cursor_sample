"""
Tenants API Endpoints - Basic Implementation
"""

from fastapi import APIRouter

router = APIRouter()

@router.get("/")
async def list_tenants():
    """List tenants - placeholder implementation"""
    return {"message": "Tenants endpoint - coming soon"}