from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.auth.dependencies import get_current_admin

from app.models.user import User
from app.models.product import Product
from app.models.category import Category

from app.schemas.product import ProductCreate, ProductResponse

from sqlalchemy.orm import joinedload


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

    query = (
        db.query(Product)
        .options(joinedload(Product.category))
    )


    # Filter by status

    if status == "active":
        query = query.filter(
            Product.is_deleted == False
        )

    elif status == "deleted":
        query = query.filter(
            Product.is_deleted == True
        )


    # Search

    if search:
        query = query.filter(
            Product.name.ilike(
                f"%{search}%"
            )
        )


    # Category filter

    if category_id:
        query = query.filter(
            Product.category_id == category_id
        )


    # Pagination

    offset = (page - 1) * limit

    products = (
        query
        .offset(offset)
        .limit(limit)
        .all()
    )


    return products

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

    category = (
        db.query(Category)
        .filter(Category.id == product.category_id)
        .first()
    )

    if category is None:
        raise HTTPException(
            status_code=404,
            detail="Category not found",
        )

    new_product = Product(
        **product.model_dump()
    )

    db.add(new_product)
    db.commit()
    db.refresh(new_product)

    return new_product

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

    product.name = product_data.name
    product.description = product_data.description
    product.price = product_data.price
    product.stock = product_data.stock
    product.category_id = product_data.category_id

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