from datetime import datetime

from pydantic import BaseModel
from pydantic import ConfigDict

class CouponCreate(BaseModel):
    """
    Request body for creating a coupon.
    """

    code: str
    discount_percent: float
    expires_at: datetime | None = None

class CouponUpdate(BaseModel):
    """
    Request body for updating a coupon.
    """

    code: str | None = None
    discount_percent: float | None = None
    active: bool | None = None
    expires_at: datetime | None = None

class CouponResponse(BaseModel):
    """
    Response returned to the client.
    """

    id: int
    code: str
    discount_percent: float
    active: bool
    expires_at: datetime | None
    created_at: datetime

    model_config = ConfigDict(
        from_attributes=True,
    )