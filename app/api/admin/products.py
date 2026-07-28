from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.auth.dependencies import get_current_admin

from app.models.user import User

from app.schemas.product import ProductCreate, ProductResponse

from app.services.product_service import (
    list_admin_products_service,
    create_product_service,
    update_product_service,
    delete_product_service,
    restore_product_service,
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
    
    try:
        return update_product_service(
            db=db,
            product_id=product_id,
            product_data=product_data,
            admin_id=current_admin.id,
        )

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

@router.delete(
    "/{product_id}",
    status_code=204,
)
def delete_product(
    product_id: int,
    current_admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db),
):

    try:
        delete_product_service(
            db=db,
            product_id=product_id,
        )

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

@router.patch(
    "/{product_id}/restore",
    response_model=ProductResponse,
)
def restore_product(
    product_id: int,
    current_admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db),
):

    try:
        return restore_product_service(
            db=db,
            product_id=product_id,
        )

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