"""
Analytics API Endpoints
Provides basic analytics and usage metrics
"""

from fastapi import APIRouter, Depends, HTTPException, Query, status
from fastapi.security import HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from app.core.database import get_db
from app.services.auth import auth_service, security
from app.models.billing import UsageMetric
from app.schemas.analytics import UsageMetricListResponse, UsageMetricResponse

router = APIRouter()


@router.get("/usage", response_model=UsageMetricListResponse)
async def list_usage_metrics(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db),
):
    """List usage metrics for the current tenant"""
    user = await auth_service.get_current_user(db, credentials)
    if not user.tenant_id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="User is not associated with a tenant")

    query = select(UsageMetric).where(UsageMetric.tenant_id == user.tenant_id).order_by(UsageMetric.date.desc())
    count_query = select(func.count()).select_from(UsageMetric).where(UsageMetric.tenant_id == user.tenant_id)

    result = await db.execute(query.offset(skip).limit(limit))
    metrics = result.scalars().all()
    total = (await db.execute(count_query)).scalar()

    metric_responses = [
        UsageMetricResponse(
            id=str(m.id),
            metric_type=m.metric_type.value,
            metric_name=m.metric_name,
            date=m.date,
            count=m.count,
            cost_usd=float(m.cost_usd) if m.cost_usd is not None else None,
        )
        for m in metrics
    ]

    return UsageMetricListResponse(metrics=metric_responses, total=total, skip=skip, limit=limit)
