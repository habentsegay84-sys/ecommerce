from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database.session import get_db

from app.models.user import User
from app.models.product import Product
from app.models.cart import Cart
from app.models.cart_item import CartItem

from app.schemas.cart import (
    CartItemCreate,
    CartItemUpdate,
    CartItemResponse,
    CartResponse
)

from app.auth.dependencies import get_current_user
from app.services.cart_service import CartService

router = APIRouter(
    prefix="/cart",
    tags=["Cart"],
)

@router.post("/add")
def add_to_cart(
    item: CartItemCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    service = CartService(db)

    try:
        service.add_to_cart(
            user_id=current_user.id,
            product_id=item.product_id,
            quantity=item.quantity,
        )

    except ValueError as exc:
        raise HTTPException(
            status_code=404,
            detail=str(exc),
        )

    return {
        "message": "Product added to cart"
    }

@router.get(
    "",
    response_model=CartResponse,
)
def get_cart(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    service = CartService(db)

    cart = service.get_cart(
        user_id=current_user.id,
    )

    if not cart:
        return CartResponse(
            items=[],
            total=0,
        )

    items = []
    total = 0

    for cart_item in cart.items:
        subtotal = (
            cart_item.product.price
            * cart_item.quantity
        )

        total += subtotal

        items.append(
            CartItemResponse(
                product_id=cart_item.product.id,
                product_name=cart_item.product.name,
                price=cart_item.product.price,
                quantity=cart_item.quantity,
                subtotal=subtotal,
            )
        )

    return CartResponse(
        items=items,
        total=total,
    )

@router.patch("/items/{product_id}")
def update_cart_item(
    product_id: int,
    item: CartItemUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if item.quantity < 1:
        raise HTTPException(
            status_code=400,
            detail="Quantity must be at least 1",
        )

    service = CartService(db)

    try:
        cart_item = service.update_item(
            user_id=current_user.id,
            product_id=product_id,
            quantity=item.quantity,
        )

    except ValueError as exc:
        raise HTTPException(
            status_code=404,
            detail=str(exc),
        )

    return {
        "message": "Cart updated successfully",
        "product_id": cart_item.product_id,
        "quantity": cart_item.quantity,
    }

@router.delete("/items/{product_id}")
def remove_cart_item(
    product_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    service = CartService(db)

    try:
        service.remove_item(
            user_id=current_user.id,
            product_id=product_id,
        )

    except ValueError as exc:
        raise HTTPException(
            status_code=404,
            detail=str(exc),
        )

    return {
        "message": "Product removed from cart"
    }

@router.delete("")
def clear_cart(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    service = CartService(db)

    try:
        service.clear_cart(
            user_id=current_user.id,
        )

    except ValueError as exc:
        raise HTTPException(
            status_code=404,
            detail=str(exc),
        )

    return {
        "message": "Cart cleared successfully"
    }