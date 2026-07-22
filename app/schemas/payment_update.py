from pydantic import BaseModel


class PaymentUpdate(BaseModel):
    status: str