from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel

class CallResponse(BaseModel):
    id: str
    caller_number: Optional[str]
    status: str
    started_at: Optional[datetime]
    ended_at: Optional[datetime]
    duration_seconds: Optional[int]
    summary: Optional[str]

class CallListResponse(BaseModel):
    calls: List[CallResponse]
    total: int
    skip: int
    limit: int
