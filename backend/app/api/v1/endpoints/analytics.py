"""
Analytics API Endpoints - Basic Implementation
"""

from fastapi import APIRouter

router = APIRouter()

@router.get("/")
async def get_analytics():
    """Get analytics - placeholder implementation"""
    return {"message": "Analytics endpoint - coming soon"}