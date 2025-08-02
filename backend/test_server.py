from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="Voice Agent Demo API")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {"message": "Voice Agent Demo API"}

@app.get("/api/v1/voice/twilio/demo/status")
async def get_twilio_demo_status():
    """
    Public demo endpoint to check Twilio status without authentication
    """
    return {
        "available": True,
        "configured": True,
        "demo_mode": True
    }

@app.get("/api/v1/calls")
async def get_calls():
    """
    Demo endpoint to get calls data
    """
    return {
        "calls": [
            {
                "id": "1",
                "caller_number": "+1 (555) 123-4567",
                "status": "completed",
                "started_at": "2024-01-15T10:30:00Z",
                "ended_at": "2024-01-15T10:31:00Z",
                "duration_seconds": 60,
                "summary": "Customer inquired about product pricing and features. AI agent provided detailed information and scheduled a follow-up call."
            },
            {
                "id": "2",
                "caller_number": "+1 (555) 987-6543",
                "status": "active",
                "started_at": "2024-01-15T11:00:00Z",
                "duration_seconds": 120,
                "summary": "In progress..."
            },
            {
                "id": "3",
                "caller_number": "+1 (555) 456-7890",
                "status": "completed",
                "started_at": "2024-01-15T09:00:00Z",
                "ended_at": "2024-01-15T09:01:00Z",
                "duration_seconds": 60,
                "summary": "Technical support call. AI agent resolved customer issue with account access."
            }
        ]
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)