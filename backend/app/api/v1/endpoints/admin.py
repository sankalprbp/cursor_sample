"""
Admin API Endpoints - Basic Implementation
"""

from fastapi import APIRouter

router = APIRouter()

@router.get("/")
async def admin_dashboard():
    """Admin dashboard - placeholder implementation"""
    return {"message": "Admin endpoint - coming soon"}