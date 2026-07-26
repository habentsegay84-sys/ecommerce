from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.schemas.product import (ProductResponse)
from app.repositories.product_repository import ProductRepository

from app.services.product_service import (
    list_products_service,
    get_product_service,
)

router = APIRouter(
    prefix="/products",
    tags=["Products"],
)

@router.get(
    "",
    response_model=list[ProductResponse],
)
def list_products(
    search: str | None = Query(default=None),
    category_id: int | None = Query(default=None),
    min_price: float | None = Query(default=None),
    max_price: float | None = Query(default=None),
    sort: str | None = Query(default=None),
    page: int = Query(default=1, ge=1),
    limit: int = Query(default=10, ge=1, le=100),
    db: Session = Depends(get_db),
):
    return list_products_service(
        db=db,
        search=search,
        category_id=category_id,
        min_price=min_price,
        max_price=max_price,
        sort=sort,
        page=page,
        limit=limit,
    )

@router.get(
    "/{product_id}",
    response_model=ProductResponse,
)
def get_product(
    product_id: int,
    db: Session = Depends(get_db),
):
    """
    Retrieve one product by ID.
    """

    return get_product_service(
        db=db,
        product_id=product_id,
    )