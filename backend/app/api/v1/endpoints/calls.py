"""Calls API Endpoints"""

from fastapi import APIRouter, Depends, HTTPException, Query, status
from fastapi.security import HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from app.core.database import get_db
from app.services.auth import auth_service, security
from app.models.call import Call
from app.schemas.call import CallResponse, CallListResponse

router = APIRouter()


@router.get("/", response_model=CallListResponse)
async def list_calls(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db),
):
    """List recent calls for the current tenant"""
    user = await auth_service.get_current_user(db, credentials)
    if not user.tenant_id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="User is not associated with a tenant")

    stmt = select(Call).where(Call.tenant_id == user.tenant_id).order_by(Call.started_at.desc())
    count_stmt = select(func.count()).select_from(Call).where(Call.tenant_id == user.tenant_id)

    result = await db.execute(stmt.offset(skip).limit(limit))
    calls = result.scalars().all()
    total = (await db.execute(count_stmt)).scalar()

    call_responses = [
        CallResponse(
            id=str(c.id),
            caller_number=c.caller_number,
            status=c.status.value,
            started_at=c.started_at,
            ended_at=c.ended_at,
            duration_seconds=c.duration_seconds,
            summary=c.summary,
        )
        for c in calls
    ]

    return CallListResponse(calls=call_responses, total=total, skip=skip, limit=limit)
