from datetime import datetime
from pydantic import BaseModel


class OrderTrackingHistoryResponse(BaseModel):

    old_status: str | None
    new_status: str
    created_at: datetime


class OrderTrackingResponse(BaseModel):

    order_id: int
    current_status: str
    history: list[OrderTrackingHistoryResponse]