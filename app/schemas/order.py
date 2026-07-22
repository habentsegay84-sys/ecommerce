from datetime import datetime
from pydantic import BaseModel, ConfigDict


class OrderItemResponse(BaseModel):
    product_id: int
    product_name: str
    quantity: int
    price: float
    subtotal: float

    model_config = ConfigDict(
        from_attributes=True
    )


class OrderResponse(BaseModel):
    id: int
    total_price: float
    status: str
    created_at: datetime
    items: list[OrderItemResponse]

    model_config = ConfigDict(
        from_attributes=True
    )