from datetime import datetime
from typing import Optional
from pydantic import BaseModel

class SubscriptionResponse(BaseModel):
    tenant_id: str
    plan: str
    status: str
    monthly_price: float
    price_per_call: float
    current_period_start: Optional[datetime] = None
    current_period_end: Optional[datetime] = None

    class Config:
        from_attributes = True
