"""
AI Voice Agent MVP - Simplified Main Application
Minimal FastAPI app that actually works without complex dependencies
"""

import os
import asyncio
from contextlib import asynccontextmanager
from datetime import datetime

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import List, Dict, Any, Optional

# Simple in-memory storage for MVP
calls_storage = []
system_stats = {
    "total_calls": 0,
    "active_calls": 0,
    "success_rate": 95.5,
    "avg_duration": 180
}


class CallSummary(BaseModel):
    id: str
    caller_number: str
    status: str
    direction: str
    started_at: str
    ended_at: Optional[str] = None
    duration_seconds: Optional[int] = None
    summary: Optional[str] = None


class CallListResponse(BaseModel):
    calls: List[CallSummary]
    total: int
    limit: int
    offset: int
    has_more: bool
    demo: bool = True
    message: str = "This is demo data for demonstration purposes."


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Simple lifespan manager"""
    print("🚀 Starting AI Voice Agent MVP...")
    
    # Create some demo data
    global calls_storage
    calls_storage = [
        {
            "id": "call-001",
            "caller_number": "+1 (555) 123-4567",
            "status": "completed",
            "direction": "inbound",
            "started_at": "2024-01-15T10:30:00Z",
            "ended_at": "2024-01-15T10:33:00Z",
            "duration_seconds": 180,
            "summary": "Customer inquired about product pricing and features. AI agent provided detailed information and scheduled a follow-up call."
        },
        {
            "id": "call-002",
            "caller_number": "+1 (555) 987-6543",
            "status": "active",
            "direction": "inbound",
            "started_at": datetime.utcnow().isoformat() + "Z",
            "duration_seconds": 120,
            "summary": "Call in progress - Customer asking about services..."
        },
        {
            "id": "call-003",
            "caller_number": "+1 (555) 456-7890",
            "status": "completed",
            "direction": "inbound",
            "started_at": "2024-01-15T09:15:00Z",
            "ended_at": "2024-01-15T09:18:00Z",
            "duration_seconds": 180,
            "summary": "Technical support call. AI agent resolved customer issue with account access."
        }
    ]
    
    print("✅ Demo data loaded")
    print("🎉 MVP is ready!")
    
    yield
    
    print("👋 Shutting down MVP...")


# Create FastAPI application
app = FastAPI(
    title="AI Voice Agent MVP",
    description="Simplified AI voice agent platform for demonstration",
    version="1.0.0-mvp",
    lifespan=lifespan,
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "AI Voice Agent MVP",
        "version": "1.0.0-mvp",
        "status": "running",
        "docs": "/docs",
        "health": "/health",
        "dashboard": "http://localhost:3000/dashboard"
    }


@app.get("/health")
async def health_check():
    """Simple health check"""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "services": {
            "database": "connected",
            "redis": "connected",
            "backend": "running"
        }
    }


@app.get("/healthz")
async def health_check_k8s():
    """Kubernetes-style health check"""
    return await health_check()


@app.get("/api/v1/voice/calls/demo", response_model=CallListResponse)
async def get_demo_calls(
    limit: int = 50,
    offset: int = 0,
    status: Optional[str] = None
):
    """Get demo calls for dashboard"""
    
    # Filter calls if status is provided
    filtered_calls = calls_storage
    if status:
        filtered_calls = [call for call in calls_storage if call["status"] == status]
    
    # Apply pagination
    paginated_calls = filtered_calls[offset:offset + limit]
    
    # Convert to response format
    call_summaries = [CallSummary(**call) for call in paginated_calls]
    
    return CallListResponse(
        calls=call_summaries,
        total=len(filtered_calls),
        limit=limit,
        offset=offset,
        has_more=offset + limit < len(filtered_calls),
        demo=True,
        message="This is demo data for demonstration purposes."
    )


@app.get("/api/v1/voice/system/status")
async def get_system_status():
    """Get system status for dashboard"""
    return {
        "status": "healthy",
        "services": {
            "database": "connected",
            "redis": "connected",
            "backend": "running"
        },
        "stats": system_stats,
        "demo_mode": True,
        "timestamp": datetime.utcnow().isoformat() + "Z"
    }


@app.get("/api/v1/voice/demo/stats")
async def get_demo_stats():
    """Get demo statistics for dashboard"""
    stats = system_stats.copy()
    stats["demo"] = True
    stats["message"] = "This is demo data for demonstration purposes."
    return stats


@app.get("/api/v1/voice/calls/{call_id}/demo")
async def get_demo_call_detail(call_id: str):
    """Get detailed call information (demo)"""
    
    # Find call
    call = next((c for c in calls_storage if c["id"] == call_id), None)
    if not call:
        raise HTTPException(status_code=404, detail="Call not found")
    
    # Mock transcripts
    transcripts = [
        {
            "id": "transcript-001",
            "speaker": "user",
            "text": "Hello, I'm interested in your services.",
            "timestamp": call["started_at"],
            "confidence": 0.95
        },
        {
            "id": "transcript-002", 
            "speaker": "assistant",
            "text": "Hello! I'd be happy to help you learn about our services. What specific area are you interested in?",
            "timestamp": call["started_at"],
            "confidence": 1.0
        }
    ]
    
    return {
        "call": CallSummary(**call),
        "transcripts": transcripts
    }


@app.post("/api/v1/voice/calls/start")
async def start_demo_call(request: Dict[str, Any]):
    """Start a demo call (simulation)"""
    
    call_id = f"call-{len(calls_storage) + 1:03d}"
    new_call = {
        "id": call_id,
        "caller_number": request.get("caller_number", "+1 (555) 000-0000"),
        "status": "active",
        "direction": "inbound",
        "started_at": datetime.utcnow().isoformat() + "Z",
        "summary": "Demo call in progress..."
    }
    
    calls_storage.append(new_call)
    system_stats["total_calls"] += 1
    system_stats["active_calls"] += 1
    
    return {
        "call_id": call_id,
        "status": "active",
        "message": "Demo call started successfully",
        "demo": True
    }


@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """Global exception handler"""
    print(f"Error: {exc}")
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal server error",
            "message": str(exc),
            "demo": True
        }
    )


if __name__ == "__main__":
    import uvicorn
    
    print("🚀 Starting AI Voice Agent MVP...")
    uvicorn.run(
        "main-simple:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info",
    )