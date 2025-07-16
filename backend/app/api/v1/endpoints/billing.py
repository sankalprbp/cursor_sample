"""
Billing API Endpoints
Provide subscription information for tenants
"""

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.database import get_db
from app.services.auth import auth_service, security
from app.models.tenant import TenantSubscription
from app.schemas.billing import SubscriptionResponse

router = APIRouter()


@router.get("/subscription", response_model=SubscriptionResponse)
async def get_subscription(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db),
):
    """Get the current tenant subscription"""
    user = await auth_service.get_current_user(db, credentials)
    if not user.tenant_id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="User is not associated with a tenant")

    stmt = select(TenantSubscription).where(TenantSubscription.tenant_id == user.tenant_id)
    result = await db.execute(stmt)
    sub = result.scalar_one_or_none()
    if not sub:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Subscription not found")

    return SubscriptionResponse(
        tenant_id=str(sub.tenant_id),
        plan=sub.plan.value,
        status=sub.status,
        monthly_price=float(sub.monthly_price),
        price_per_call=float(sub.price_per_call),
        current_period_start=sub.current_period_start,
        current_period_end=sub.current_period_end,
    )
