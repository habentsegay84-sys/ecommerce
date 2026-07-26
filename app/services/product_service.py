from sqlalchemy.orm import Session

from app.models.product import Product
from app.repositories.product_repository import ProductRepository
from app.models.category import Category

def list_products_service(
    db: Session,
    search: str | None,
    category_id: int | None,
    min_price: float | None,
    max_price: float | None,
    sort: str | None,
    page: int,
    limit: int,
):
    """
    Return paginated products with filtering,
    sorting and rating summary.
    """

    repository = ProductRepository(db)

    query = (
        db.query(Product)
        .options(
            joinedload(Product.category)
        )
        .filter(
            Product.is_deleted == False
        )
    )

    if search:
        query = query.filter(
            Product.name.ilike(f"%{search}%")
        )

    if category_id:
        query = query.filter(
            Product.category_id == category_id
        )

    if min_price is not None:
        query = query.filter(
            Product.price >= min_price
        )

    if max_price is not None:
        query = query.filter(
            Product.price <= max_price
        )

    if sort == "price":
        query = query.order_by(
            Product.price
        )

    elif sort == "-price":
        query = query.order_by(
            Product.price.desc()
        )

    offset = (page - 1) * limit

    products = (
        query
        .offset(offset)
        .limit(limit)
        .all()
    )

    for product in products:

        summary = repository.get_rating_summary(
            product.id,
        )

        product.average_rating = (
            summary["average_rating"]
        )

        product.review_count = (
            summary["review_count"]
        )

    return products

def get_product_service(
    db: Session,
    product_id: int,
):
    """
    Retrieve a single product with
    category and rating information.
    """

    repository = ProductRepository(db)

    product = repository.get_product_with_category(
        product_id,
    )

    if product is None:
        raise ValueError(
            "Product not found"
        )

    summary = repository.get_rating_summary(
        product.id,
    )

    product.average_rating = (
        summary["average_rating"]
    )

    product.review_count = (
        summary["review_count"]
    )

    return product

def create_product_service(
    db: Session,
    product_data,
):
    """
    Create a new product after validating category.
    """

    repository = ProductRepository(db)

    category = (
        db.query(Category)
        .filter(
            Category.id == product_data.category_id
        )
        .first()
    )

    if category is None:
        raise ValueError(
            "Category not found"
        )

    product = Product(
        name=product_data.name,
        description=product_data.description,
        price=product_data.price,
        stock=product_data.stock,
        category_id=product_data.category_id,
    )

    return repository.create(product)

def update_product_service(
    db: Session,
    product_id: int,
    product_data,
):
    """
    Update an existing product.
    """

    repository = ProductRepository(db)

    product = repository.get_by_id(
        product_id
    )

    if product is None:
        raise ValueError(
            "Product not found"
        )

    if product_data.name is not None:
        product.name = product_data.name

    if product_data.description is not None:
        product.description = product_data.description

    if product_data.price is not None:
        product.price = product_data.price

    if product_data.stock is not None:
        product.stock = product_data.stock

    if product_data.category_id is not None:
        product.category_id = product_data.category_id

    return repository.update(product)

def delete_product_service(
    db: Session,
    product_id: int,
):
    """
    Soft delete a product.
    """

    repository = ProductRepository(db)

    product = repository.get_by_id(
        product_id
    )

    if product is None:
        raise ValueError(
            "Product not found"
        )

    return repository.delete(product)

def restore_product_service(
    db: Session,
    product_id: int,
):
    """
    Restore a deleted product.
    """

    repository = ProductRepository(db)

    product = repository.get_by_id(
        product_id
    )

    if product is None:
        raise ValueError(
            "Product not found"
        )

    return repository.restore(product)

def list_admin_products_service(
    db: Session,
    status: str | None,
    search: str | None,
    category_id: int | None,
    page: int,
    limit: int,
):
    """
    Retrieve products for admin dashboard.
    """

    repository = ProductRepository(db)

    return repository.list_admin_products(
        status=status,
        search=search,
        category_id=category_id,
        page=page,
        limit=limit,
    )