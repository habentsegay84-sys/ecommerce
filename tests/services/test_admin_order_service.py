import pytest

from app.models.order_status_history import OrderStatusHistory
from app.services.admin_order_service import (
    list_all_orders_service,
    update_order_status_service,
)
from app.models.order import Order


def test_list_all_orders_service(
    db,
    test_order,
):
    """
    Verify that the admin order service retrieves
    orders from the database.
    """

    orders = list_all_orders_service(
        db=db,
    )

    assert len(orders) == 1

    assert orders[0]["id"] == test_order.id
    assert orders[0]["total_price"] == 100
    assert orders[0]["status"] == "pending"
    assert orders[0]["items"] == []


def test_list_all_orders_service_filters_by_status(
    db,
    test_user,
):
    """
    Verify that the admin order service correctly
    filters orders by their current status.
    """

    pending_order = test_order = None

    pending_order = Order(
        user_id=test_user.id,
        total_price=100,
        status="pending",
    )

    shipped_order = Order(
        user_id=test_user.id,
        total_price=200,
        status="shipped",
    )

    db.add_all(
        [
            pending_order,
            shipped_order,
        ]
    )

    db.commit()

    orders = list_all_orders_service(
        db=db,
        status="shipped",
    )

    assert len(orders) == 1
    assert orders[0]["id"] == shipped_order.id
    assert orders[0]["status"] == "shipped"


def test_update_order_status_service(
    db,
    test_order,
    admin_user,
):
    """
    Verify that an administrator can update an order's
    status and that the status change is recorded.
    """

    updated_order = update_order_status_service(
        db=db,
        order_id=test_order.id,
        status="processing",
        admin_id=admin_user.id,
    )

    assert updated_order.id == test_order.id
    assert updated_order.status == "processing"

    history = (
        db.query(OrderStatusHistory)
        .filter(
            OrderStatusHistory.order_id == test_order.id
        )
        .first()
    )

    assert history is not None
    assert history.old_status == "pending"
    assert history.new_status == "processing"
    assert history.changed_by == admin_user.id


def test_update_order_status_service_rejects_invalid_status(
    db,
    test_order,
    admin_user,
):
    """
    Verify that unsupported order statuses are rejected
    before modifying the order.
    """

    with pytest.raises(
        ValueError,
        match="Invalid order status",
    ):
        update_order_status_service(
            db=db,
            order_id=test_order.id,
            status="invalid_status",
            admin_id=admin_user.id,
        )

    db.refresh(test_order)

    assert test_order.status == "pending"

    history = (
        db.query(OrderStatusHistory)
        .filter(
            OrderStatusHistory.order_id == test_order.id
        )
        .first()
    )

    assert history is None


def test_update_order_status_service_rejects_missing_order(
    db,
    admin_user,
):
    """
    Verify that attempting to update a nonexistent order
    raises a not-found error.
    """

    with pytest.raises(
        LookupError,
        match="Order not found",
    ):
        update_order_status_service(
            db=db,
            order_id=999999,
            status="processing",
            admin_id=admin_user.id,
        )