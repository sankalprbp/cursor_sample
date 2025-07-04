"""
Main API Router
Combines all API endpoints for the voice agent platform
"""

from fastapi import APIRouter

from app.api.v1.endpoints import (
    auth,
    users,
    tenants,
    calls,
    knowledge,
    webhooks,
    billing,
    analytics,
    admin,
    voice,
)

# Create main API router
api_router = APIRouter()

# Include all endpoint routers
api_router.include_router(
    auth.router,
    prefix="/auth",
    tags=["Authentication"]
)

api_router.include_router(
    users.router,
    prefix="/users",
    tags=["Users"]
)

api_router.include_router(
    tenants.router,
    prefix="/tenants",
    tags=["Tenants"]
)

api_router.include_router(
    calls.router,
    prefix="/calls",
    tags=["Calls"]
)

api_router.include_router(
    knowledge.router,
    prefix="/knowledge",
    tags=["Knowledge Base"]
)

api_router.include_router(
    webhooks.router,
    prefix="/webhooks",
    tags=["Webhooks"]
)

api_router.include_router(
    billing.router,
    prefix="/billing",
    tags=["Billing"]
)

api_router.include_router(
    analytics.router,
    prefix="/analytics",
    tags=["Analytics"]
)

api_router.include_router(
    admin.router,
    prefix="/admin",
    tags=["Administration"]
)

api_router.include_router(
    voice.router,
    prefix="/voice",
    tags=["Voice Agent"]
)