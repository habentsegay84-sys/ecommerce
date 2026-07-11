from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database.session import get_db

from app.models.user import User
from app.models.product import Product
from app.models.cart import Cart
from app.models.cart_item import CartItem

from app.schemas.cart import CartItemCreate

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