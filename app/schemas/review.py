from datetime import datetime

from pydantic import BaseModel
from pydantic import ConfigDict
from pydantic import Field


class ReviewCreate(BaseModel):
    """
    Request body for creating a review.
    """

    rating: int = Field(
        ge=1,
        le=5,
    )

    comment: str | None = None


class ReviewUpdate(BaseModel):
    """
    Request body for updating a review.
    """

    rating: int | None = Field(
        default=None,
        ge=1,
        le=5,
    )

    comment: str | None = None


class ReviewResponse(BaseModel):
    """
    Response returned to the client.
    """

    id: int
    rating: int
    comment: str | None
    user_id: int
    product_id: int
    created_at: datetime

    model_config = ConfigDict(
        from_attributes=True,
    )