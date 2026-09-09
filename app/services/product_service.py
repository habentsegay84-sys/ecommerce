from sqlalchemy.orm import Session

from app.models.product import Product
from app.repositories.product_repository import ProductRepository
from app.models.inventory import InventoryLog
from app.repositories.inventory_repository import InventoryRepository
from app.repositories.category_repository import CategoryRepository

def list_products_service(
    db: Session,
    search: str | None = None,
    category_id: int | None = None,
    min_price: float | None = None,
    max_price: float | None = None,
    sort: str | None = None,
    page: int = 1,
    limit: int = 10,
):
    """
    Return paginated products with filtering,
    sorting and rating summary.
    """

    repository = ProductRepository(db)

    products = repository.list_products(
        search=search,
        category_id=category_id,
        min_price=min_price,
        max_price=max_price,
        sort=sort,
        page=page,
        limit=limit,
    )

    for product in products:
        summary = repository.get_rating_summary(product.id)

        product.average_rating = summary["average_rating"]
        product.review_count = summary["review_count"]

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
    category_repository = CategoryRepository(db)

    category = category_repository.get_by_id(
        product_data.category_id
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

    product = repository.create(product)

    db.commit()

    return product

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
    category_repository = CategoryRepository(db)

    product = product_repository.get_by_id(
        product_id
    )

    if product is None:
        raise ValueError(
            "Product not found"
        )

    category = category_repository.get_by_id(
        product_data.category_id
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

    product = product_repository.update(product)

    db.commit()

    return product

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

    product = repository.delete(product)
    db.commit()
    return product

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

    product = repository.restore(product)
    db.commit()
    return product

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