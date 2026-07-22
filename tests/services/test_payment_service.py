from app.services.payment_service import pay_order_service
from app.schemas.payment import PaymentCreate

import pytest

from app.services.payment_service import pay_order_service
from app.schemas.payment import PaymentCreate
from app.models.payment import Payment
from app.exceptions.payment import OrderAlreadyPaidError

from app.exceptions.order import OrderNotFoundError

def test_successful_payment(
    db,
    test_user,
    test_order,
):
    """
    Test successful payment creation.
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

    assert payment.status == "successful"

    assert payment.amount == 100

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