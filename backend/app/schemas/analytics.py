from datetime import date
from typing import List, Optional
from pydantic import BaseModel

class UsageMetricResponse(BaseModel):
    id: str
    metric_type: str
    metric_name: str
    date: date
    count: int
    cost_usd: Optional[float] = None

    class Config:
        from_attributes = True

class UsageMetricListResponse(BaseModel):
    metrics: List[UsageMetricResponse]
    total: int
    skip: int
    limit: int
