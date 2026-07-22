from datetime import datetime
from pydantic import BaseModel, ConfigDict


class PaymentResponse(BaseModel):

    id: int
    order_id: int
    amount: float

    payment_method: str

    status: str

    transaction_reference: str | None

    paid_at: datetime | None

    created_at: datetime

    model_config = ConfigDict(
        from_attributes=True
    )


class PaymentCreate(BaseModel):

    payment_method: str