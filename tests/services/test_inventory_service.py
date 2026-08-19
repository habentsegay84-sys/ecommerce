import pytest

from app.models.product import Product
from app.models.category import Category
from app.models.inventory import InventoryLog
from app.services.inventory_service import (
    update_stock_service,
    list_inventory_logs_service,
)


def create_product(db, stock=10):
    category = Category(
        name="Electronics",
    )

    db.add(category)
    db.commit()
    db.refresh(category)

    product = Product(
        name="Test Laptop",
        price=1000.00,
        stock=stock,
        category_id=category.id,
    )

    db.add(product)
    db.commit()
    db.refresh(product)

    return product


def test_update_stock_service_updates_stock(
    db,
    admin_user,
):
    product = create_product(
        db,
        stock=10,
    )

    updated_product = update_stock_service(
        db=db,
        product_id=product.id,
        new_stock=25,
        admin_id=admin_user.id,
    )

    assert updated_product.stock == 25


def test_update_stock_service_creates_inventory_log(
    db,
    admin_user,
):
    product = create_product(
        db,
        stock=10,
    )

    update_stock_service(
        db=db,
        product_id=product.id,
        new_stock=25,
        admin_id=admin_user.id,
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
    assert log.new_stock == 25
    assert log.change_type == "admin_update"
    assert log.changed_by == admin_user.id


def test_update_stock_service_rejects_missing_product(
    db,
    admin_user,
):
    with pytest.raises(ValueError, match="Product not found"):
        update_stock_service(
            db=db,
            product_id=9999,
            new_stock=20,
            admin_id=admin_user.id,
        )


def test_update_stock_service_rejects_negative_stock(
    db,
    admin_user,
):
    product = create_product(
        db,
        stock=10,
    )

    with pytest.raises(
        ValueError,
        match="Stock cannot be negative",
    ):
        update_stock_service(
            db=db,
            product_id=product.id,
            new_stock=-1,
            admin_id=admin_user.id,
        )


def test_update_stock_service_rejects_same_stock(
    db,
    admin_user,
):
    product = create_product(
        db,
        stock=10,
    )

    with pytest.raises(
        ValueError,
        match="Stock is already this value",
    ):
        update_stock_service(
            db=db,
            product_id=product.id,
            new_stock=10,
            admin_id=admin_user.id,
        )


def test_list_inventory_logs_service(
    db,
    admin_user,
):
    product = create_product(
        db,
        stock=10,
    )

    update_stock_service(
        db=db,
        product_id=product.id,
        new_stock=25,
        admin_id=admin_user.id,
    )

    response = list_inventory_logs_service(db)

    assert len(response) == 1

    log = response[0]

    assert log.product_id == product.id
    assert log.product_name == "Test Laptop"
    assert log.old_stock == 10
    assert log.new_stock == 25
    assert log.change_type == "admin_update"
    assert log.changed_by == admin_user.id