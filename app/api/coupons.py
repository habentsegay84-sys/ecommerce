from fastapi import APIRouter
from fastapi import Depends
from fastapi import HTTPException

from sqlalchemy.orm import Session

from app.auth.admin import get_current_admin
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

    Only authenticated administrators can create coupons.
    Business-rule validation is delegated to the service layer,
    while service errors are translated into HTTP responses here.
    """

    try:
        return create_coupon_service(
            db=db,
            coupon_data=coupon_data,
        )

    except ValueError as e:
        if str(e) == "Coupon code already exists.":
            raise HTTPException(
                status_code=400,
                detail=str(e),
            )

        raise HTTPException(
            status_code=400,
            detail=str(e),
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
    Return all coupons.

    Coupon management is restricted to administrators.
    """

    return list_coupons_service(
        db=db,
    )


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
    Update an existing coupon.

    The service layer validates that the coupon exists
    and applies the requested partial update.
    """

    try:
        return update_coupon_service(
            db=db,
            coupon_id=coupon_id,
            coupon_data=coupon_data,
        )

    except ValueError as e:
        if str(e) == "Coupon not found.":
            raise HTTPException(
                status_code=404,
                detail=str(e),
            )

        raise HTTPException(
            status_code=400,
            detail=str(e),
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
    Delete an existing coupon.

    Only administrators can delete coupons.
    """

    try:
        delete_coupon_service(
            db=db,
            coupon_id=coupon_id,
        )

    except ValueError as e:
        if str(e) == "Coupon not found.":
            raise HTTPException(
                status_code=404,
                detail=str(e),
            )

        raise HTTPException(
            status_code=400,
            detail=str(e),
        )

    return {
        "message": "Coupon deleted successfully.",
    }