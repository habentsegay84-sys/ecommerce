from datetime import datetime

from pydantic import BaseModel, ConfigDict


class CategoryCreate(BaseModel):
    name: str
    description: str | None = None


class CategoryResponse(BaseModel):
    id: int
    name: str
    description: str | None
    created_at: datetime

    model_config = ConfigDict(
        from_attributes=True
    )

class CategorySimple(BaseModel):
    id: int
    name: str

    model_config = ConfigDict(
        from_attributes=True
    )