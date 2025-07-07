"""
Multi-Tenant AI Voice Agent Platform
Main FastAPI application
"""

import os
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse
import sentry_sdk
from sentry_sdk.integrations.fastapi import FastApiIntegration
from sentry_sdk.integrations.sqlalchemy import SqlalchemyIntegration

from app.core.config import settings
from app.core.database import engine, Base
from app.core.redis_client import redis_client
from app.api.v1.router import api_router
from app.websocket.connection_manager import ConnectionManager


# Initialize Sentry for error tracking
if settings.SENTRY_DSN:
    sentry_sdk.init(
        dsn=settings.SENTRY_DSN,
        integrations=[
            FastApiIntegration(auto_enabling=True),
            SqlalchemyIntegration(),
        ],
        traces_sample_rate=0.1,
    )


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager"""
    # Startup
    try:
        # Initialize database tables
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        
        # Initialize Redis connection
        await redis_client.ping()
        
        # Initialize WebSocket connection manager
        app.state.connection_manager = ConnectionManager()
        
        print("🚀 Voice Agent Platform started successfully!")
        
    except Exception as e:
        print(f"❌ Failed to start application: {e}")
        raise
    
    yield
    
    # Shutdown
    try:
        await redis_client.close()
        await engine.dispose()
        print("👋 Voice Agent Platform shut down gracefully")
    except Exception as e:
        print(f"❌ Error during shutdown: {e}")


# Create FastAPI application
app = FastAPI(
    title="Voice Agent Platform API",
    description="Multi-tenant AI voice agent platform for business call handling",
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs" if settings.DEBUG else None,
    redoc_url="/redoc" if settings.DEBUG else None,
)

# Add middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.get_allowed_origins(),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(
    TrustedHostMiddleware, 
    allowed_hosts=settings.get_allowed_hosts()
)

# Include API routers
app.include_router(api_router, prefix="/api/v1")


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    try:
        # Check database connection
        async with engine.begin() as conn:
            await conn.execute("SELECT 1")
        
        # Check Redis connection
        await redis_client.ping()
        
        return {
            "status": "healthy",
            "version": "1.0.0",
            "environment": settings.ENVIRONMENT,
            "services": {
                "database": "connected",
                "redis": "connected",
            }
        }
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"Service unhealthy: {str(e)}")


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Voice Agent Platform API",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/health",
    }


@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """Global exception handler"""
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal server error",
            "message": str(exc) if settings.DEBUG else "Something went wrong",
        }
    )


if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG,
        log_level=settings.LOG_LEVEL.lower(),
    )