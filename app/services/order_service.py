from sqlalchemy.orm import Session
from datetime import datetime, timezone

from app.models.cart import Cart
from app.models.cart_item import CartItem
from app.models.coupon import Coupon
from app.models.order import Order
from app.models.order_item import OrderItem
from app.models.inventory import InventoryLog
from app.repositories.inventory_repository import InventoryRepository
from app.repositories.product_repository import ProductRepository
from app.repositories.order_repository import OrderRepository
from app.repositories.cart_repository import CartRepository
from app.repositories.coupon_repository import CouponRepository

from app.schemas.checkout import CheckoutRequest

from app.schemas.order import (
    OrderResponse,
    OrderItemResponse,
)
from app.schemas.order_tracking import (
    OrderTrackingResponse,
    OrderTrackingHistoryResponse,
)

def list_orders_service(
    db: Session,
    user_id: int,
):
    """
    Return all orders for a user.
    """

    repository = OrderRepository(db)

    orders = repository.list_by_user(user_id)

    response = []

    for order in orders:

        items = []

        for item in order.items:

            items.append(
                OrderItemResponse(
                    product_id=item.product.id,
                    product_name=item.product.name,
                    quantity=item.quantity,
                    price=item.price,
                    subtotal=item.price * item.quantity,
                )
            )

        response.append(
            OrderResponse(
                id=order.id,
                total_price=order.total_price,
                status=order.status,
                created_at=order.created_at,
                items=items,
            )
        )

    return response

def get_order_service(
    db: Session,
    order_id: int,
    user_id: int,
):
    """
    Retrieve one order belonging to a user.
    """

    repository = OrderRepository(db)

    order = repository.get_user_order(
        order_id=order_id,
        user_id=user_id,
    )

    if order is None:
        raise ValueError(
            "Order not found"
        )

    items = []

    for item in order.items:

        items.append(
            OrderItemResponse(
                product_id=item.product.id,
                product_name=item.product.name,
                quantity=item.quantity,
                price=item.price,
                subtotal=item.price * item.quantity,
            )
        )

    return OrderResponse(
        id=order.id,
        total_price=order.total_price,
        status=order.status,
        created_at=order.created_at,
        items=items,
    )

def track_order_service(
    db: Session,
    order_id: int,
    user_id: int,
):
    """
    Return tracking information for an order.
    """

    repository = OrderRepository(db)

    order = repository.get_user_order(
        order_id=order_id,
        user_id=user_id,
    )

    if order is None:
        raise ValueError(
            "Order not found"
        )

    history = repository.get_tracking_history(
        order.id,
    )

    return OrderTrackingResponse(
        order_id=order.id,
        current_status=order.status,
        history=[
            OrderTrackingHistoryResponse(
                old_status=item.old_status,
                new_status=item.new_status,
                created_at=item.created_at,
            )
            for item in history
        ],
    )

def checkout_service(
    db: Session,
    user_id: int,
    checkout_data: CheckoutRequest,
):
    """
    Create an order from the user's cart.
    """

    repository = OrderRepository(db)
    product_repository = ProductRepository(db)
    inventory_repository = InventoryRepository(db)
    cart_repository = CartRepository(db)
    coupon_repository = CouponRepository(db)

    cart = cart_repository.get_by_user_id(user_id)

    if cart is None:
        raise ValueError(
            "Cart not found"
        )

    if not cart.items:
        raise ValueError(
            "Cart is empty"
        )

    coupon = None

    # Find coupon only when one was provided.
    if checkout_data.coupon_code:

        coupon = coupon_repository.get_active_coupon(
            checkout_data.coupon_code
        )

        if coupon is None:
            raise ValueError(
                "Coupon not found"
            )

        if coupon.expires_at:

            expires_at = coupon.expires_at

            if expires_at.tzinfo is None:
                expires_at = expires_at.replace(
                    tzinfo=timezone.utc
                )

            if expires_at < datetime.now(timezone.utc):
                raise ValueError(
                    "Coupon expired"
                )

    # Calculate cart total.
    total_price = 0

    for item in cart.items:

        total_price += (
            item.product.price
            * item.quantity
        )

    # Apply coupon discount.
    if coupon:
        total_price = total_price * (
            1 - coupon.discount_percent / 100
        )

    order = Order(
        user_id=user_id,
        total_price=total_price,
        status="pending",
        coupon_id=(
            coupon.id
            if coupon
            else None
        ),
    )

    try:
        repository.create(order)

        for item in cart.items:

            order_item = OrderItem(
                order_id=order.id,
                product_id=item.product_id,
                quantity=item.quantity,
                price=item.product.price,
            )

            repository.create_order_item(order_item)

            stock_change = product_repository.decrease_stock(
                product_id=item.product_id,
                quantity=item.quantity,
            )

            if stock_change is None:
                raise ValueError(
                    f"Not enough stock for {item.product.name}"
                )

            old_stock, new_stock = stock_change

            log = InventoryLog(
                product_id=item.product_id,
                old_stock=old_stock,
                new_stock=new_stock,
                change_type="sale",
                changed_by=user_id,
            )

            inventory_repository.create_log(log)

        cart_repository.clear_items(cart.id)

        db.commit()

        return order

    except Exception:
        db.rollback()
        raise