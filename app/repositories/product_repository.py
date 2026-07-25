from sqlalchemy.orm import Session

from app.models.product import Product


class ProductRepository:
    """
    Repository responsible for product database operations.
    """

    def __init__(
        self,
        db: Session,
    ):
        self.db = db

    def get_by_id(
        self,
        product_id: int,
    ) -> Product | None:
        """
        Retrieve a product by its ID.
        """

        return (
            self.db.query(Product)
            .filter(Product.id == product_id)
            .first()
        )