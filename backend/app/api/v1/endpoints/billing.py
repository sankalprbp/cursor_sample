"""
Billing API Endpoints - Basic Implementation
"""

from fastapi import APIRouter

router = APIRouter()

@router.get("/")
async def list_billing():
    """List billing - placeholder implementation"""
    return {"message": "Billing endpoint - coming soon"}