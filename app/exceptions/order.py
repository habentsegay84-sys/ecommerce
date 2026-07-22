from fastapi import HTTPException


class OrderNotFoundError(HTTPException):
    """
    Raised when an order cannot be found or does not belong
    to the authenticated user.
    """

    def __init__(self):
        super().__init__(
            status_code=404,
            detail="Order not found",
        )