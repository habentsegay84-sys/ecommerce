from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session, joinedload

from app.database.session import get_db
from app.auth.dependencies import get_current_admin

from app.models.user import User
from app.models.product import Product
from app.models.inventory import InventoryLog

from app.schemas.inventory import InventoryLogResponse

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

    product = (
        db.query(Product)
        .filter(Product.id == product_id)
        .first()
    )

    if product is None:
        raise HTTPException(
            status_code=404,
            detail="Product not found",
        )


    if stock < 0:
        raise HTTPException(
            status_code=400,
            detail="Stock cannot be negative",
        )


    old_stock = product.stock

    product.stock = stock

    if old_stock == stock:
        raise HTTPException(
            status_code=400,
            detail="Stock is already this value",
        )

    log = InventoryLog(
        product_id=product.id,
        old_stock=old_stock,
        new_stock=stock,
        change_type="admin_update",
        changed_by=current_admin.id,
    )

    db.add(log)

    db.commit()
    db.refresh(product)


    return {
        "message": "Stock updated successfully",
        "product_id": product.id,
        "new_stock": product.stock,
    }

@router.get(
    "/logs",
    response_model=list[InventoryLogResponse],
)
def get_inventory_logs(
    current_admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db),
):

    logs = (
        db.query(InventoryLog)
        .options(
            joinedload(InventoryLog.product)
        )
        .order_by(
            InventoryLog.created_at.desc()
        )
        .all()
    )

    response = []

    for log in logs:

        response.append(
            InventoryLogResponse(
                id=log.id,
                product_id=log.product_id,
                product_name=log.product.name,
                old_stock=log.old_stock,
                new_stock=log.new_stock,
                change_type=log.change_type,
                changed_by=log.changed_by,
                created_at=log.created_at,
            )
        )

    return response