from tests.utils.auth import get_auth_headers

from app.models.order import Order
from app.models.order_item import OrderItem
from app.models.category import Category
from app.models.product import Product
from app.models.order_status_history import OrderStatusHistory

from tests.utils.auth import (
    get_auth_headers,
    get_admin_auth_headers,
)


def test_list_orders_requires_auth(client):
    """
    Verify that unauthenticated requests cannot access
    administrator order resources.
    """

    response = client.get("/admin/orders")

    assert response.status_code == 401

def test_normal_user_cannot_list_admin_orders(client):
    """
    Verify that a regular authenticated user cannot access
    administrator order resources.
    """

    headers = get_auth_headers(client)

    response = client.get(
        "/admin/orders",
        headers=headers,
    )

    assert response.status_code == 403


def test_normal_user_cannot_update_order_status(client, test_order):
    """
    Verify that a regular user cannot modify an order's status.
    """

    headers = get_auth_headers(client)

    response = client.patch(
        f"/admin/orders/{test_order.id}/status",
        params={
            "status": "processing",
        },
        headers=headers,
    )

    assert response.status_code == 403

def test_admin_can_list_orders(
    client,
    db,
    admin_user,
    test_user,
):
    """
    Verify that an authenticated administrator can retrieve
    customer orders with their associated customer information.
    """

    order = Order(
        user_id=test_user.id,
        total_price=2500.00,
        status="pending",
    )

    db.add(order)
    db.commit()
    db.refresh(order)

    headers = get_admin_auth_headers(
        client,
        db,
    )

    response = client.get(
        "/admin/orders",
        headers=headers,
    )

    assert response.status_code == 200

    data = response.json()

    assert len(data) == 1

    assert data[0]["id"] == order.id
    assert data[0]["customer"] == test_user.username
    assert data[0]["email"] == test_user.email
    assert data[0]["total_price"] == 2500.00
    assert data[0]["status"] == "pending"
    assert data[0]["items"] == []

def test_admin_can_list_order_with_items(
    client,
    db,
    admin_user,
    test_user,
):
    """
    Verify that administrators receive order items
    with the expected product and pricing information.
    """

    category = Category(
        name="Electronics",
    )

    db.add(category)
    db.commit()
    db.refresh(category)

    product = Product(
        name="Test Laptop",
        price=1200.00,
        stock=10,
        category_id=category.id,
    )

    db.add(product)
    db.commit()
    db.refresh(product)

    order = Order(
        user_id=test_user.id,
        total_price=2400.00,
        status="pending",
    )

    db.add(order)
    db.commit()
    db.refresh(order)

    order_item = OrderItem(
        order_id=order.id,
        product_id=product.id,
        quantity=2,
        price=1200.00,
    )

    db.add(order_item)
    db.commit()

    headers = get_admin_auth_headers(
        client,
        db
    )

    response = client.get(
        "/admin/orders",
        headers=headers,
    )

    assert response.status_code == 200

    data = response.json()

    assert len(data) == 1

    assert data[0]["id"] == order.id
    assert len(data[0]["items"]) == 1

    item = data[0]["items"][0]

    assert item["product_name"] == "Test Laptop"
    assert item["quantity"] == 2
    assert item["price"] == 1200.00

def test_admin_can_filter_orders_by_status(
    client,
    db,
    admin_user,
    test_user,
):
    """
    Verify that administrators can filter orders
    by their current status.
    """

    pending_order = Order(
        user_id=test_user.id,
        total_price=1000.00,
        status="pending",
    )

    shipped_order = Order(
        user_id=test_user.id,
        total_price=2000.00,
        status="shipped",
    )

    db.add_all(
        [
            pending_order,
            shipped_order,
        ]
    )

    db.commit()

    headers = get_admin_auth_headers(
        client,
        db
    )

    response = client.get(
        "/admin/orders",
        params={
            "status": "pending",
        },
        headers=headers,
    )

    assert response.status_code == 200

    data = response.json()

    assert len(data) == 1

    assert data[0]["id"] == pending_order.id
    assert data[0]["status"] == "pending"

def test_admin_can_update_order_status(
    client,
    db,
    admin_user,
    test_order,
):
    """
    Verify that an administrator can update an order's status
    and that the corresponding status history is recorded.
    """

    headers = get_admin_auth_headers(
        client,
        db,
    )

    response = client.patch(
        f"/admin/orders/{test_order.id}/status",
        params={
            "status": "processing",
        },
        headers=headers,
    )

    assert response.status_code == 200

    data = response.json()

    assert data["message"] == "Order status updated"
    assert data["order_id"] == test_order.id
    assert data["status"] == "processing"

    db.refresh(test_order)

    assert test_order.status == "processing"

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

def test_admin_cannot_use_invalid_order_status(
    client,
    db,
    admin_user,
    test_order,
):
    """
    Verify that administrators cannot assign an unsupported
    status to an order.
    """

    headers = get_admin_auth_headers(
        client,
        db,
    )

    response = client.patch(
        f"/admin/orders/{test_order.id}/status",
        params={
            "status": "invalid_status",
        },
        headers=headers,
    )

    assert response.status_code == 400

    data = response.json()

    assert data["detail"] == "Invalid order status"

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

def test_admin_cannot_update_nonexistent_order(
    client,
    db,
    admin_user,
):
    """
    Verify that updating a nonexistent order returns
    a not-found response.
    """

    headers = get_admin_auth_headers(
        client,
        db,
    )

    response = client.patch(
        "/admin/orders/999999/status",
        params={
            "status": "processing",
        },
        headers=headers,
    )

    assert response.status_code == 404

    data = response.json()

    assert data["detail"] == "Order not found"