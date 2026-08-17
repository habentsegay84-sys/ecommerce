from tests.utils.auth import get_auth_headers

from app.models.cart import Cart
from app.models.cart_item import CartItem
from app.models.category import Category
from app.models.product import Product
from app.models.order import Order
from app.models.user import User
from app.models.order_item import OrderItem
from app.models.order_status_history import OrderStatusHistory

def test_checkout_requires_auth(client):
    response = client.post(
        "/orders/checkout",
        json={},
    )

    assert response.status_code == 401


def test_list_orders_requires_auth(client):
    response = client.get("/orders")

    assert response.status_code == 401


def test_get_order_requires_auth(client):
    response = client.get("/orders/1")

    assert response.status_code == 401


def test_track_order_requires_auth(client):
    response = client.get("/orders/1/tracking")

    assert response.status_code == 401


def test_get_nonexistent_order(client):
    headers = get_auth_headers(client)

    response = client.get(
        "/orders/999",
        headers=headers,
    )

    assert response.status_code == 404


def test_track_nonexistent_order(client):
    headers = get_auth_headers(client)

    response = client.get(
        "/orders/999/tracking",
        headers=headers,
    )

    assert response.status_code == 404


def test_checkout_empty_cart(client):
    headers = get_auth_headers(client)

    response = client.post(
        "/orders/checkout",
        headers=headers,
        json={},
    )

    assert response.status_code == 400
    assert response.json()["detail"] == "Cart not found"

def test_successful_checkout(client, db):
    """
    Verify that an authenticated user can successfully
    convert a populated cart into an order.
    """

    headers = get_auth_headers(client)

    category = Category(
        name="Electronics",
    )

    db.add(category)
    db.commit()
    db.refresh(category)

    product = Product(
        name="Test Laptop",
        description="Laptop for checkout testing",
        price=1000.00,
        stock=10,
        category_id=category.id,
    )

    db.add(product)
    db.commit()
    db.refresh(product)

    cart = Cart(
        user_id=1,
    )

    db.add(cart)
    db.commit()
    db.refresh(cart)

    cart_item = CartItem(
        cart_id=cart.id,
        product_id=product.id,
        quantity=2,
    )

    db.add(cart_item)
    db.commit()

    response = client.post(
        "/orders/checkout",
        headers=headers,
        json={},
    )

    assert response.status_code == 200

    data = response.json()

    assert data["message"] == "Order created successfully"
    assert data["total_price"] == 2000.00
    assert data["order_id"] is not None

def test_checkout_updates_stock_and_clears_cart(client, db):
    """
    Verify that a successful checkout decreases product stock
    and removes the purchased items from the user's cart.
    """

    headers = get_auth_headers(client)

    category = Category(
        name="Electronics",
    )

    db.add(category)
    db.commit()
    db.refresh(category)

    product = Product(
        name="Test Laptop",
        description="Laptop for checkout testing",
        price=1000.00,
        stock=10,
        category_id=category.id,
    )

    db.add(product)
    db.commit()
    db.refresh(product)

    cart = Cart(
        user_id=1,
    )

    db.add(cart)
    db.commit()
    db.refresh(cart)

    cart_item = CartItem(
        cart_id=cart.id,
        product_id=product.id,
        quantity=2,
    )

    db.add(cart_item)
    db.commit()

    response = client.post(
        "/orders/checkout",
        headers=headers,
        json={},
    )

    assert response.status_code == 200

    db.refresh(product)

    assert product.stock == 8

    remaining_items = (
        db.query(CartItem)
        .filter(
            CartItem.cart_id == cart.id
        )
        .all()
    )

    assert remaining_items == []

def test_user_cannot_view_another_users_order(client, db):
    """
    Verify that an authenticated user cannot access
    an order belonging to another user.
    """

    headers = get_auth_headers(client)

    another_user = User(
        username="anotheruser",
        email="another@example.com",
        hashed_password="password123",
    )

    db.add(another_user)
    db.commit()
    db.refresh(another_user)

    order = Order(
        user_id=another_user.id,
        total_price=500.00,
        status="pending",
    )

    db.add(order)
    db.commit()
    db.refresh(order)

    response = client.get(
        f"/orders/{order.id}",
        headers=headers,
    )

    assert response.status_code == 404

def test_user_cannot_track_another_users_order(client, db):
    """
    Verify that an authenticated user cannot access
    tracking information for another user's order.
    """

    headers = get_auth_headers(client)

    another_user = User(
        username="anotheruser",
        email="another@example.com",
        hashed_password="password123",
    )

    db.add(another_user)
    db.commit()
    db.refresh(another_user)

    order = Order(
        user_id=another_user.id,
        total_price=500.00,
        status="pending",
    )

    db.add(order)
    db.commit()
    db.refresh(order)

    response = client.get(
        f"/orders/{order.id}/tracking",
        headers=headers,
    )

    assert response.status_code == 404

def test_list_orders_returns_user_orders(client, db):
    """
    Verify that an authenticated user receives their own orders
    with the expected order details.
    """

    headers = get_auth_headers(client)

    order = Order(
        user_id=1,
        total_price=1500.00,
        status="pending",
    )

    db.add(order)
    db.commit()
    db.refresh(order)

    response = client.get(
        "/orders",
        headers=headers,
    )

    assert response.status_code == 200

    data = response.json()

    assert len(data) == 1

    assert data[0]["id"] == order.id
    assert data[0]["total_price"] == 1500.00
    assert data[0]["status"] == "pending"
    assert data[0]["items"] == []

def test_get_order_returns_order_details(client, db):
    """
    Verify that an authenticated user can retrieve
    the details of their own order.
    """

    headers = get_auth_headers(client)

    order = Order(
        user_id=1,
        total_price=750.00,
        status="pending",
    )

    db.add(order)
    db.commit()
    db.refresh(order)

    response = client.get(
        f"/orders/{order.id}",
        headers=headers,
    )

    assert response.status_code == 200

    data = response.json()

    assert data["id"] == order.id
    assert data["total_price"] == 750.00
    assert data["status"] == "pending"
    assert data["items"] == []

def test_get_order_returns_items(client, db):
    """
    Verify that an order response includes its products,
    quantities, prices, and calculated subtotals.
    """

    headers = get_auth_headers(client)

    category = Category(
        name="Electronics",
    )

    db.add(category)
    db.commit()
    db.refresh(category)

    product = Product(
        name="Test Laptop",
        price=1000.00,
        stock=10,
        category_id=category.id,
    )

    db.add(product)
    db.commit()
    db.refresh(product)

    order = Order(
        user_id=1,
        total_price=2000.00,
        status="pending",
    )

    db.add(order)
    db.commit()
    db.refresh(order)

    order_item = OrderItem(
        order_id=order.id,
        product_id=product.id,
        quantity=2,
        price=1000.00,
    )

    db.add(order_item)
    db.commit()

    response = client.get(
        f"/orders/{order.id}",
        headers=headers,
    )

    assert response.status_code == 200

    data = response.json()

    assert data["id"] == order.id
    assert data["total_price"] == 2000.00

    assert len(data["items"]) == 1

    item = data["items"][0]

    assert item["product_id"] == product.id
    assert item["product_name"] == "Test Laptop"
    assert item["quantity"] == 2
    assert item["price"] == 1000.00
    assert item["subtotal"] == 2000.00

def test_track_order_returns_status_history(client, db):
    """
    Verify that an authenticated user can retrieve the current
    order status and its chronological status history.
    """

    headers = get_auth_headers(client)

    order = Order(
        user_id=1,
        total_price=1000.00,
        status="shipped",
    )

    db.add(order)
    db.commit()
    db.refresh(order)

    history_1 = OrderStatusHistory(
    order_id=order.id,
    old_status=None,
    new_status="pending",
    changed_by=1,
    )

    history_2 = OrderStatusHistory(
        order_id=order.id,
        old_status="pending",
        new_status="processing",
        changed_by=1,
    )

    history_3 = OrderStatusHistory(
        order_id=order.id,
        old_status="processing",
        new_status="shipped",
        changed_by=1,
    )

    db.add_all(
        [
            history_1,
            history_2,
            history_3,
        ]
    )

    db.commit()

    response = client.get(
        f"/orders/{order.id}/tracking",
        headers=headers,
    )

    assert response.status_code == 200

    data = response.json()

    assert data["order_id"] == order.id
    assert data["current_status"] == "shipped"

    assert len(data["history"]) == 3

    assert data["history"][0]["old_status"] is None
    assert data["history"][0]["new_status"] == "pending"

    assert data["history"][1]["old_status"] == "pending"
    assert data["history"][1]["new_status"] == "processing"

    assert data["history"][2]["old_status"] == "processing"
    assert data["history"][2]["new_status"] == "shipped"