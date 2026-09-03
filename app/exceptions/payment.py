from fastapi import HTTPException


class OrderAlreadyPaidError(HTTPException):
    """
    Raised when a payment already exists for an order.
    """

    def __init__(self):
        super().__init__(
            status_code=400,
            detail="Order already paid",
        )


class PaymentNotFoundError(HTTPException):
    """
    Raised when a payment cannot be found.
    """

    def __init__(self):
        super().__init__(
            status_code=404,
            detail="Payment not found",
        )


class InvalidPaymentStatusError(HTTPException):
    """
    Raised when an invalid payment status is provided.
    """

    def __init__(self):
        super().__init__(
            status_code=400,
            detail="Invalid payment status",
        )