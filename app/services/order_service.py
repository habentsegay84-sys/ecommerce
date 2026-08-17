from sqlalchemy.orm import Session
from datetime import datetime, timezone

from app.models.cart import Cart
from app.models.cart_item import CartItem
from app.models.coupon import Coupon
from app.models.order import Order
from app.models.order_item import OrderItem

from app.schemas.checkout import CheckoutRequest

from app.repositories.order_repository import OrderRepository
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

    cart = (
        db.query(Cart)
        .filter(Cart.user_id == user_id)
        .first()
    )

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

        coupon = (
            db.query(Coupon)
            .filter(
                Coupon.code == checkout_data.coupon_code,
                Coupon.active == True,
            )
            .first()
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

        if item.quantity > item.product.stock:
            raise ValueError(
                f"Not enough stock for {item.product.name}"
            )

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

            db.add(order_item)

            item.product.stock -= item.quantity

        (
            db.query(CartItem)
            .filter(
                CartItem.cart_id == cart.id
            )
            .delete()
        )

        db.commit()
        db.refresh(order)

        return order

    except Exception:
        db.rollback()
        raise