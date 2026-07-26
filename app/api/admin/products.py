from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.auth.dependencies import get_current_admin

from app.models.user import User

from app.schemas.product import ProductCreate, ProductResponse

from app.services.product_service import (
    list_admin_products_service,
    create_product_service,
)

router = APIRouter(
    prefix="/admin/products",
    tags=["Admin Products"],
)

@router.get(
    "",
    response_model=list[ProductResponse],
)
def list_admin_products(
    status: str | None = Query(default=None),
    search: str | None = Query(default=None),
    category_id: int | None = Query(default=None),
    page: int = Query(default=1, ge=1),
    limit: int = Query(default=10, ge=1, le=100),
    current_admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db),
):

    return list_admin_products_service(
        db=db,
        status=status,
        search=search,
        category_id=category_id,
        page=page,
        limit=limit,
    )

@router.post(
    "",
    response_model=ProductResponse,
    status_code=201,
)
def create_product(
    product: ProductCreate,
    current_admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db),
):

    try:
        return create_product_service(
            db=db,
            product_data=product,
        )

    except ValueError as e:
        raise HTTPException(
            status_code=404,
            detail=str(e),
        )
@router.patch(
    "/{product_id}",
    response_model=ProductResponse,
)
def update_product(
    product_id: int,
    product_data: ProductCreate,
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

    category = (
        db.query(Category)
        .filter(
            Category.id == product_data.category_id
        )
        .first()
    )

    if category is None:
        raise HTTPException(
            status_code=404,
            detail="Category not found",
        )

    old_stock = product.stock

    product.name = product_data.name
    product.description = product_data.description
    product.price = product_data.price
    product.stock = product_data.stock
    product.category_id = product_data.category_id

    # Create inventory history if stock changed

    if old_stock != product.stock:

        inventory_log = InventoryLog(
            product_id=product.id,
            old_stock=old_stock,
            new_stock=product.stock,
            change_type="admin_update",
            changed_by=current_admin.id,
        )

        db.add(inventory_log)

    db.commit()
    db.refresh(product)

    return product

@router.delete(
    "/{product_id}",
    status_code=204,
)
def delete_product(
    product_id: int,
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

    if product.is_deleted:
        raise HTTPException(
            status_code=400,
            detail="Product already deleted",
        )

    product.is_deleted = True

    db.commit()

@router.patch(
    "/{product_id}/restore",
    response_model=ProductResponse,
)
def restore_product(
    product_id: int,
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

    if not product.is_deleted:
        raise HTTPException(
            status_code=400,
            detail="Product is already active",
        )

    product.is_deleted = False

    db.commit()
    db.refresh(product)

    return product