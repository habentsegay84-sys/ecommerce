from tests.utils.auth import get_auth_headers

from app.models.category import Category
from app.models.product import Product
from app.models.cart import Cart
from app.models.cart_item import CartItem


def test_add_to_cart_requires_auth(client):
    """
    Verify that unauthenticated users cannot add products to a cart.
    """

    response = client.post(
        "/cart/add",
        json={
            "product_id": 1,
            "quantity": 1,
        },
    )

    assert response.status_code == 401


def test_get_cart_requires_auth(client):
    """
    Verify that unauthenticated users cannot access a cart.
    """

    response = client.get("/cart")

    assert response.status_code == 401


def test_update_cart_item_requires_auth(client):
    """
    Verify that unauthenticated users cannot modify cart items.
    """

    response = client.patch(
        "/cart/items/1",
        json={
            "quantity": 2,
        },
    )

    assert response.status_code == 401


def test_remove_cart_item_requires_auth(client):
    """
    Verify that unauthenticated users cannot remove cart items.
    """

    response = client.delete(
        "/cart/items/1",
    )

    assert response.status_code == 401


def test_clear_cart_requires_auth(client):
    """
    Verify that unauthenticated users cannot clear a cart.
    """

    response = client.delete("/cart")

    assert response.status_code == 401

def test_add_to_cart_product_not_found(
    client,
    test_user,
):
    """
    Verify that adding a non-existent product returns a not-found error.
    """

    headers = get_auth_headers(client)

    response = client.post(
        "/cart/add",
        json={
            "product_id": 9999,
            "quantity": 1,
        },
        headers=headers,
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Product not found"

def test_add_to_cart_creates_cart(
    client,
    db,
    test_user,
):
    """
    Verify that adding a product creates a cart and
    adds the requested product quantity.
    """

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

    headers = get_auth_headers(client)

    response = client.post(
        "/cart/add",
        json={
            "product_id": product.id,
            "quantity": 2,
        },
        headers=headers,
    )

    assert response.status_code == 200

    data = response.json()

    assert data["message"] == "Product added to cart"

    cart = (
        db.query(Cart)
        .filter(Cart.user_id == test_user.id)
        .first()
    )

    assert cart is not None

    cart_item = (
        db.query(CartItem)
        .filter(
            CartItem.cart_id == cart.id,
            CartItem.product_id == product.id,
        )
        .first()
    )

    assert cart_item is not None
    assert cart_item.quantity == 2

def test_add_existing_product_to_cart_increases_quantity(
    client,
    db,
    test_user,
):
    """
    Verify that adding an existing cart product increases
    its quantity instead of creating a duplicate cart item.
    """

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

    headers = get_auth_headers(client)

    first_response = client.post(
        "/cart/add",
        json={
            "product_id": product.id,
            "quantity": 2,
        },
        headers=headers,
    )

    assert first_response.status_code == 200

    second_response = client.post(
        "/cart/add",
        json={
            "product_id": product.id,
            "quantity": 3,
        },
        headers=headers,
    )

    assert second_response.status_code == 200

    cart = (
        db.query(Cart)
        .filter(Cart.user_id == test_user.id)
        .first()
    )

    assert cart is not None

    cart_items = (
        db.query(CartItem)
        .filter(
            CartItem.cart_id == cart.id,
            CartItem.product_id == product.id,
        )
        .all()
    )

    assert len(cart_items) == 1
    assert cart_items[0].quantity == 5

def test_get_cart_returns_items_and_total(
    client,
    db,
    test_user,
):
    """
    Verify that the cart endpoint returns the user's items,
    calculated subtotals, and the correct cart total.
    """

    category = Category(
        name="Electronics",
    )

    db.add(category)
    db.commit()
    db.refresh(category)

    laptop = Product(
        name="Laptop",
        price=1000.00,
        stock=10,
        category_id=category.id,
    )

    mouse = Product(
        name="Mouse",
        price=50.00,
        stock=20,
        category_id=category.id,
    )

    db.add_all([laptop, mouse])
    db.commit()

    db.refresh(laptop)
    db.refresh(mouse)

    cart = Cart(
        user_id=test_user.id,
    )

    db.add(cart)
    db.commit()
    db.refresh(cart)

    db.add_all(
        [
            CartItem(
                cart_id=cart.id,
                product_id=laptop.id,
                quantity=2,
            ),
            CartItem(
                cart_id=cart.id,
                product_id=mouse.id,
                quantity=3,
            ),
        ]
    )

    db.commit()

    headers = get_auth_headers(client)

    response = client.get(
        "/cart",
        headers=headers,
    )

    assert response.status_code == 200

    data = response.json()

    assert len(data["items"]) == 2

    assert data["total"] == 2150.00

    laptop_item = next(
        item
        for item in data["items"]
        if item["product_id"] == laptop.id
    )

    mouse_item = next(
        item
        for item in data["items"]
        if item["product_id"] == mouse.id
    )

    assert laptop_item["product_name"] == "Laptop"
    assert laptop_item["price"] == 1000.00
    assert laptop_item["quantity"] == 2
    assert laptop_item["subtotal"] == 2000.00

    assert mouse_item["product_name"] == "Mouse"
    assert mouse_item["price"] == 50.00
    assert mouse_item["quantity"] == 3
    assert mouse_item["subtotal"] == 150.00

def test_get_empty_cart(
    client,
    test_user,
):
    """
    Verify that a user without a cart receives an empty cart
    with a zero total.
    """

    headers = get_auth_headers(client)

    response = client.get(
        "/cart",
        headers=headers,
    )

    assert response.status_code == 200

    data = response.json()

    assert data["items"] == []
    assert data["total"] == 0

def test_update_cart_item_successfully(
    client,
    db,
    test_user,
):
    """
    Verify that an authenticated user can update the quantity
    of an existing product in their cart.
    """

    category = Category(
        name="Electronics",
    )

    db.add(category)
    db.commit()
    db.refresh(category)

    product = Product(
        name="Laptop",
        price=1000.00,
        stock=10,
        category_id=category.id,
    )

    db.add(product)
    db.commit()
    db.refresh(product)

    cart = Cart(
        user_id=test_user.id,
    )

    db.add(cart)
    db.commit()
    db.refresh(cart)

    cart_item = CartItem(
        cart_id=cart.id,
        product_id=product.id,
        quantity=1,
    )

    db.add(cart_item)
    db.commit()

    headers = get_auth_headers(client)

    response = client.patch(
        f"/cart/items/{product.id}",
        json={
            "quantity": 5,
        },
        headers=headers,
    )

    assert response.status_code == 200

    data = response.json()

    assert data["message"] == "Cart updated successfully"
    assert data["product_id"] == product.id
    assert data["quantity"] == 5

    db.refresh(cart_item)

    assert cart_item.quantity == 5

def test_update_cart_item_rejects_zero_quantity(
    client,
    db,
    test_user,
):
    """
    Verify that a cart item's quantity cannot be set to zero.
    """

    headers = get_auth_headers(client)

    response = client.patch(
        "/cart/items/1",
        json={
            "quantity": 0,
        },
        headers=headers,
    )

    assert response.status_code == 400

    assert response.json()["detail"] == (
        "Quantity must be at least 1"
    )

def test_update_cart_item_rejects_negative_quantity(
    client,
    test_user,
):
    """
    Verify that a cart item's quantity cannot be negative.
    """

    headers = get_auth_headers(client)

    response = client.patch(
        "/cart/items/1",
        json={
            "quantity": -2,
        },
        headers=headers,
    )

    assert response.status_code == 400

    assert response.json()["detail"] == (
        "Quantity must be at least 1"
    )

def test_remove_cart_item_successfully(
    client,
    db,
    test_user,
):
    """
    Verify that an authenticated user can remove a product
    from their cart.
    """

    category = Category(
        name="Electronics",
    )

    db.add(category)
    db.commit()
    db.refresh(category)

    product = Product(
        name="Laptop",
        price=1000.00,
        stock=10,
        category_id=category.id,
    )

    db.add(product)
    db.commit()
    db.refresh(product)

    cart = Cart(
        user_id=test_user.id,
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
    db.refresh(cart_item)

    headers = get_auth_headers(client)

    response = client.delete(
        f"/cart/items/{product.id}",
        headers=headers,
    )

    assert response.status_code == 200

    assert response.json() == {
        "message": "Product removed from cart"
    }

    remaining_item = (
        db.query(CartItem)
        .filter(
            CartItem.id == cart_item.id
        )
        .first()
    )

    assert remaining_item is None

def test_remove_cart_item_not_found(
    client,
    db,
    test_user,
):
    """
    Verify that removing a product that is not in the user's
    cart returns a not-found response.
    """

    cart = Cart(
        user_id=test_user.id,
    )

    db.add(cart)
    db.commit()

    headers = get_auth_headers(client)

    response = client.delete(
        "/cart/items/999",
        headers=headers,
    )

    assert response.status_code == 404

    assert response.json()["detail"] == (
        "Product not found in cart"
    )

def test_clear_cart_successfully(
    client,
    db,
    test_user,
):
    """
    Verify that an authenticated user can remove all
    products from their cart.
    """

    category = Category(
        name="Electronics",
    )

    db.add(category)
    db.commit()
    db.refresh(category)

    product = Product(
        name="Laptop",
        price=1000.00,
        stock=10,
        category_id=category.id,
    )

    db.add(product)
    db.commit()
    db.refresh(product)

    cart = Cart(
        user_id=test_user.id,
    )

    db.add(cart)
    db.commit()
    db.refresh(cart)

    cart_items = [
        CartItem(
            cart_id=cart.id,
            product_id=product.id,
            quantity=2,
        ),
    ]

    db.add_all(cart_items)
    db.commit()

    headers = get_auth_headers(client)

    response = client.delete(
        "/cart",
        headers=headers,
    )

    assert response.status_code == 200

    assert response.json() == {
        "message": "Cart cleared successfully"
    }

    remaining_items = (
        db.query(CartItem)
        .filter(
            CartItem.cart_id == cart.id
        )
        .all()
    )

    assert remaining_items == []

def test_clear_cart_not_found(
    client,
):
    """
    Verify that clearing a cart that does not exist
    returns a not-found response.
    """

    headers = get_auth_headers(client)

    response = client.delete(
        "/cart",
        headers=headers,
    )

    assert response.status_code == 404

    assert response.json()["detail"] == (
        "Cart not found"
    )