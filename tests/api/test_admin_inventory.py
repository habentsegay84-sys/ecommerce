from app.models.product import Product
from app.models.category import Category
from app.models.inventory import InventoryLog
from app.models.cart import Cart
from app.models.cart_item import CartItem

from tests.utils.auth import (
    get_auth_headers,
    get_admin_auth_headers,
)

from app.schemas.checkout import CheckoutRequest
from app.services.order_service import checkout_service

def create_product(db):
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

    return product


def test_update_stock_requires_auth(
    client,
    db,
):
    product = create_product(db)

    response = client.patch(
        f"/admin/inventory/{product.id}/stock",
        params={
            "stock": 20,
        },
    )

    assert response.status_code == 401


def test_normal_user_cannot_update_stock(
    client,
    db,
):
    product = create_product(db)

    headers = get_auth_headers(client)

    response = client.patch(
        f"/admin/inventory/{product.id}/stock",
        params={
            "stock": 20,
        },
        headers=headers,
    )

    assert response.status_code == 403


def test_admin_can_update_stock(
    client,
    db,
    admin_user,
):
    product = create_product(db)

    headers = get_admin_auth_headers(
        client,
        db,
    )

    response = client.patch(
        f"/admin/inventory/{product.id}/stock",
        params={
            "stock": 20,
        },
        headers=headers,
    )

    assert response.status_code == 200

    data = response.json()

    assert data["message"] == "Stock updated successfully"
    assert data["product_id"] == product.id
    assert data["new_stock"] == 20

    db.refresh(product)

    assert product.stock == 20


def test_update_stock_creates_inventory_log(
    client,
    db,
    admin_user,
):
    product = create_product(db)

    headers = get_admin_auth_headers(
        client,
        db,
    )

    response = client.patch(
        f"/admin/inventory/{product.id}/stock",
        params={
            "stock": 25,
        },
        headers=headers,
    )

    assert response.status_code == 200

    log = (
        db.query(InventoryLog)
        .filter(
            InventoryLog.product_id == product.id
        )
        .first()
    )

    assert log is not None
    assert log.old_stock == 10
    assert log.new_stock == 25
    assert log.change_type == "admin_update"
    assert log.changed_by == admin_user.id


def test_update_stock_rejects_negative_stock(
    client,
    db,
    admin_user,
):
    product = create_product(db)

    headers = get_admin_auth_headers(
        client,
        db,
    )

    response = client.patch(
        f"/admin/inventory/{product.id}/stock",
        params={
            "stock": -1,
        },
        headers=headers,
    )

    assert response.status_code == 400
    assert response.json()["detail"] == "Stock cannot be negative"


def test_update_stock_rejects_same_stock(
    client,
    db,
    admin_user,
):
    product = create_product(db)

    headers = get_admin_auth_headers(
        client,
        db,
    )

    response = client.patch(
        f"/admin/inventory/{product.id}/stock",
        params={
            "stock": 10,
        },
        headers=headers,
    )

    assert response.status_code == 400
    assert response.json()["detail"] == (
        "Stock is already this value"
    )


def test_update_stock_returns_404_for_missing_product(
    client,
    db,
    admin_user,
):
    headers = get_admin_auth_headers(
        client,
        db,
    )

    response = client.patch(
        "/admin/inventory/9999/stock",
        params={
            "stock": 20,
        },
        headers=headers,
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Product not found"


def test_inventory_logs_requires_auth(
    client,
):
    response = client.get(
        "/admin/inventory/logs"
    )

    assert response.status_code == 401


def test_normal_user_cannot_view_inventory_logs(
    client,
):
    headers = get_auth_headers(client)

    response = client.get(
        "/admin/inventory/logs",
        headers=headers,
    )

    assert response.status_code == 403


def test_admin_can_view_inventory_logs(
    client,
    db,
    admin_user,
):
    product = create_product(db)

    headers = get_admin_auth_headers(
        client,
        db,
    )

    client.patch(
        f"/admin/inventory/{product.id}/stock",
        params={
            "stock": 30,
        },
        headers=headers,
    )

    response = client.get(
        "/admin/inventory/logs",
        headers=headers,
    )

    assert response.status_code == 200

    data = response.json()

    assert len(data) == 1

    log = data[0]

    assert log["product_id"] == product.id
    assert log["product_name"] == "Test Laptop"
    assert log["old_stock"] == 10
    assert log["new_stock"] == 30
    assert log["change_type"] == "admin_update"
    assert log["changed_by"] == admin_user.id

def test_admin_can_view_sale_inventory_log(
    client,
    db,
    test_user,
    admin_user,
):
    product = create_product(db)

    # Add the product to the user's cart.

    cart = Cart(user_id=test_user.id)
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

    # User checks out.

    checkout_service(
        db=db,
        user_id=test_user.id,
        checkout_data=CheckoutRequest(),
    )

    # Admin views inventory logs.
    headers = get_admin_auth_headers(
        client,
        db,
    )

    response = client.get(
        "/admin/inventory/logs",
        headers=headers,
    )

    assert response.status_code == 200

    data = response.json()

    assert len(data) == 1

    log = data[0]

    assert log["product_id"] == product.id
    assert log["product_name"] == "Test Laptop"
    assert log["old_stock"] == 10
    assert log["new_stock"] == 8
    assert log["change_type"] == "sale"
    assert log["changed_by"] == test_user.id