from sqlalchemy.orm import Session
from sqlalchemy.orm import joinedload

from app.models.payment import Payment
from app.models.order import Order
from uuid import uuid4

from app.constants.payment_status import SUCCESSFUL


class PaymentRepository:
    """
    Repository responsible for database operations
    related to payments.
    """

    def __init__(
        self,
        db: Session,
    ):
        self.db = db

    def create(
        self,
        payment: Payment,
    ) -> Payment:
        """
        Save a new payment.
        """

        self.db.add(payment)

        return payment

    def build_payment(
        self,
        order_id: int,
        amount: float,
        payment_method: str,
    ) -> Payment:
        """
        Build a payment entity.
        """

        return Payment(
            order_id=order_id,
            amount=amount,
            payment_method=payment_method,
            status=SUCCESSFUL,
            transaction_reference=str(uuid4()),
            paid_at=None,
        )

    def get_by_id(
        self,
        payment_id: int,
    ) -> Payment | None:
        """
        Retrieve a payment by ID.
        """

        return (
            self.db.query(Payment)
            .filter(
                Payment.id == payment_id
            )
            .first()
        )

    def update(
        self,
        payment: Payment,
    ) -> Payment:
        """
        Save payment changes.
        """

        self.db.commit()
        self.db.refresh(payment)

        return payment

    def list_all(
        self,
        status: str | None = None,
        payment_method: str | None = None,
        page: int = 1,
        limit: int = 10,
    ):
        """
        Retrieve payments for admin.
        """

        query = (
            self.db.query(Payment)
            .options(
                joinedload(Payment.order)
                .joinedload(Order.user)
            )
        )

        if status:
            query = query.filter(
                Payment.status == status
            )

        if payment_method:
            query = query.filter(
                Payment.payment_method == payment_method
            )

        offset = (page - 1) * limit

        return (
            query
            .offset(offset)
            .limit(limit)
            .all()
        )

    