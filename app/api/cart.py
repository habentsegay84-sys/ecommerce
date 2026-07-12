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

    # 1. Check product exists
    product = (
        db.query(Product)
        .filter(Product.id == item.product_id)
        .first()
    )

    if not product:
        raise HTTPException(
            status_code=404,
            detail="Product not found"
        )


    # 2. Find user's cart
    cart = (
        db.query(Cart)
        .filter(Cart.user_id == current_user.id)
        .first()
    )


    # 3. Create cart if user has no cart
    if not cart:
        cart = Cart(
            user_id=current_user.id
        )

        db.add(cart)
        db.commit()
        db.refresh(cart)


    # 4. Check if product already exists in cart
    existing_item = (
        db.query(CartItem)
        .filter(
            CartItem.cart_id == cart.id,
            CartItem.product_id == item.product_id
        )
        .first()
    )


    # 5. Update quantity or create new item
    if existing_item:

        existing_item.quantity += item.quantity

    else:

        new_item = CartItem(
            cart_id=cart.id,
            product_id=item.product_id,
            quantity=item.quantity
        )

        db.add(new_item)


    # 6. Save changes
    db.commit()


    return {
        "message": "Product added to cart"
    }

@router.get(
    "",
    response_model=CartResponse
)
def get_cart(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):

    cart = (
        db.query(Cart)
        .filter(Cart.user_id == current_user.id)
        .first()
    )

    if not cart:
        return CartResponse(
            items=[],
            total=0
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
        total=total
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
            detail="Quantity must be at least 1"
        )

    cart = (
        db.query(Cart)
        .filter(Cart.user_id == current_user.id)
        .first()
    )

    if not cart:
        raise HTTPException(
            status_code=404,
            detail="Cart not found"
        )

    cart_item = (
        db.query(CartItem)
        .filter(
            CartItem.cart_id == cart.id,
            CartItem.product_id == product_id
        )
        .first()
    )

    if not cart_item:
        raise HTTPException(
            status_code=404,
            detail="Product not found in cart"
        )

    cart_item.quantity = item.quantity

    db.commit()
    db.refresh(cart_item)

    return {
        "message": "Cart updated successfully",
        "product_id": cart_item.product_id,
        "quantity": cart_item.quantity
    }

@router.delete("/items/{product_id}")
def remove_cart_item(
    product_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):

    cart = (
        db.query(Cart)
        .filter(Cart.user_id == current_user.id)
        .first()
    )

    if not cart:
        raise HTTPException(
            status_code=404,
            detail="Cart not found"
        )

    cart_item = (
        db.query(CartItem)
        .filter(
            CartItem.cart_id == cart.id,
            CartItem.product_id == product_id
        )
        .first()
    )

    if not cart_item:
        raise HTTPException(
            status_code=404,
            detail="Product not found in cart"
        )

    db.delete(cart_item)
    db.commit()

    return {
        "message": "Product removed from cart"
    }

@router.delete("")
def clear_cart(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):

    cart = (
        db.query(Cart)
        .filter(Cart.user_id == current_user.id)
        .first()
    )

    if not cart:
        raise HTTPException(
            status_code=404,
            detail="Cart not found"
        )

    (
        db.query(CartItem)
        .filter(CartItem.cart_id == cart.id)
        .delete()
    )

    db.commit()

    return {
        "message": "Cart cleared successfully"
    }