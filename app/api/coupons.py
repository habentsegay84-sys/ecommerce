from fastapi import APIRouter
from fastapi import Depends

from sqlalchemy.orm import Session

from app.database.session import get_db
from app.schemas.coupon import CouponCreate
from app.schemas.coupon import CouponResponse
from app.services.coupon_service import create_coupon_service

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
    db: Session = Depends(get_db),
):
    """
    Create a new coupon.
    """

    return create_coupon_service(
        db=db,
        coupon_data=coupon_data,
    )