from sqlalchemy.orm import Session

from app.models.order import Order


class OrderRepository:
    """
    Repository responsible for all database operations
    related to orders.
    """

    def __init__(self, db: Session):
        self.db = db

    def get_user_order(
        self,
        order_id: int,
        user_id: int,
    ) -> Order | None:
        """
        Retrieve an order that belongs to a specific user.
        """

        return (
            self.db.query(Order)
            .filter(
                Order.id == order_id,
                Order.user_id == user_id,
            )
            .first()
        )