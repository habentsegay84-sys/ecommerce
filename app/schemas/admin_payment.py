from datetime import datetime
from pydantic import BaseModel


class AdminPaymentResponse(BaseModel):

    id: int

    order_id: int

    amount: float

    payment_method: str

    status: str

    transaction_reference: str | None

    paid_at: datetime | None

    created_at: datetime

    class Config:
        from_attributes = True