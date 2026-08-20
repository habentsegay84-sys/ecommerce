from app.models.product import Product
from app.models.category import Category
from app.models.inventory import InventoryLog
from app.schemas.product import ProductCreate

from app.services.product_service import (
    list_products_service,
    get_product_service,
    create_product_service,
    update_product_service,
    delete_product_service,
    restore_product_service,
    list_admin_products_service,
)


def create_category(db, name="Electronics"):
    category = Category(
        name=name,
    )

    db.add(category)
    db.commit()
    db.refresh(category)

    return category


def create_product(
    db,
    category_id,
    name="Laptop",
    price=1000,
    stock=10,
):
    product = Product(
        name=name,
        description="Test product",
        price=price,
        stock=stock,
        category_id=category_id,
    )

    db.add(product)
    db.commit()
    db.refresh(product)

    return product

def test_list_products_returns_products(db):
    category = create_category(db)

    create_product(
        db,
        category.id,
        name="Laptop",
        price=1000,
    )

    create_product(
        db,
        category.id,
        name="Phone",
        price=500,
    )

    products = list_products_service(
        db=db,
        search=None,
        category_id=None,
        min_price=None,
        max_price=None,
        sort=None,
        page=1,
        limit=10,
    )

    assert len(products) == 2

def test_list_products_search(db):
    category = create_category(db)

    create_product(
        db,
        category.id,
        name="Gaming Laptop",
    )

    create_product(
        db,
        category.id,
        name="iPhone",
    )

    products = list_products_service(
        db=db,
        search="Laptop",
        category_id=None,
        min_price=None,
        max_price=None,
        sort=None,
        page=1,
        limit=10,
    )

    assert len(products) == 1
    assert products[0].name == "Gaming Laptop"

def test_list_products_price_filters(db):
    category = create_category(db)

    create_product(
        db,
        category.id,
        name="Cheap",
        price=100,
    )

    create_product(
        db,
        category.id,
        name="Medium",
        price=500,
    )

    create_product(
        db,
        category.id,
        name="Expensive",
        price=1000,
    )

    products = list_products_service(
        db=db,
        search=None,
        category_id=None,
        min_price=400,
        max_price=800,
        sort=None,
        page=1,
        limit=10,
    )

    assert len(products) == 1
    assert products[0].name == "Medium"

def test_list_products_sort_price_ascending(db):
    category = create_category(db)

    create_product(
        db,
        category.id,
        name="Expensive",
        price=1000,
    )

    create_product(
        db,
        category.id,
        name="Cheap",
        price=100,
    )

    products = list_products_service(
        db=db,
        search=None,
        category_id=None,
        min_price=None,
        max_price=None,
        sort="price",
        page=1,
        limit=10,
    )

    assert products[0].name == "Cheap"
    assert products[1].name == "Expensive"

def test_get_product_service(db):
    category = create_category(db)

    product = create_product(
        db,
        category.id,
        name="Laptop",
        price=1000,
    )

    result = get_product_service(
        db=db,
        product_id=product.id,
    )

    assert result.id == product.id
    assert result.name == "Laptop"
    assert result.category.id == category.id
    assert result.review_count == 0

def test_get_product_service_missing_product(db):
    try:
        get_product_service(
            db=db,
            product_id=9999,
        )
        assert False
    except ValueError as e:
        assert str(e) == "Product not found"

def test_create_product_service(db):
    category = create_category(db)

    product_data = ProductCreate(
        name="Laptop",
        description="Gaming laptop",
        price=1500,
        stock=20,
        category_id=category.id,
    )

    product = create_product_service(
        db=db,
        product_data=product_data,
    )

    assert product.id is not None
    assert product.name == "Laptop"
    assert product.price == 1500
    assert product.stock == 20
    assert product.category_id == category.id

def test_create_product_service_missing_category(db):
    product_data = ProductCreate(
        name="Laptop",
        description="Gaming laptop",
        price=1500,
        stock=20,
        category_id=9999,
    )

    try:
        create_product_service(
            db=db,
            product_data=product_data,
        )
        assert False
    except ValueError as e:
        assert str(e) == "Category not found"

def test_update_product_service(db):
    category = create_category(db)

    product = create_product(
        db,
        category.id,
        name="Old Laptop",
        price=1000,
        stock=10,
    )

    product_data = ProductCreate(
        name="New Laptop",
        description="Updated laptop",
        price=1200,
        stock=15,
        category_id=category.id,
    )

    updated = update_product_service(
        db=db,
        product_id=product.id,
        product_data=product_data,
        admin_id=1,
    )

    assert updated.name == "New Laptop"
    assert updated.description == "Updated laptop"
    assert updated.price == 1200
    assert updated.stock == 15
    assert updated.category_id == category.id

def test_update_product_service_creates_inventory_log(db):
    category = create_category(db)

    product = create_product(
        db,
        category.id,
        name="Laptop",
        price=1000,
        stock=10,
    )

    product_data = ProductCreate(
        name="Laptop",
        description="Updated laptop",
        price=1000,
        stock=20,
        category_id=category.id,
    )

    update_product_service(
        db=db,
        product_id=product.id,
        product_data=product_data,
        admin_id=1,
    )

    log = (
        db.query(InventoryLog)
        .filter(
            InventoryLog.product_id == product.id
        )
        .first()
    )

    assert log is not None
    assert log.old_stock == 10
    assert log.new_stock == 20
    assert log.change_type == "admin_update"
    assert log.changed_by == 1

def test_update_product_service_does_not_create_log_when_stock_unchanged(db):
    category = create_category(db)

    product = create_product(
        db,
        category.id,
        name="Laptop",
        price=1000,
        stock=10,
    )

    product_data = ProductCreate(
        name="Updated Laptop",
        description="Updated description",
        price=1100,
        stock=10,
        category_id=category.id,
    )

    update_product_service(
        db=db,
        product_id=product.id,
        product_data=product_data,
        admin_id=1,
    )

    logs = (
        db.query(InventoryLog)
        .filter(
            InventoryLog.product_id == product.id
        )
        .all()
    )

    assert len(logs) == 0

def test_update_product_service_missing_product(db):
    category = create_category(db)

    product_data = ProductCreate(
        name="Laptop",
        description="Laptop",
        price=1000,
        stock=10,
        category_id=category.id,
    )

    try:
        update_product_service(
            db=db,
            product_id=9999,
            product_data=product_data,
            admin_id=1,
        )
        assert False
    except ValueError as e:
        assert str(e) == "Product not found"

def test_update_product_service_missing_category(db):
    category = create_category(db)

    product = create_product(
        db,
        category.id,
        name="Laptop",
    )

    product_data = ProductCreate(
        name="Updated Laptop",
        description="Updated",
        price=1200,
        stock=20,
        category_id=9999,
    )

    try:
        update_product_service(
            db=db,
            product_id=product.id,
            product_data=product_data,
            admin_id=1,
        )
        assert False
    except ValueError as e:
        assert str(e) == "Category not found"

def test_delete_product_service(db):
    category = create_category(db)

    product = create_product(
        db,
        category.id,
        name="Laptop",
    )

    deleted = delete_product_service(
        db=db,
        product_id=product.id,
    )

    assert deleted.is_deleted is True

def test_delete_product_service_missing_product(db):
    try:
        delete_product_service(
            db=db,
            product_id=9999,
        )
        assert False
    except ValueError as e:
        assert str(e) == "Product not found"

def test_delete_product_service_already_deleted(db):
    category = create_category(db)

    product = create_product(
        db,
        category.id,
    )

    product.is_deleted = True
    db.commit()

    try:
        delete_product_service(
            db=db,
            product_id=product.id,
        )
        assert False
    except ValueError as e:
        assert str(e) == "Product already deleted"

def test_restore_product_service(db):
    category = create_category(db)

    product = create_product(
        db,
        category.id,
    )

    product.is_deleted = True
    db.commit()

    restored = restore_product_service(
        db=db,
        product_id=product.id,
    )

    assert restored.is_deleted is False

def test_restore_product_service_already_active(db):
    category = create_category(db)

    product = create_product(
        db,
        category.id,
    )

    try:
        restore_product_service(
            db=db,
            product_id=product.id,
        )
        assert False
    except ValueError as e:
        assert str(e) == "Product is already active"