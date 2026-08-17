import pytest

from datetime import datetime, timedelta, timezone

from app.models.cart import Cart
from app.models.cart_item import CartItem
from app.models.category import Category
from app.models.coupon import Coupon
from app.models.order import Order
from app.models.order_item import OrderItem
from app.models.product import Product
from app.schemas.checkout import CheckoutRequest
from app.services.order_service import checkout_service


def test_checkout_cart_not_found(db):

    checkout_data = CheckoutRequest()

    with pytest.raises(
        ValueError,
        match="Cart not found",
    ):
        checkout_service(
            db=db,
            user_id=999,
            checkout_data=checkout_data,
        )

def test_checkout_empty_cart(db):
    """
    Checkout should fail when the user's cart is empty.
    """

    cart = Cart(
        user_id=999,
    )

    db.add(cart)
    db.commit()
    db.refresh(cart)

    checkout_data = CheckoutRequest()

    with pytest.raises(
        ValueError,
        match="Cart is empty",
    ):
        checkout_service(
            db=db,
            user_id=999,
            checkout_data=checkout_data,
        )

def test_successful_checkout(db, test_user):
    """
    A user should be able to checkout
    when their cart contains an available product.
    """

    # Create category
    category = Category(
        name="Electronics",
    )

    db.add(category)
    db.commit()
    db.refresh(category)

    # Create product
    product = Product(
        name="Test Laptop",
        description="Laptop for testing",
        price=1000.00,
        stock=10,
        category_id=category.id,
    )

    db.add(product)
    db.commit()
    db.refresh(product)

    # Create cart
    cart = Cart(
        user_id=test_user.id,
    )

    db.add(cart)
    db.commit()
    db.refresh(cart)

    # Add product to cart
    cart_item = CartItem(
        cart_id=cart.id,
        product_id=product.id,
        quantity=2,
    )

    db.add(cart_item)
    db.commit()

    checkout_data = CheckoutRequest()

    # Perform checkout
    order = checkout_service(
        db=db,
        user_id=test_user.id,
        checkout_data=checkout_data,
    )

    # Verify order
    assert order is not None
    assert order.user_id == test_user.id
    assert order.total_price == 2000.00
    assert order.status == "pending"

    # Verify order item
    assert len(order.items) == 1

    order_item = order.items[0]

    assert order_item.product_id == product.id
    assert order_item.quantity == 2
    assert order_item.price == 1000.00

    # Verify stock was reduced
    db.refresh(product)

    assert product.stock == 8

    # Verify cart was cleared
    db.refresh(cart)

    assert len(cart.items) == 0

def test_checkout_insufficient_stock(db, test_user):
    """
    Checkout should fail when the requested quantity
    exceeds the available product stock.
    """

    category = Category(
        name="Electronics",
    )

    db.add(category)
    db.commit()
    db.refresh(category)

    product = Product(
        name="Limited Laptop",
        description="Product with limited stock",
        price=1000.00,
        stock=2,
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
        quantity=5,
    )

    db.add(cart_item)
    db.commit()

    checkout_data = CheckoutRequest()

    with pytest.raises(
        ValueError,
        match=f"Not enough stock for {product.name}",
    ):
        checkout_service(
            db=db,
            user_id=test_user.id,
            checkout_data=checkout_data,
        )

    # Stock must not be reduced after the failed checkout.
    db.refresh(product)

    assert product.stock == 2

def test_checkout_with_valid_coupon(db, test_user):
    """
    A valid active coupon should reduce the order total.
    """

    category = Category(
        name="Electronics",
    )

    db.add(category)
    db.commit()
    db.refresh(category)

    product = Product(
        name="Test Laptop",
        description="Laptop for coupon testing",
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

    coupon = Coupon(
        code="SAVE20",
        discount_percent=20,
        active=True,
        expires_at=None,
    )

    db.add(coupon)
    db.commit()
    db.refresh(coupon)

    checkout_data = CheckoutRequest(
        coupon_code="SAVE20",
    )

    order = checkout_service(
        db=db,
        user_id=test_user.id,
        checkout_data=checkout_data,
    )

    # Original total:
    # 1000 * 2 = 2000
    #
    # 20% discount:
    # 2000 * 0.80 = 1600

    assert order.total_price == 1600.00

    assert order.coupon_id == coupon.id

def test_checkout_with_invalid_coupon(db, test_user):
    """
    Checkout should fail when the coupon does not exist.
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

    checkout_data = CheckoutRequest(
        coupon_code="DOES_NOT_EXIST",
    )

    with pytest.raises(
        ValueError,
        match="Coupon not found",
    ):
        checkout_service(
            db=db,
            user_id=test_user.id,
            checkout_data=checkout_data,
        )

def test_checkout_with_expired_coupon(db, test_user):
    """
    Checkout should fail when the coupon has expired.
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

    expired_coupon = Coupon(
        code="EXPIRED20",
        discount_percent=20,
        active=True,
        expires_at=datetime.now(timezone.utc) - timedelta(days=1),
    )

    db.add(expired_coupon)
    db.commit()

    checkout_data = CheckoutRequest(
        coupon_code="EXPIRED20",
    )

    with pytest.raises(
        ValueError,
        match="Coupon expired",
    ):
        checkout_service(
            db=db,
            user_id=test_user.id,
            checkout_data=checkout_data,
        )

def test_checkout_rolls_back_when_order_item_creation_fails(
    db,
    test_user,
    monkeypatch,
):
    """
    Checkout should rollback the entire transaction
    if creating an order item fails.
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

    checkout_data = CheckoutRequest()

    original_add = db.add

    def failing_add(obj):
        if isinstance(obj, OrderItem):
            raise RuntimeError("Simulated database failure")

        return original_add(obj)

    monkeypatch.setattr(db, "add", failing_add)

    with pytest.raises(
        RuntimeError,
        match="Simulated database failure",
    ):
        checkout_service(
            db=db,
            user_id=test_user.id,
            checkout_data=checkout_data,
        )

    # The order must not exist.
    orders = (
        db.query(Order)
        .filter(Order.user_id == test_user.id)
        .all()
    )

    assert orders == []

    # Stock must remain unchanged.
    db.refresh(product)

    assert product.stock == 10

    # Cart item must remain.
    remaining_cart_items = (
        db.query(CartItem)
        .filter(CartItem.cart_id == cart.id)
        .all()
    )

    assert len(remaining_cart_items) == 1
    assert remaining_cart_items[0].quantity == 2