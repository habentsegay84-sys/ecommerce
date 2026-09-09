from sqlalchemy.orm import Session

from app.models.cart import Cart
from app.models.cart_item import CartItem

from app.repositories.cart_repository import CartRepository
from app.repositories.product_repository import ProductRepository

class CartService:
    """
    Service responsible for cart business logic.

    Coordinates product validation, cart management,
    quantity updates, item removal, and cart clearing.
    """

    def __init__(
        self,
        db: Session,
    ):
        self.db = db
        self.cart_repository = CartRepository(db)
        self.product_repository = ProductRepository(db)

    def get_or_create_cart(
        self,
        user_id: int,
    ) -> Cart:
        """
        Retrieve the user's cart or create one if it does not exist.
        """

        cart = self.cart_repository.get_by_user_id(
            user_id
        )

        if not cart:
            cart = self.cart_repository.create(
                user_id
            )

        return cart

    def add_to_cart(
        self,
        user_id: int,
        product_id: int,
        quantity: int,
    ):
        """
        Add a product to the user's cart.

        If the product already exists in the cart,
        increase its quantity instead of creating
        a duplicate cart item.
        """

        product = self.product_repository.get_by_id(
            product_id
        )

        if not product:
            raise ValueError(
                "Product not found"
            )

        cart = self.get_or_create_cart(
            user_id
        )

        existing_item = (
            self.cart_repository.get_item(
                cart.id,
                product_id,
            )
        )

        if existing_item:
            existing_item.quantity += quantity

        else:
            self.cart_repository.create_item(
                cart_id=cart.id,
                product_id=product_id,
                quantity=quantity,
            )

        self.cart_repository.save()
        self.db.commit()

    def get_cart(
        self,
        user_id: int,
    ):
        """
        Retrieve the user's cart.
        """

        return self.cart_repository.get_by_user_id(
            user_id
        )

    def update_item(
        self,
        user_id: int,
        product_id: int,
        quantity: int,
    ):
        """
        Update the quantity of a product in the user's cart.
        """

        cart = self.cart_repository.get_by_user_id(
            user_id
        )

        if not cart:
            raise ValueError(
                "Cart not found"
            )

        cart_item = (
            self.cart_repository.get_item(
                cart.id,
                product_id,
            )
        )

        if not cart_item:
            raise ValueError(
                "Product not found in cart"
            )

        cart_item.quantity = quantity

        self.cart_repository.save()
        self.db.commit()
        self.cart_repository.refresh(cart_item)

        return cart_item

    def remove_item(
        self,
        user_id: int,
        product_id: int,
    ):
        """
        Remove a product from the user's cart.
        """

        cart = self.cart_repository.get_by_user_id(
            user_id
        )

        if not cart:
            raise ValueError(
                "Cart not found"
            )

        cart_item = (
            self.cart_repository.get_item(
                cart.id,
                product_id,
            )
        )

        if not cart_item:
            raise ValueError(
                "Product not found in cart"
            )

        self.cart_repository.delete_item(
            cart_item
        )

        self.cart_repository.save()
        self.db.commit()

    def clear_cart(
        self,
        user_id: int,
    ):
        """
        Remove all products from the user's cart.
        """

        cart = self.cart_repository.get_by_user_id(
            user_id
        )

        if not cart:
            raise ValueError(
                "Cart not found"
            )

        self.cart_repository.clear_items(
            cart.id
        )

        self.cart_repository.save()
        self.db.commit()