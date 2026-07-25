from fastapi import APIRouter
from fastapi import Depends

from sqlalchemy.orm import Session

from app.database.session import get_db

from app.models.user import User
from app.schemas.coupon import (
    CouponCreate,
    CouponUpdate,
    CouponResponse,
)

from app.services.coupon_service import (
    create_coupon_service,
    list_coupons_service,
    update_coupon_service,
    delete_coupon_service,
)
from app.auth.admin import get_current_admin

router = APIRouter(
    prefix="/coupons",
    tags=["Coupons"],
)

@router.post(
    "",
    response_model=CouponResponse,
)
def create_coupon(
    coupon_data: CouponCreate,
    current_admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db),
):
    """
    Create a new coupon.
    """

    return create_coupon_service(
        db=db,
        coupon_data=coupon_data,
    )

@router.get(
    "",
    response_model=list[CouponResponse],
)
def list_coupons(
    current_admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db),
):
    """
    List all coupons.
    """

    return list_coupons_service(db)

@router.patch(
    "/{coupon_id}",
    response_model=CouponResponse,
)
def update_coupon(
    coupon_id: int,
    coupon_data: CouponUpdate,
    current_admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db),
):
    """
    Update a coupon.
    """

    return update_coupon_service(
        db=db,
        coupon_id=coupon_id,
        coupon_data=coupon_data,
    )

@router.delete(
    "/{coupon_id}",
)
def delete_coupon(
    coupon_id: int,
    current_admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db),
):
    """
    Delete a coupon.
    """

    delete_coupon_service(
        db=db,
        coupon_id=coupon_id,
    )

    return {
        "message": "Coupon deleted successfully."
    }