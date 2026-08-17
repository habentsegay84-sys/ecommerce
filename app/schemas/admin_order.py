from datetime import datetime
from pydantic import BaseModel, ConfigDict


class AdminOrderItemResponse(BaseModel):
    product_name: str
    quantity: int
    price: float

    model_config = ConfigDict(
        from_attributes=True
    )


class AdminOrderResponse(BaseModel):
    id: int
    customer: str
    email: str
    total_price: float
    status: str
    created_at: datetime
    items: list[AdminOrderItemResponse]

    model_config = ConfigDict(
        from_attributes=True
    )