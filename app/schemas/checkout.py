from pydantic import BaseModel


class CheckoutRequest(BaseModel):
    coupon_code: str | None = None