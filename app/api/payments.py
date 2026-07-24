from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database.session import get_db

from app.auth.dependencies import get_current_user

from app.models.user import User
from app.models.order import Order
from app.models.payment import Payment
from app.auth.admin import get_current_admin

from app.schemas.payment import (
    PaymentCreate,
    PaymentResponse,
)
from app.schemas.payment_status import PaymentStatusUpdate

from app.services.payment_service import (
    pay_order_service,
    update_payment_status,
)

from uuid import uuid4
from datetime import datetime

from app.constants.payment_status import (
    PENDING,
    PROCESSING,
    SUCCESSFUL,
    FAILED,
)


router = APIRouter(
    prefix="/payments",
    tags=["Payments"],
)

@router.post(
    "/{order_id}/pay",
    response_model=PaymentResponse,
)
def pay_order(
    order_id: int,
    payment_data: PaymentCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    
    return pay_order_service(
        db=db,
        order_id=order_id,
        payment_data=payment_data,
        current_user=current_user,
    )

@router.patch(
    "/{payment_id}/status",
    response_model=PaymentResponse,
)
def change_payment_status(
    payment_id: int,
    payment_status: PaymentStatusUpdate,
    current_user: User = Depends(get_current_admin),
    db: Session = Depends(get_db),
):
    """
    Update payment status.

    Example:
    pending -> processing
    processing -> successful
    processing -> failed
    """

    return update_payment_status(
        db=db,
        payment_id=payment_id,
        status=payment_status.status,
    )

