from sqlalchemy.orm import Session

from app.models.cart import Cart
from app.models.cart_item import CartItem


class CartRepository:
    """
    Repository responsible for cart-related database operations.
    """

    def __init__(
        self,
        db: Session,
    ):
        self.db = db

    def get_by_user_id(
        self,
        user_id: int,
    ) -> Cart | None:
        """
        Retrieve the cart belonging to a specific user.
        """

        return (
            self.db.query(Cart)
            .filter(
                Cart.user_id == user_id,
            )
            .first()
        )

    def create(
        self,
        user_id: int,
    ) -> Cart:
        """
        Create a new cart for a user.
        """

        cart = Cart(
            user_id=user_id,
        )

        self.db.add(cart)
        self.db.commit()
        self.db.refresh(cart)

        return cart

    def get_item(
        self,
        cart_id: int,
        product_id: int,
    ) -> CartItem | None:
        """
        Retrieve a specific product from a cart.
        """

        return (
            self.db.query(CartItem)
            .filter(
                CartItem.cart_id == cart_id,
                CartItem.product_id == product_id,
            )
            .first()
        )

    def create_item(
        self,
        cart_id: int,
        product_id: int,
        quantity: int,
    ) -> CartItem:
        """
        Add a product to a cart.
        """

        cart_item = CartItem(
            cart_id=cart_id,
            product_id=product_id,
            quantity=quantity,
        )

        self.db.add(cart_item)

        return cart_item

    def delete_item(
        self,
        cart_item: CartItem,
    ) -> None:
        """
        Delete a specific item from a cart.
        """

        self.db.delete(cart_item)

    def delete_all_items(
        self,
        cart_id: int,
    ) -> None:
        """
        Remove all items belonging to a cart.
        """

        (
            self.db.query(CartItem)
            .filter(
                CartItem.cart_id == cart_id,
            )
            .delete()
        )

    def save(
        self,
    ) -> None:
        """
        Persist pending cart changes.
        """

        self.db.commit()

    def refresh(
        self,
        entity,
    ):
        """
        Refresh an entity from the database.
        """

        self.db.refresh(entity)

        return entity