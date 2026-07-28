from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session, joinedload

from app.database.session import get_db
from app.auth.dependencies import get_current_admin

from app.models.user import User
from app.models.product import Product
from app.models.inventory import InventoryLog

from app.schemas.inventory import InventoryLogResponse
from app.services.inventory_service import (
    update_stock_service,
    list_inventory_logs_service,
)

router = APIRouter(
    prefix="/admin/inventory",
    tags=["Admin Inventory"],
)

@router.patch("/{product_id}/stock")
def update_stock(
    product_id: int,
    stock: int,
    current_admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db),
):

    try:

        product = update_stock_service(
            db=db,
            product_id=product_id,
            new_stock=stock,
            admin_id=current_admin.id,
        )

        return {
            "message": "Stock updated successfully",
            "product_id": product.id,
            "new_stock": product.stock,
        }

    except ValueError as e:

        if str(e) == "Product not found":
            raise HTTPException(
                status_code=404,
                detail=str(e),
            )

        raise HTTPException(
            status_code=400,
            detail=str(e),
        )

@router.get(
    "/logs",
    response_model=list[InventoryLogResponse],
)
def get_inventory_logs(
    current_admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db),
):

    return list_inventory_logs_service(
        db=db,
    )