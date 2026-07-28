from sqlalchemy.orm import Session

from app.repositories.product_repository import ProductRepository
from app.repositories.inventory_repository import InventoryRepository
from app.models.inventory import InventoryLog
from app.schemas.inventory import (
    InventoryLogResponse,
)

def update_stock_service(
    db: Session,
    product_id: int,
    new_stock: int,
    admin_id: int,
):
    """
    Update product stock and
    create an inventory log.
    """

    product_repository = ProductRepository(db)
    inventory_repository = InventoryRepository(db)

    product = product_repository.get_by_id(
        product_id,
    )

    if product is None:
        raise ValueError(
            "Product not found"
        )

    if new_stock < 0:
        raise ValueError(
            "Stock cannot be negative"
        )

    if product.stock == new_stock:
        raise ValueError(
            "Stock is already this value"
        )

    old_stock = product.stock

    product.stock = new_stock

    log = InventoryLog(
        product_id=product.id,
        old_stock=old_stock,
        new_stock=new_stock,
        change_type="admin_update",
        changed_by=admin_id,
    )

    inventory_repository.create_log(log)

    return product_repository.update(product)

def list_inventory_logs_service(
    db: Session,
):
    """
    Return formatted inventory logs.
    """

    repository = InventoryRepository(db)

    logs = repository.list_logs()

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