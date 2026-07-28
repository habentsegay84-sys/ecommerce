from fastapi import APIRouter, Depends, HTTPException
from datetime import datetime
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.auth.dependencies import get_current_user

from app.models.user import User
from app.models.cart import Cart
from app.models.cart_item import CartItem
from app.models.order import Order
from app.models.order_item import OrderItem
from app.schemas.order import (
    OrderResponse,
    OrderItemResponse,
)
from app.models.order_status_history import OrderStatusHistory
from app.schemas.order_tracking import (
    OrderTrackingResponse,
    OrderTrackingHistoryResponse,
)
from app.schemas.checkout import CheckoutRequest
from app.models.coupon import Coupon
from app.schemas.order import CheckoutRequest
from app.services.order_service import (
    list_orders_service,
    get_order_service,
    track_order_service,
    checkout_service
)

router = APIRouter(
    prefix="/orders",
    tags=["Orders"],
)


@router.post("/checkout")
def checkout(
    checkout_data: CheckoutRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    try:

        order = checkout_service(
            db=db,
            user_id=current_user.id,
            checkout_data=checkout_data,
        )

        return {
            "message": "Order created successfully",
            "order_id": order.id,
            "total_price": order.total_price,
        }

    except ValueError as e:

        raise HTTPException(
            status_code=400,
            detail=str(e),
        )

@router.get(
    "",
    response_model=list[OrderResponse],
)
def list_orders(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):

    return list_orders_service(
        db=db,
        user_id=current_user.id,
    )

@router.get(
    "/{order_id}",
    response_model=OrderResponse,
)
def get_order(
    order_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):

    try:
        return get_order_service(
            db=db,
            order_id=order_id,
            user_id=current_user.id,
        )

    except ValueError as e:
        raise HTTPException(
            status_code=404,
            detail=str(e),
        )

@router.get(
    "/{order_id}/tracking",
    response_model=OrderTrackingResponse,
)
def track_order(
    order_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):

    try:
        return track_order_service(
            db=db,
            order_id=order_id,
            user_id=current_user.id,
        )

    except ValueError as e:
        raise HTTPException(
            status_code=404,
            detail=str(e),
        )