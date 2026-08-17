from sqlalchemy.orm import Session

from app.models.order import Order
from app.models.order_status_history import OrderStatusHistory
from app.models.order_item import OrderItem
from app.repositories.order_repository import OrderRepository


ALLOWED_ORDER_STATUSES = {
    "pending",
    "processing",
    "shipped",
    "delivered",
    "cancelled",
}


def list_all_orders_service(
    db: Session,
    status: str | None = None,
):
    """
    Retrieve all customer orders for administrator access.

    Optionally filters orders by their current status.
    """

    repository = OrderRepository(db)

    orders = repository.list_all(
        status=status,
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


def update_order_status_service(
    db: Session,
    order_id: int,
    status: str,
    admin_id: int,
):
    """
    Update an order's status and record the change
    in the order status history.
    """

    if status not in ALLOWED_ORDER_STATUSES:
        raise ValueError(
            "Invalid order status"
        )

    repository = OrderRepository(db)

    order = repository.get_by_id(
        order_id,
    )

    if order is None:
        raise LookupError(
            "Order not found"
        )

    old_status = order.status

    order.status = status

    history = OrderStatusHistory(
        order_id=order.id,
        old_status=old_status,
        new_status=status,
        changed_by=admin_id,
    )

    db.add(history)
    db.commit()
    db.refresh(order)

    return order