from fastapi import APIRouter, Depends, Query,HTTPException
from sqlalchemy.orm import Session, joinedload

from app.database.session import get_db
from app.auth.dependencies import get_current_admin

from app.models.user import User
from app.models.payment import Payment
from app.models.order import Order

from app.schemas.admin_payment import AdminPaymentResponse
from app.schemas.payment_update import PaymentUpdate


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

    query = (
        db.query(Payment)
        .options(
            joinedload(Payment.order)
            .joinedload(Order.user)
        )
    )


    # Filter by payment status

    if status:
        query = query.filter(
            Payment.status == status
        )


    # Filter by payment method

    if payment_method:
        query = query.filter(
            Payment.payment_method == payment_method
        )


    # Pagination

    offset = (page - 1) * limit

    payments = (
        query
        .offset(offset)
        .limit(limit)
        .all()
    )


    return payments

@router.patch("/{payment_id}")
def update_payment_status(
    payment_id: int,
    payment_data: PaymentUpdate,
    current_admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db),
):
    payment = (
        db.query(Payment)
        .filter(Payment.id == payment_id)
        .first()
    )

    if payment is None:
        raise HTTPException(
            status_code=404,
            detail="Payment not found",
        )

    payment.status = payment_data.status

    db.commit()
    db.refresh(payment)

    return {
        "message": "Payment updated successfully",
        "payment": payment,
    }