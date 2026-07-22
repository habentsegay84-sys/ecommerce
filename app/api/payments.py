from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database.session import get_db

from app.auth.dependencies import get_current_user

from app.models.user import User
from app.models.order import Order
from app.models.payment import Payment

from app.schemas.payment import (
    PaymentCreate,
    PaymentResponse,
)
from app.services.payment_service import pay_order_service

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

