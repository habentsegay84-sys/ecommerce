from sqlalchemy.orm import Session

from app.models.payment import Payment


class PaymentRepository:
    """
    Repository responsible for database operations
    related to payments.
    """

    def __init__(self, db: Session):
        self.db = db

    def create(self, payment: Payment) -> Payment:
        """
        Persist a new payment and return the saved entity.
        """

    def create(
        self,
        payment: Payment,
    ) -> Payment:
        """
        Add a new payment to the current transaction.
        """

        self.db.add(payment)

        return payment