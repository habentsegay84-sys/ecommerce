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