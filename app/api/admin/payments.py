from fastapi import APIRouter, Depends, Query,HTTPException
from sqlalchemy.orm import Session, joinedload

from app.database.session import get_db
from app.auth.dependencies import get_current_admin

from app.models.user import User
from app.models.payment import Payment
from app.models.order import Order

from app.schemas.admin_payment import AdminPaymentResponse
from app.schemas.payment_update import PaymentUpdate
from app.services.payment_service import (
    list_payments_service,
    update_payment_status,
)


router = APIRouter(
    prefix="/admin/payments",
    tags=["Admin Payments"],
)
@router.get(
    "",
    response_model=list[AdminPaymentResponse],
)
def list_payments(
    status: str | None = Query(default=None),
    payment_method: str | None = Query(default=None),
    page: int = Query(default=1, ge=1),
    limit: int = Query(default=10, ge=1, le=100),
    current_admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db),
):

    return list_payments_service(
        db=db,
        status=status,
        payment_method=payment_method,
        page=page,
        limit=limit,
    )

@router.patch("/{payment_id}")
def update_payment_status_admin(
    payment_id: int,
    payment_data: PaymentUpdate,
    current_admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db),
):
    try:

        payment = update_payment_status(
            db=db,
            payment_id=payment_id,
            status=payment_data.status,
        )

        return {
            "message": "Payment updated successfully",
            "payment": payment,
        }

    except ValueError as e:

        if str(e) == "Payment not found":
            raise HTTPException(
                status_code=404,
                detail=str(e),
            )

        raise HTTPException(
            status_code=400,
            detail=str(e),
        )
    