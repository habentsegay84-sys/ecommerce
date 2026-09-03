from app.services.payment_service import (
    pay_order_service,
    update_payment_status,
)
from app.schemas.payment import PaymentCreate
from app.models.payment import Payment
from app.exceptions.payment import (
    OrderAlreadyPaidError,
    InvalidPaymentStatusError,
    PaymentNotFoundError,
)
from app.exceptions.order import OrderNotFoundError

import pytest

from app.constants.payment_status import (
    SUCCESSFUL,
    FAILED,
)

def test_payment_creation_starts_as_pending(
    db,
    test_user,
    test_order,
):
    """
    Test that creating a payment starts it as pending.
    """

    payment_data = PaymentCreate(
        payment_method="cash"
    )

    payment = pay_order_service(
        db=db,
        order_id=test_order.id,
        payment_data=payment_data,
        current_user=test_user,
    )

    assert payment.order_id == test_order.id
    assert payment.status == "pending"
    assert payment.amount == 100
    assert payment.transaction_reference is not None


def test_duplicate_payment_is_blocked(
    db,
    test_user,
    test_order,
):
    """
    Test that an order cannot be paid twice.
    """

    existing_payment = Payment(
        order_id=test_order.id,
        amount=test_order.total_price,
        payment_method="cash",
        status="successful",
        transaction_reference="old-payment",
    )

    db.add(existing_payment)
    db.commit()

    payment_data = PaymentCreate(
        payment_method="cash"
    )

    with pytest.raises(OrderAlreadyPaidError):

        pay_order_service(
            db=db,
            order_id=test_order.id,
            payment_data=payment_data,
            current_user=test_user,
        )


def test_user_cannot_pay_someone_elses_order(
    db,
    test_order,
    another_user,
):
    """
    Test that users cannot pay orders
    that do not belong to them.
    """

    payment_data = PaymentCreate(
        payment_method="cash"
    )

    with pytest.raises(OrderNotFoundError):

        pay_order_service(
            db=db,
            order_id=test_order.id,
            payment_data=payment_data,
            current_user=another_user,
        )

def test_payment_can_be_marked_successful(
    db,
    test_user,
    test_order,
):
    """
    Test that a pending payment can become successful.
    """


    payment_data = PaymentCreate(
        payment_method="cash"
    )

    payment = pay_order_service(
        db=db,
        order_id=test_order.id,
        payment_data=payment_data,
        current_user=test_user,
    )

    assert payment.status == "pending"
    assert payment.paid_at is None

    updated_payment = update_payment_status(
        db=db,
        payment_id=payment.id,
        status="successful",
    )

    assert updated_payment.status == "successful"
    assert updated_payment.paid_at is not None
    assert updated_payment.order.status == "processing"


def test_invalid_payment_status_is_rejected(
    db,
    test_user,
    test_order,
):
    """
    Test that an invalid payment status is rejected.
    """


    payment_data = PaymentCreate(
        payment_method="cash"
    )

    payment = pay_order_service(
        db=db,
        order_id=test_order.id,
        payment_data=payment_data,
        current_user=test_user,
    )

    with pytest.raises(InvalidPaymentStatusError):
        update_payment_status(
            db=db,
            payment_id=payment.id,
            status="invalid_status",
        )


def test_nonexistent_payment_is_rejected(
    db,
):
    """
    Test that updating a nonexistent payment is rejected.
    """

    with pytest.raises(PaymentNotFoundError):
        update_payment_status(
            db=db,
            payment_id=999999,
            status="successful",
        )

def test_successful_payment_cannot_be_changed(
    db,
    test_user,
    test_order,
):
    """
    Test that a successful payment cannot be changed
    to another status.
    """

    payment_data = PaymentCreate(
        payment_method="cash"
    )

    payment = pay_order_service(
        db=db,
        order_id=test_order.id,
        payment_data=payment_data,
        current_user=test_user,
    )

    update_payment_status(
        db=db,
        payment_id=payment.id,
        status=SUCCESSFUL,
    )

    with pytest.raises(InvalidPaymentStatusError):
        update_payment_status(
            db=db,
            payment_id=payment.id,
            status=FAILED,
        )