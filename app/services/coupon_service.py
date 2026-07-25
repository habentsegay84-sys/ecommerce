from sqlalchemy.orm import Session

from app.models.coupon import Coupon
from app.repositories.coupon_repository import CouponRepository
from app.schemas.coupon import (
    CouponCreate,
    CouponUpdate,
)

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

def list_coupons_service(
    db: Session,
):
    """
    Return all coupons.
    """

    repository = CouponRepository(db)

    return repository.list_all()

def update_coupon_service(
    db: Session,
    coupon_id: int,
    coupon_data: CouponUpdate,
):
    """
    Update an existing coupon.
    """

    repository = CouponRepository(db)

    coupon = repository.get_by_id(
        coupon_id,
    )

    if coupon is None:
        raise ValueError(
            "Coupon not found."
        )

    update_data = coupon_data.model_dump(
        exclude_unset=True
    )

    for key, value in update_data.items():
        setattr(
            coupon,
            key,
            value,
        )

    return repository.update(coupon)

def delete_coupon_service(
    db: Session,
    coupon_id: int,
):
    """
    Delete a coupon.
    """

    repository = CouponRepository(db)

    coupon = repository.get_by_id(
        coupon_id,
    )

    if coupon is None:
        raise ValueError(
            "Coupon not found."
        )

    repository.delete(coupon)