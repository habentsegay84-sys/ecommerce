from pydantic import BaseModel


class CartItemCreate(BaseModel):
    product_id: int
    quantity: int


class CartItemResponse(BaseModel):
    product_id: int
    product_name: str
    price: float
    quantity: int
    subtotal: float


class CartResponse(BaseModel):
    items: list[CartItemResponse]
    total: float

class CartItemUpdate(BaseModel):
    quantity: int