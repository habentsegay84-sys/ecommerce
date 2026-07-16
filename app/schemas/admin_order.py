from datetime import datetime
from pydantic import BaseModel


class AdminOrderItemResponse(BaseModel):

    product_name: str
    quantity: int
    price: float

    class Config:
        from_attributes = True



class AdminOrderResponse(BaseModel):

    id: int

    customer: str
    email: str

    total_price: float
    status: str

    created_at: datetime

    items: list[AdminOrderItemResponse]

    class Config:
        from_attributes = True