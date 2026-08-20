from tests.utils.auth import get_auth_headers, get_admin_auth_headers

from app.models.category import Category
from app.models.product import Product
from app.models.inventory import InventoryLog

from decimal import Decimal


def test_list_admin_products_requires_auth(client):
    """
    Verify that the admin product endpoint rejects
    requests that do not contain authentication credentials.
    """

    response = client.get("/admin/products")

    assert response.status_code == 401


def test_normal_user_cannot_list_admin_products(
    client,
    test_user,
):
    """
    Verify that a regular authenticated user cannot
    access administrator-only product management endpoints.
    """

    headers = get_auth_headers(
        client,
        username="normaluser",
        email="normal@example.com",
    )

    response = client.get(
        "/admin/products",
        headers=headers,
    )

    assert response.status_code == 403


def test_normal_user_cannot_create_product(
    client,
    test_user,
):
    """
    Verify that product creation is restricted to
    users with administrator privileges.
    """

    headers = get_auth_headers(
        client,
        username="normaluser2",
        email="normal2@example.com",
    )

    response = client.post(
        "/admin/products",
        headers=headers,
        json={
            "name": "Test Laptop",
            "description": "Test product",
            "price": 1000,
            "stock": 10,
            "category_id": 1,
        },
    )

    assert response.status_code == 403

def test_admin_can_list_products(
    client,
    db,
    admin_user,
):
    """
    Verify that an administrator can retrieve products
    through the admin product management endpoint.
    """

    category = Category(
        name="Electronics",
    )

    db.add(category)
    db.commit()
    db.refresh(category)

    product = Product(
        name="Laptop",
        description="Professional laptop",
        price=1200,
        stock=10,
        category_id=category.id,
    )

    db.add(product)
    db.commit()
    db.refresh(product)

    headers = get_admin_auth_headers(
        client,
        db,
    )

    response = client.get(
        "/admin/products",
        headers=headers,
    )

    assert response.status_code == 200

    data = response.json()

    assert len(data) == 1
    assert data[0]["name"] == "Laptop"
    assert Decimal(data[0]["price"]) == Decimal("1200.0")
    assert data[0]["stock"] == 10

def test_admin_can_filter_active_products(
    client,
    db,
    admin_user,
):
    """
    Verify that the active-product filter excludes
    products that have been soft deleted.
    """

    category = Category(
        name="Electronics",
    )

    db.add(category)
    db.commit()
    db.refresh(category)

    active_product = Product(
        name="Active Laptop",
        description="Available product",
        price=1000,
        stock=5,
        category_id=category.id,
        is_deleted=False,
    )

    deleted_product = Product(
        name="Deleted Laptop",
        description="Removed product",
        price=900,
        stock=3,
        category_id=category.id,
        is_deleted=True,
    )

    db.add_all([
        active_product,
        deleted_product,
    ])

    db.commit()

    headers = get_admin_auth_headers(
        client,
        db,
    )

    response = client.get(
        "/admin/products?status=active",
        headers=headers,
    )

    assert response.status_code == 200

    data = response.json()

    assert len(data) == 1
    assert data[0]["name"] == "Active Laptop"

def test_admin_can_filter_deleted_products(
    client,
    db,
    admin_user,
):
    """
    Verify that the deleted-product filter returns only
    products that have been soft deleted.
    """

    category = Category(
        name="Electronics",
    )

    db.add(category)
    db.commit()
    db.refresh(category)

    active_product = Product(
        name="Active Phone",
        description="Available product",
        price=500,
        stock=10,
        category_id=category.id,
        is_deleted=False,
    )

    deleted_product = Product(
        name="Deleted Phone",
        description="Removed product",
        price=400,
        stock=2,
        category_id=category.id,
        is_deleted=True,
    )

    db.add_all([
        active_product,
        deleted_product,
    ])

    db.commit()

    headers = get_admin_auth_headers(
        client,
        db,
    )

    response = client.get(
        "/admin/products?status=deleted",
        headers=headers,
    )

    assert response.status_code == 200

    data = response.json()

    assert len(data) == 1
    assert data[0]["name"] == "Deleted Phone"

def test_admin_can_create_product(
    client,
    db,
    admin_user,
):
    """
    Verify that an administrator can create a product
    associated with an existing category.
    """

    category = Category(
        name="Electronics",
    )

    db.add(category)
    db.commit()
    db.refresh(category)

    headers = get_admin_auth_headers(
        client,
        db,
    )

    response = client.post(
        "/admin/products",
        headers=headers,
        json={
            "name": "Professional Laptop",
            "description": "High-performance laptop",
            "price": "1500.00",
            "stock": 20,
            "category_id": category.id,
        },
    )

    assert response.status_code == 201

    data = response.json()

    assert data["name"] == "Professional Laptop"
    assert data["description"] == "High-performance laptop"
    assert Decimal(data["price"]) == Decimal("1500.00")
    assert data["stock"] == 20
    assert data["category"]["id"] == category.id

    # Verify persistence at the database level.
    product = (
        db.query(Product)
        .filter(Product.name == "Professional Laptop")
        .first()
    )

    assert product is not None
    assert product.category_id == category.id

def test_admin_create_product_with_missing_category(
    client,
    db,
    admin_user,
):
    """
    Verify that product creation fails when the referenced
    category does not exist.
    """

    headers = get_admin_auth_headers(
        client,
        db,
    )

    response = client.post(
        "/admin/products",
        headers=headers,
        json={
            "name": "Invalid Product",
            "description": "Product with invalid category",
            "price": "500.00",
            "stock": 10,
            "category_id": 9999,
        },
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Category not found"

def test_admin_can_update_product(
    client,
    db,
    admin_user,
):
    """
    Verify that an administrator can update an existing
    product and persist the modified product data.
    """

    category = Category(
        name="Electronics",
    )

    db.add(category)
    db.commit()
    db.refresh(category)

    product = Product(
        name="Old Laptop",
        description="Old description",
        price=Decimal("1000.00"),
        stock=10,
        category_id=category.id,
    )

    db.add(product)
    db.commit()
    db.refresh(product)

    headers = get_admin_auth_headers(
        client,
        db,
    )

    response = client.patch(
        f"/admin/products/{product.id}",
        headers=headers,
        json={
            "name": "Updated Laptop",
            "description": "Updated description",
            "price": "1250.00",
            "stock": 15,
            "category_id": category.id,
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["name"] == "Updated Laptop"
    assert data["description"] == "Updated description"
    assert Decimal(data["price"]) == Decimal("1250.00")
    assert data["stock"] == 15
    assert data["category"]["id"] == category.id

    # Verify that the updated values were persisted.
    db.refresh(product)

    assert product.name == "Updated Laptop"
    assert product.stock == 15

def test_admin_update_product_creates_inventory_log(
    client,
    db,
    admin_user,
):
    """
    Verify that changing product stock through the admin
    API creates an inventory history record containing
    the previous and updated stock values.
    """

    category = Category(
        name="Electronics",
    )

    db.add(category)
    db.commit()
    db.refresh(category)

    product = Product(
        name="Inventory Laptop",
        description="Laptop for inventory testing",
        price=Decimal("1000.00"),
        stock=10,
        category_id=category.id,
    )

    db.add(product)
    db.commit()
    db.refresh(product)

    headers = get_admin_auth_headers(
        client,
        db,
    )

    response = client.patch(
        f"/admin/products/{product.id}",
        headers=headers,
        json={
            "name": "Inventory Laptop",
            "description": "Laptop for inventory testing",
            "price": "1000.00",
            "stock": 25,
            "category_id": category.id,
        },
    )

    assert response.status_code == 200

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

def test_admin_update_missing_product(
    client,
    db,
    admin_user,
):
    """
    Verify that updating a product that does not exist
    returns a 404 response.
    """

    category = Category(
        name="Electronics",
    )

    db.add(category)
    db.commit()
    db.refresh(category)

    headers = get_admin_auth_headers(
        client,
        db,
    )

    response = client.patch(
        "/admin/products/9999",
        headers=headers,
        json={
            "name": "Missing Product",
            "description": "This product does not exist",
            "price": "500.00",
            "stock": 10,
            "category_id": category.id,
        },
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Product not found"


def test_admin_update_product_with_missing_category(
    client,
    db,
    admin_user,
):
    """
    Verify that updating a product with an invalid category
    returns a validation error without modifying the product.
    """

    category = Category(
        name="Electronics",
    )

    db.add(category)
    db.commit()
    db.refresh(category)

    product = Product(
        name="Existing Laptop",
        description="Existing product",
        price=Decimal("1000.00"),
        stock=10,
        category_id=category.id,
    )

    db.add(product)
    db.commit()
    db.refresh(product)

    headers = get_admin_auth_headers(
        client,
        db,
    )

    response = client.patch(
        f"/admin/products/{product.id}",
        headers=headers,
        json={
            "name": "Updated Laptop",
            "description": "Updated description",
            "price": "1200.00",
            "stock": 20,
            "category_id": 9999,
        },
    )

    assert response.status_code == 400
    assert response.json()["detail"] == "Category not found"

    # Verify that the failed validation did not modify
    # the existing product.
    db.refresh(product)

    assert product.name == "Existing Laptop"
    assert product.stock == 10
    assert product.category_id == category.id

def test_admin_can_delete_product(
    client,
    db,
    admin_user,
):
    """
    Verify that an administrator can soft-delete a product
    without physically removing its database record.
    """

    category = Category(
        name="Electronics",
    )

    db.add(category)
    db.commit()
    db.refresh(category)

    product = Product(
        name="Delete Laptop",
        description="Product to be deleted",
        price=Decimal("1000.00"),
        stock=10,
        category_id=category.id,
    )

    db.add(product)
    db.commit()
    db.refresh(product)

    headers = get_admin_auth_headers(
        client,
        db,
    )

    response = client.delete(
        f"/admin/products/{product.id}",
        headers=headers,
    )

    assert response.status_code == 204

    # The product should remain in the database but be marked
    # as deleted rather than physically removed.
    db.refresh(product)

    assert product.is_deleted is True

    stored_product = (
        db.query(Product)
        .filter(Product.id == product.id)
        .first()
    )

    assert stored_product is not None


def test_admin_delete_missing_product(
    client,
    db,
    admin_user,
):
    """
    Verify that deleting a nonexistent product returns 404.
    """

    headers = get_admin_auth_headers(
        client,
        db,
    )

    response = client.delete(
        "/admin/products/9999",
        headers=headers,
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Product not found"


def test_admin_cannot_delete_already_deleted_product(
    client,
    db,
    admin_user,
):
    """
    Verify that attempting to delete an already deleted
    product returns a business validation error.
    """

    category = Category(
        name="Electronics",
    )

    db.add(category)
    db.commit()
    db.refresh(category)

    product = Product(
        name="Already Deleted Laptop",
        description="Deleted product",
        price=Decimal("1000.00"),
        stock=5,
        category_id=category.id,
        is_deleted=True,
    )

    db.add(product)
    db.commit()
    db.refresh(product)

    headers = get_admin_auth_headers(
        client,
        db,
    )

    response = client.delete(
        f"/admin/products/{product.id}",
        headers=headers,
    )

    assert response.status_code == 400
    assert response.json()["detail"] == "Product already deleted"

def test_admin_can_restore_deleted_product(
    client,
    db,
    admin_user,
):
    """
    Verify that an administrator can restore a soft-deleted
    product and make it active again.
    """

    category = Category(
        name="Electronics",
    )

    db.add(category)
    db.commit()
    db.refresh(category)

    product = Product(
        name="Restore Laptop",
        description="Deleted laptop",
        price=Decimal("1000.00"),
        stock=5,
        category_id=category.id,
        is_deleted=True,
    )

    db.add(product)
    db.commit()
    db.refresh(product)

    headers = get_admin_auth_headers(
        client,
        db,
    )

    response = client.patch(
        f"/admin/products/{product.id}/restore",
        headers=headers,
    )

    assert response.status_code == 200

    data = response.json()

    assert data["id"] == product.id
    assert data["name"] == "Restore Laptop"

    db.refresh(product)

    assert product.is_deleted is False


def test_admin_restore_missing_product(
    client,
    db,
    admin_user,
):
    """
    Verify that restoring a nonexistent product returns 404.
    """

    headers = get_admin_auth_headers(
        client,
        db,
    )

    response = client.patch(
        "/admin/products/9999/restore",
        headers=headers,
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Product not found"


def test_admin_cannot_restore_active_product(
    client,
    db,
    admin_user,
):
    """
    Verify that restoring an already active product returns
    a business validation error.
    """

    category = Category(
        name="Electronics",
    )

    db.add(category)
    db.commit()
    db.refresh(category)

    product = Product(
        name="Active Laptop",
        description="Active product",
        price=Decimal("1000.00"),
        stock=5,
        category_id=category.id,
        is_deleted=False,
    )

    db.add(product)
    db.commit()
    db.refresh(product)

    headers = get_admin_auth_headers(
        client,
        db,
    )

    response = client.patch(
        f"/admin/products/{product.id}/restore",
        headers=headers,
    )

    assert response.status_code == 400
    assert response.json()["detail"] == "Product is already active"