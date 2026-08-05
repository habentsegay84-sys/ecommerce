from sqlalchemy.orm import Session

from app.models.order import Order
from app.models.order_status_history import OrderStatusHistory
from sqlalchemy.orm import joinedload

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

    def get_with_payment(
        self,
        order_id: int,
        user_id: int,
    ):
        """
        Retrieve a user's order together
        with its payment relationship.
        """


        return (
            self.db.query(Order)
            .options(
                joinedload(Order.payment)
            )
            .filter(
                Order.id == order_id,
                Order.user_id == user_id,
            )
            .first()
        )
    
    def update_status(
    self,
    order: Order,
    status: str,
    ):
        """
        Update an order's status.
        """

        order.status = status

        self.db.commit()
        self.db.refresh(order)

        return order
    
    def create(
        self,
        order: Order,
    ):
        """
        Save a new order.
        """

        self.db.add(order)
        self.db.commit()
        self.db.refresh(order)

        return order

    def get_by_id(
        self,
        order_id: int,
    ):
        """
        Retrieve an order by ID.
        """

        return (
            self.db.query(Order)
            .filter(Order.id == order_id)
            .first()
        )

    def update(
        self,
        order: Order,
    ):
        """
        Save changes to an order.
        """

        self.db.commit()
        self.db.refresh(order)

        return order

    def list_by_user(
        self,
        user_id: int,
    ):
        """
        Return all orders belonging to a user.
        """

        return (
            self.db.query(Order)
            .filter(Order.user_id == user_id)
            .order_by(Order.id.desc())
            .all()
        )

    def get_tracking_history(
        self,
        order_id: int,
    ):
        """
        Return tracking history for an order.
        """

        return (
            self.db.query(OrderStatusHistory)
            .filter(
                OrderStatusHistory.order_id == order_id,
            )
            .order_by(
                OrderStatusHistory.created_at.asc()
            )
            .all()
        )

    def flush(self):
        """
        Flush pending database changes.
        """

        self.db.flush()