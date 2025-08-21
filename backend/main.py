"""
Multi-Tenant AI Voice Agent Platform
Main FastAPI application
"""

import os
import asyncio
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse
import sentry_sdk
from sentry_sdk.integrations.fastapi import FastApiIntegration
from sentry_sdk.integrations.sqlalchemy import SqlalchemyIntegration

from app.core.config import settings
from app.core.database import engine, Base
from sqlalchemy import text
from app.core.database_init import create_tables, create_sample_data
from app.core.redis_client import redis_client
from app.core.minio_client import get_minio_client
from app.api.v1.router import api_router
from app.websocket.connection_manager import ConnectionManager


# Initialize Sentry for error tracking
if settings.SENTRY_DSN and settings.SENTRY_DSN.strip():
    sentry_sdk.init(
        dsn=settings.SENTRY_DSN,
        integrations=[
            FastApiIntegration(),
            SqlalchemyIntegration(),
        ],
        traces_sample_rate=0.1,
    )


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager"""
    # Startup
    startup_errors = []
    
    try:
        # Initialize database tables
        print("🔧 Initializing database...")
        try:
            await create_tables()
            print("✅ Database tables created successfully")
        except Exception as e:
            startup_errors.append(f"Database initialization failed: {e}")
            print(f"⚠️  Database initialization failed: {e}")
        
        # Create sample data if needed (only in development)
        if settings.ENVIRONMENT == "development":
            try:
                await create_sample_data()
                print("✅ Sample data created successfully")
            except Exception as e:
                # Sample data might already exist, just log and continue
                print(f"ℹ️  Sample data creation skipped: {e}")
        
        # Initialize Redis connection
        print("🔧 Connecting to Redis...")
        try:
            await redis_client.ping()
            print("✅ Redis connection established")
        except Exception as e:
            startup_errors.append(f"Redis connection failed: {e}")
            print(f"⚠️  Redis connection failed: {e}")
        
        # Initialize WebSocket connection manager
        try:
            app.state.connection_manager = ConnectionManager()
            print("✅ WebSocket connection manager initialized")
        except Exception as e:
            startup_errors.append(f"WebSocket manager initialization failed: {e}")
            print(f"⚠️  WebSocket manager initialization failed: {e}")
        
        if startup_errors:
            print(f"⚠️  Application started with {len(startup_errors)} warnings:")
            for error in startup_errors:
                print(f"   - {error}")
        else:
            print("🚀 Voice Agent Platform started successfully!")
        
    except Exception as e:
        print(f"❌ Critical startup failure: {e}")
        # Don't raise the exception to allow the app to start in degraded mode
        print("⚠️  Starting in degraded mode...")
    
    yield
    
    # Shutdown
    try:
        print("🔧 Shutting down services...")
        try:
            await redis_client.close()
        except Exception as e:
            print(f"⚠️  Redis shutdown error: {e}")
        
        try:
            await engine.dispose()
        except Exception as e:
            print(f"⚠️  Database shutdown error: {e}")
        
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


@app.get("/healthz")
async def health_check() -> dict:
    """Comprehensive health check endpoint"""
    db_ok = redis_ok = minio_ok = False

    try:
        async with engine.begin() as conn:
            await conn.execute(text("SELECT 1"))
        db_ok = True
    except Exception:
        db_ok = False

    try:
        await redis_client.ping()
        redis_ok = True
    except Exception:
        redis_ok = False

    minio_client = get_minio_client()
    if minio_client:
        try:
            await asyncio.to_thread(minio_client.list_buckets)
            minio_ok = True
        except Exception:
            minio_ok = False
    else:
        minio_ok = None

    status = "ok" if all(x is not False for x in (db_ok, redis_ok, minio_ok)) else "error"
    return {
        "status": status,
        "database": db_ok,
        "redis": redis_ok,
        "minio": minio_ok,
    }


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Voice Agent Platform API",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/healthz",
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

    print("🚀 Starting Uvicorn server...")

    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG,
        log_level=settings.LOG_LEVEL.lower(),
    )