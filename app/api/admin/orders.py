from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.auth.admin import get_current_admin

from app.models.user import User
from app.services.admin_order_service import (
    list_all_orders_service,
    update_order_status_service,
)
from app.schemas.admin_order import AdminOrderResponse


router = APIRouter(
    prefix="/admin/orders",
    tags=["Admin Orders"],
)


@router.get(
    "",
    response_model=list[AdminOrderResponse],
)
def list_all_orders(
    status: str | None = Query(default=None),
    current_admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db),
):
    """
    Retrieve customer orders for an authenticated administrator.
    """

    return list_all_orders_service(
        db=db,
        status=status,
    )


@router.patch("/{order_id}/status")
def update_order_status(
    order_id: int,
    status: str,
    current_admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db),
):
    """
    Update an order's status and record the change
    in the order status history.
    """

    try:
        order = update_order_status_service(
            db=db,
            order_id=order_id,
            status=status,
            admin_id=current_admin.id,
        )

        return {
            "message": "Order status updated",
            "order_id": order.id,
            "status": order.status,
        }

    except ValueError as e:
        raise HTTPException(
            status_code=400,
            detail=str(e),
        )

    except LookupError as e:
        raise HTTPException(
            status_code=404,
            detail=str(e),
        )