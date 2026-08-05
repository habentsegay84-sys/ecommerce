from datetime import datetime, timezone
from uuid import uuid4

from sqlalchemy.orm import Session

from app.models.payment import Payment
from app.models.user import User

from app.schemas.payment import PaymentCreate

from app.constants.payment_status import (
    PENDING,
    PROCESSING,
    SUCCESSFUL,
    FAILED,
)
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
    order = order_repository.get_with_payment(
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

    payment = payment_repository.build_payment(
        order_id=order.id,
        amount=order.total_price,
        payment_method=payment_data.payment_method,
    )
    # Update the order status before saving the payment.
    order_repository.update_status(
        order,
        PROCESSING,
    )

    payment_repository.create(payment)

    # Record the successful payment for auditing purposes.
    logger.info(
        "Payment status updated | payment_id=%s status=%s",
        payment.id,
        payment.status,
    )

    return payment_repository.update(
        payment,
    ) 

def update_payment_status(
    db: Session,
    payment_id: int,
    status: str,
):
    """
    Update payment status.

    Responsibilities:
    - Find payment.
    - Validate status.
    - Update payment.
    - Update related order when successful.
    """

    payment_repository = PaymentRepository(db)

    payment = payment_repository.get_by_id(
        payment_id,
    )

    if payment is None:
        raise ValueError(
            "Payment not found"
        )


    valid_statuses = {
        PENDING,
        PROCESSING,
        SUCCESSFUL,
        FAILED,
    }


    if status not in valid_statuses:
        raise ValueError(
            "Invalid payment status"
        )


    payment.status = status


    if status == SUCCESSFUL:
        payment.order.status = PROCESSING


    if status == SUCCESSFUL:
        payment.paid_at = datetime.now(timezone.utc)


    logger.info(
        "Payment status updated | payment_id=%s status=%s",
        payment.id,
        payment.status,
    )

    return payment_repository.update(
        payment,
    )

def list_payments_service(
    db: Session,
    status: str | None,
    payment_method: str | None,
    page: int,
    limit: int,
):
    """
    Retrieve payments for
    the admin dashboard.
    """

    repository = PaymentRepository(db)

    return repository.list_all(
        status=status,
        payment_method=payment_method,
        page=page,
        limit=limit,
    )
