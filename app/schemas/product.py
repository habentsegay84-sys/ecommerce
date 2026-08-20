from datetime import datetime
from decimal import Decimal
from pydantic import BaseModel, ConfigDict
from typing import Optional
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

    average_rating: float | None = None
    review_count: int = 0

    category: CategorySimple

    created_at: datetime

    model_config = ConfigDict(
        from_attributes=True
    )

class ProductUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    price: Optional[Decimal] = None
    stock: Optional[int] = None
    category_id: Optional[int] = None