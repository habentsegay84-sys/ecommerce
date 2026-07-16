from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.auth.dependencies import get_current_user

from app.models.user import User
from app.models.cart import Cart
from app.models.cart_item import CartItem
from app.models.order import Order
from app.models.order_item import OrderItem
from app.schemas.order import (
    OrderResponse,
    OrderItemResponse,
)
from app.models.order_status_history import OrderStatusHistory
from app.schemas.order_tracking import (
    OrderTrackingResponse,
    OrderTrackingHistoryResponse,
)

router = APIRouter(
    prefix="/orders",
    tags=["Orders"],
)


@router.post("/checkout")
def checkout(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    try:
        # Find the user's cart
        cart = (
            db.query(Cart)
            .filter(Cart.user_id == current_user.id)
            .first()
        )

        if not cart:
            raise HTTPException(
                status_code=404,
                detail="Cart not found",
            )

        if not cart.items:
            raise HTTPException(
                status_code=400,
                detail="Cart is empty",
            )

        # Calculate total and validate stock
        total_price = 0

        for item in cart.items:

            if item.quantity > item.product.stock:
                raise HTTPException(
                    status_code=400,
                    detail=f"Not enough stock for {item.product.name}",
                )

            total_price += (
                item.product.price
                * item.quantity
            )

        # Create order
        order = Order(
            user_id=current_user.id,
            total_price=total_price,
            status="pending",
        )

        db.add(order)

        # Get order.id without committing
        db.flush()

        # Create order items and reduce stock
        for item in cart.items:

            order_item = OrderItem(
                order_id=order.id,
                product_id=item.product_id,
                quantity=item.quantity,
                price=item.product.price,
            )

            db.add(order_item)

            # Reduce stock
            item.product.stock -= item.quantity

        # Clear cart
        (
            db.query(CartItem)
            .filter(CartItem.cart_id == cart.id)
            .delete()
        )

        # One commit for everything
        db.commit()

        db.refresh(order)

        return {
            "message": "Order created successfully",
            "order_id": order.id,
            "total_price": order.total_price,
        }

    except Exception:
        db.rollback()
        raise

@router.get(
    "",
    response_model=list[OrderResponse]
)
def list_orders(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):

    orders = (
        db.query(Order)
        .filter(Order.user_id == current_user.id)
        .order_by(Order.created_at.desc())
        .all()
    )

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

@router.get(
    "/{order_id}",
    response_model=OrderResponse
)
def get_order(
    order_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):

    order = (
        db.query(Order)
        .filter(
            Order.id == order_id,
            Order.user_id == current_user.id,
        )
        .first()
    )

    if not order:
        raise HTTPException(
            status_code=404,
            detail="Order not found",
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

@router.get(
    "/{order_id}/tracking",
    response_model=OrderTrackingResponse,
)
def track_order(
    order_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):

    order = (
        db.query(Order)
        .filter(
            Order.id == order_id,
            Order.user_id == current_user.id,
        )
        .first()
    )


    if order is None:
        raise HTTPException(
            status_code=404,
            detail="Order not found",
        )


    history = (
        db.query(OrderStatusHistory)
        .filter(
            OrderStatusHistory.order_id == order.id
        )
        .order_by(
            OrderStatusHistory.created_at.asc()
        )
        .all()
    )


    return {
        "order_id": order.id,
        "current_status": order.status,
        "history": [
            {
                "old_status": item.old_status,
                "new_status": item.new_status,
                "created_at": item.created_at,
            }
            for item in history
        ],
    }