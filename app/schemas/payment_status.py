from pydantic import BaseModel

from app.constants.payment_status import (
    PENDING,
    PROCESSING,
    SUCCESSFUL,
    FAILED,
)


class PaymentStatusUpdate(BaseModel):
    status: str