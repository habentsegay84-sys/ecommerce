from datetime import datetime
from uuid import uuid4

from sqlalchemy.orm import Session

from app.models.payment import Payment
from app.models.user import User

from app.schemas.payment import PaymentCreate

from app.constants.payment_status import SUCCESSFUL
from app.exceptions.order import OrderNotFoundError
from app.exceptions.payment import OrderAlreadyPaidError
from app.repositories.order_repository import OrderRepository
from app.repositories.payment_repository import PaymentRepository
from app.core.logger import logger
from app.constants.order_status import PROCESSING

def pay_order_service(
    db: Session,
    order_id: int,
    payment_data: PaymentCreate,
    current_user: User,
):
    """
    Process payment for an order owned by the authenticated user.

    Responsibilities:
    - Verify the order exists.
    - Prevent duplicate payments.
    - Create a payment record.
    - Update the order status.
    - Persist the payment.
    """

    # Repository responsible for order database operations.
    order_repository = OrderRepository(db)

    # Repository responsible for payment persistence.
    payment_repository = PaymentRepository(db)

    # Retrieve the authenticated user's order.
    order = order_repository.get_user_order(
        order_id=order_id,
        user_id=current_user.id,
    )

    if order is None:
        # Record failed payment attempts for missing orders.
        logger.warning(
            "Order not found | order_id=%s user_id=%s",
            order_id,
            current_user.id,
        )

        raise OrderNotFoundError()

    if order.payment:
        # Prevent duplicate payments for the same order.
        logger.warning(
            "Duplicate payment attempt | order_id=%s",
            order.id,
        )

        raise OrderAlreadyPaidError()

    payment = Payment(
        order_id=order.id,
        amount=order.total_price,
        payment_method=payment_data.payment_method,
        status=SUCCESSFUL,
        transaction_reference=str(uuid4()),
        paid_at=datetime.utcnow(),
    )
    # Update the order status before saving the payment.
    order.status = PROCESSING

    saved_payment = payment_repository.create(payment)

    # Record the successful payment for auditing purposes.
    logger.info(
        "Payment created | payment_id=%s order_id=%s user_id=%s amount=%s",
        saved_payment.id,
        order.id,
        current_user.id,
        payment.amount,
    )

    return saved_payment