from sqlalchemy.orm import Session

from app.models.product import Product
from sqlalchemy import func
from app.models.review import Review
from sqlalchemy.orm import joinedload


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

    def get_product_with_category(
        self,
        product_id: int,
    ) -> Product | None:
        """
        Retrieve one product together with its category.
        """

        return (
            self.db.query(Product)
            .options(
                joinedload(Product.category)
            )
            .filter(
                Product.id == product_id,
                Product.is_deleted == False,
            )
            .first()
        )

    def get_rating_summary(
        self,
        product_id: int,
    ):
        """
        Return average rating and review count
        for a product.
        """

        average_rating, review_count = (
            self.db.query(
                func.avg(Review.rating),
                func.count(Review.id),
            )
            .filter(
                Review.product_id == product_id,
            )
            .first()
        )

        return {
            "average_rating": (
                round(float(average_rating), 2)
                if average_rating
                else None
            ),
            "review_count": review_count,
        }

    def create(
        self,
        product: Product,
    ):
        """
        Add a new product to the current transaction.
        """

        self.db.add(product)
        self.db.flush()

        return product


    def update(
        self,
        product: Product,
    ):
        """
        Update a product in the current transaction.
        """

        self.db.flush()

        return product


    def delete(self, product: Product):
        """
        Soft delete a product in the current transaction.
        """
        product.is_deleted = True
        self.db.flush()
        return product


    def restore(self, product: Product):
        """
        Restore a product in the current transaction.
        """
        product.is_deleted = False
        self.db.flush()
        return product

    def list_admin_products(
        self,
        status: str | None = None,
        search: str | None = None,
        category_id: int | None = None,
        page: int = 1,
        limit: int = 10,
    ):
        """
        Retrieve products for admin dashboard.
        Includes deleted products.
        """

        query = (
            self.db.query(Product)
            .options(
                joinedload(Product.category)
            )
        )

        if status == "active":
            query = query.filter(
                Product.is_deleted == False
            )

        elif status == "deleted":
            query = query.filter(
                Product.is_deleted == True
            )

        if search:
            query = query.filter(
                Product.name.ilike(
                    f"%{search}%"
                )
            )

        if category_id:
            query = query.filter(
                Product.category_id == category_id
            )

        offset = (page - 1) * limit

        return (
            query
            .offset(offset)
            .limit(limit)
            .all()
        )

    def decrease_stock(
        self,
        product_id: int,
        quantity: int,
    ) -> tuple[int, int] | None:
        """
        Atomically decrease product stock.

        Returns:
            (old_stock, new_stock) when successful.
            None when the product does not have enough stock.
        """

        product = (
            self.db.query(Product)
            .filter(Product.id == product_id)
            .with_for_update()
            .first()
        )

        if product is None:
            return None

        if product.stock < quantity:
            return None

        old_stock = product.stock
        product.stock -= quantity
        new_stock = product.stock

        return old_stock, new_stock

    def list_products(
        self,
        search: str | None = None,
        category_id: int | None = None,
        min_price: float | None = None,
        max_price: float | None = None,
        sort: str | None = None,
        page: int = 1,
        limit: int = 10,
    ):
        """
        Return paginated, non-deleted products with filtering and sorting.
        """

        query = (
            self.db.query(Product)
            .options(joinedload(Product.category))
            .filter(Product.is_deleted == False)
        )

        if search:
            query = query.filter(
                Product.name.ilike(f"%{search}%")
            )

        if category_id:
            query = query.filter(
                Product.category_id == category_id
            )

        if min_price is not None:
            query = query.filter(
                Product.price >= min_price
            )

        if max_price is not None:
            query = query.filter(
                Product.price <= max_price
            )

        if sort == "price":
            query = query.order_by(Product.price)

        elif sort == "-price":
            query = query.order_by(Product.price.desc())

        offset = (page - 1) * limit

        return (
            query
            .offset(offset)
            .limit(limit)
            .all()
        )