from datetime import datetime
from pydantic import BaseModel


class InventoryLogResponse(BaseModel):

    id: int
    product_id: int
    product_name: str

    old_stock: int
    new_stock: int

    change_type: str
    changed_by: int

    created_at: datetime

    class Config:
        from_attributes = True