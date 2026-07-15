from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.auth.dependencies import get_current_admin

from app.models.user import User
from app.models.product import Product
from app.models.inventory import InventoryLog


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