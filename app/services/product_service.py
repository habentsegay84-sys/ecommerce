from sqlalchemy.orm import Session

from app.models.product import Product
from app.repositories.product_repository import ProductRepository
from app.models.category import Category
from app.models.inventory import InventoryLog
from app.repositories.inventory_repository import InventoryRepository

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
    admin_id: int,
):
    """
    Update an existing product.
    """

    product_repository = ProductRepository(db)
    inventory_repository = InventoryRepository(db)

    product = product_repository.get_by_id(
        product_id
    )

    if product is None:
        raise ValueError(
            "Product not found"
        )

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

    old_stock = product.stock

    product.name = product_data.name
    product.description = product_data.description
    product.price = product_data.price
    product.stock = product_data.stock
    product.category_id = product_data.category_id

    if old_stock != product.stock:

        inventory_repository.create_log(
            InventoryLog(
                product_id=product.id,
                old_stock=old_stock,
                new_stock=product.stock,
                change_type="admin_update",
                changed_by=admin_id,
            )
        )

    return product_repository.update(product)

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

    if product.is_deleted:
        raise ValueError(
            "Product already deleted"
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
    
    if not product.is_deleted:
        raise ValueError(
            "Product is already active"
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