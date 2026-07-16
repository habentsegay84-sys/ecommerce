from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session, joinedload

from app.database.session import get_db
from app.auth.dependencies import get_current_admin

from app.models.user import User
from app.models.order import Order
from app.models.order_status_history import OrderStatusHistory

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

    query = (
        db.query(Order)
        .options(
            joinedload(Order.user),
            joinedload(Order.items)
        )
    )


    if status:
        query = query.filter(
            Order.status == status
        )


    orders = (
        query
        .order_by(Order.created_at.desc())
        .all()
    )


    response = []

    for order in orders:

        items = []

        for item in order.items:

            items.append(
                {
                    "product_name": item.product.name,
                    "quantity": item.quantity,
                    "price": item.price,
                }
            )


        response.append(
            {
                "id": order.id,
                "customer": order.user.username,
                "email": order.user.email,
                "total_price": order.total_price,
                "status": order.status,
                "created_at": order.created_at,
                "items": items,
            }
        )


    return response

@router.patch("/{order_id}/status")
def update_order_status(
    order_id: int,
    status: str,
    current_admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db),
):

    order = (
        db.query(Order)
        .filter(Order.id == order_id)
        .first()
    )


    if order is None:
        raise HTTPException(
            status_code=404,
            detail="Order not found",
        )


    allowed_status = [
        "pending",
        "processing",
        "shipped",
        "delivered",
        "cancelled",
    ]


    if status not in allowed_status:
        raise HTTPException(
            status_code=400,
            detail="Invalid order status",
        )


    old_status = order.status

    order.status = status


    history = OrderStatusHistory(
        order_id=order.id,
        old_status=old_status,
        new_status=status,
        changed_by=current_admin.id,
    )

    db.add(history)

    db.commit()
    db.refresh(order)


    return {
        "message": "Order status updated",
        "order_id": order.id,
        "status": order.status,
    }