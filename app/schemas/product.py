from datetime import datetime
from decimal import Decimal
from pydantic import BaseModel
from app.schemas.category import CategorySimple


class ProductCreate(BaseModel):
    name: str
    description: str | None = None
    price: Decimal
    stock: int
    image_url: str | None = None
    category_id: int


class ProductResponse(BaseModel):
    id: int
    name: str
    description: str | None
    price: Decimal
    stock: int
    image_url: str | None

    category: CategorySimple

    created_at: datetime

    class Config:
        from_attributes = True