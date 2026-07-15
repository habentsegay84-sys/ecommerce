from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session, joinedload


from app.database.session import get_db
from app.models.product import Product
from app.schemas.product import (ProductResponse)

router = APIRouter(
    prefix="/products",
    tags=["Products"],
)

@router.get("", response_model=list[ProductResponse])
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
    query = (
        db.query(Product)
        .options(joinedload(Product.category))
        .filter(Product.is_deleted == False)
    )

    if search:
        query = query.filter(Product.name.ilike(f"%{search}%"))

    if category_id:
        query = query.filter(Product.category_id == category_id)

    if min_price is not None:
        query = query.filter(Product.price >= min_price)

    if max_price is not None:
        query = query.filter(Product.price <= max_price)

    if sort == "price":
        query = query.order_by(Product.price)

    elif sort == "-price":
        query = query.order_by(Product.price.desc())

    offset = (page - 1) * limit

    return query.offset(offset).limit(limit).all()