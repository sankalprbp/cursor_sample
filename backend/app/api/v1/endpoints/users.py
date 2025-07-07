"""
Users API Endpoints - Basic Implementation
"""

from fastapi import APIRouter

router = APIRouter()

@router.get("/")
async def list_users():
    """List users - placeholder implementation"""
    return {"message": "Users endpoint - coming soon"}