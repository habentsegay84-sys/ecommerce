from sqlalchemy.orm import Session

from app.models.coupon import Coupon
from app.repositories.coupon_repository import CouponRepository
from app.schemas.coupon import CouponCreate

def create_coupon_service(
    db: Session,
    coupon_data: CouponCreate,
):
    """
    Create a new coupon after validating
    business rules.
    """

    coupon_repository = CouponRepository(db)

    existing_coupon = coupon_repository.get_by_code(
        coupon_data.code,
    )

    if existing_coupon:
        raise ValueError(
            "Coupon code already exists."
        )

    coupon = Coupon(
        code=coupon_data.code,
        discount_percent=coupon_data.discount_percent,
        active=True,
        expires_at=coupon_data.expires_at,
    )

    return coupon_repository.create(coupon)