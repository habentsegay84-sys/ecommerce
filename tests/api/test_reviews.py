from app.models.category import Category
from app.models.product import Product
from app.models.review import Review
from app.models.user import User

from app.core.security import hash_password
from tests.utils.auth import get_auth_headers

def test_create_review_requires_auth(
    client,
    db,
):
    """
    Verify that creating a product review requires authentication.

    Unauthenticated clients must receive HTTP 401 instead of
    being allowed to create a review.
    """

    response = client.post(
        "/reviews/products/1",
        json={
            "rating": 5,
            "comment": "Excellent product",
        },
    )

    assert response.status_code == 401

def test_create_review_success(
    client,
    db,
):
    """
    Verify that an authenticated user can successfully
    create a review for an existing product.
    """

    # Create a category required by the product.
    category = Category(
        name="Electronics",
    )

    db.add(category)
    db.commit()
    db.refresh(category)

    # Create the product that will receive the review.
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

    # Register and authenticate a dedicated test user.
    headers = get_auth_headers(
        client,
        username="reviewuser",
        email="reviewuser@example.com",
        password="password123",
    )

    response = client.post(
        f"/reviews/products/{product.id}",
        headers=headers,
        json={
            "rating": 5,
            "comment": "Excellent product",
        },
    )

    assert response.status_code == 200

    data = response.json()

    # Verify the review data returned by the API.
    assert data["rating"] == 5
    assert data["comment"] == "Excellent product"
    assert data["product_id"] == product.id

    # The API should generate these fields automatically.
    assert "id" in data
    assert "user_id" in data
    assert "created_at" in data

def test_create_review_rejects_duplicate_review(
    client,
    db,
):
    """
    Verify that a user cannot submit more than one
    review for the same product.
    """

    # Create a category required by the product.
    category = Category(
        name="Electronics",
    )

    db.add(category)
    db.commit()
    db.refresh(category)

    # Create the product that will be reviewed.
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

    # Register and authenticate the review user.
    headers = get_auth_headers(
        client,
        username="reviewuser",
        email="reviewuser@example.com",
        password="password123",
    )

    # Create the first review.
    first_response = client.post(
        f"/reviews/products/{product.id}",
        headers=headers,
        json={
            "rating": 5,
            "comment": "Excellent product",
        },
    )

    assert first_response.status_code == 200

    # Attempt to submit another review for the same product
    # using the same authenticated user.
    second_response = client.post(
        f"/reviews/products/{product.id}",
        headers=headers,
        json={
            "rating": 3,
            "comment": "Trying to review again",
        },
    )

    assert second_response.status_code == 400

    data = second_response.json()

    assert data["detail"] == (
        "You have already reviewed this product."
    )

def test_create_review_product_not_found(
    client,
):
    """
    Verify that creating a review for a non-existent
    product returns HTTP 404.
    """

    headers = get_auth_headers(
        client,
        username="missingproductuser",
        email="missingproduct@example.com",
    )

    response = client.post(
        "/reviews/products/99999",
        headers=headers,
        json={
            "rating": 5,
            "comment": "This product does not exist.",
        },
    )

    assert response.status_code == 404

    data = response.json()

    assert data["detail"] == "Product not found."

def test_list_reviews_success(
    client,
    db,
):
    """
    Verify that users can retrieve all reviews
    associated with an existing product.
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

    user = User(
        username="reviewuser",
        email="reviewuser@example.com",
        hashed_password=hash_password("password123"),
    )

    db.add(user)
    db.commit()
    db.refresh(user)

    review = Review(
        rating=5,
        comment="Excellent product.",
        user_id=user.id,
        product_id=product.id,
    )

    db.add(review)
    db.commit()
    db.refresh(review)

    response = client.get(
        f"/reviews/products/{product.id}",
    )

    assert response.status_code == 200

    data = response.json()

    assert len(data) == 1
    assert data[0]["rating"] == 5
    assert data[0]["comment"] == "Excellent product."
    assert data[0]["product_id"] == product.id
    assert data[0]["user_id"] == user.id


def test_list_reviews_product_not_found(
    client,
):
    """
    Verify that requesting reviews for a non-existent
    product returns a not-found response.
    """

    response = client.get(
        "/reviews/products/99999",
    )

    assert response.status_code == 404

    data = response.json()

    assert data["detail"] == "Product not found."

def test_update_review_success(
    client,
    db,
):
    """
    Verify that an authenticated user can update
    their own review.
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

    headers = get_auth_headers(
        client,
        username="reviewuser",
        email="reviewuser@example.com",
    )

    response = client.post(
        f"/reviews/products/{product.id}",
        json={
            "rating": 3,
            "comment": "It is okay.",
        },
        headers=headers,
    )

    assert response.status_code == 200

    review_id = response.json()["id"]

    response = client.patch(
        f"/reviews/{review_id}",
        json={
            "rating": 5,
            "comment": "Excellent product!",
        },
        headers=headers,
    )

    assert response.status_code == 200

    data = response.json()

    assert data["id"] == review_id
    assert data["rating"] == 5
    assert data["comment"] == "Excellent product!"

def test_update_review_rejects_other_users_review(
    client,
    db,
):
    """
    Verify that a user cannot modify another user's review.

    This protects reviews from unauthorized modification.
    """

    # Create the category required by the product.
    category = Category(
        name="Electronics",
    )

    db.add(category)
    db.commit()
    db.refresh(category)

    # Create the product being reviewed.
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

    # Authenticate the original reviewer.
    owner_headers = get_auth_headers(
        client,
        username="reviewowner",
        email="reviewowner@example.com",
    )

    # Create the original review.
    create_response = client.post(
        f"/reviews/products/{product.id}",
        headers=owner_headers,
        json={
            "rating": 4,
            "comment": "Good product.",
        },
    )

    assert create_response.status_code == 200

    review_id = create_response.json()["id"]

    # Authenticate a different user.
    other_user_headers = get_auth_headers(
        client,
        username="anotherreviewer",
        email="anotherreviewer@example.com",
    )

    # Attempt to modify the owner's review.
    response = client.patch(
        f"/reviews/{review_id}",
        headers=other_user_headers,
        json={
            "rating": 1,
            "comment": "Unauthorized modification.",
        },
    )

    assert response.status_code == 403

    data = response.json()

    assert data["detail"] == (
        "You can only update your own review."
    )

def test_update_review_not_found(
    client,
    db,
):
    """
    Verify that updating a non-existent review returns
    HTTP 404 instead of exposing a service-layer exception.
    """

    headers = get_auth_headers(
        client,
        username="reviewuser",
        email="reviewuser@example.com",
    )

    response = client.patch(
        "/reviews/99999",
        headers=headers,
        json={
            "rating": 5,
            "comment": "Updated review.",
        },
    )

    assert response.status_code == 404

    data = response.json()

    assert data["detail"] == "Review not found."

def test_update_review_partial_update(
    client,
    db,
):
    """
    Verify that updating only one review field preserves
    the other existing fields.
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

    headers = get_auth_headers(
        client,
        username="partialuser",
        email="partialuser@example.com",
    )

    # Create the initial review.
    create_response = client.post(
        f"/reviews/products/{product.id}",
        headers=headers,
        json={
            "rating": 3,
            "comment": "Original comment.",
        },
    )

    assert create_response.status_code == 200

    review_id = create_response.json()["id"]

    # Update only the rating.
    update_response = client.patch(
        f"/reviews/{review_id}",
        headers=headers,
        json={
            "rating": 5,
        },
    )

    assert update_response.status_code == 200

    data = update_response.json()

    assert data["rating"] == 5

    # The original comment must remain unchanged.
    assert data["comment"] == "Original comment."

def test_delete_review_success(
    client,
    db,
):
    """
    Verify that an authenticated user can delete
    their own review.
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

    headers = get_auth_headers(
        client,
        username="deleteuser",
        email="deleteuser@example.com",
    )

    # Create the review that will be deleted.
    create_response = client.post(
        f"/reviews/products/{product.id}",
        headers=headers,
        json={
            "rating": 5,
            "comment": "Great product.",
        },
    )

    assert create_response.status_code == 200

    review_id = create_response.json()["id"]

    # Delete the review.
    delete_response = client.delete(
        f"/reviews/{review_id}",
        headers=headers,
    )

    assert delete_response.status_code == 200

    data = delete_response.json()

    assert data["message"] == "Review deleted successfully."

    # Verify that the review no longer exists.
    get_response = client.get(
        f"/reviews/products/{product.id}",
    )

    assert get_response.status_code == 200
    assert get_response.json() == []

def test_delete_review_not_found(
    client,
):
    """
    Verify that deleting a non-existent review
    returns HTTP 404.
    """

    headers = get_auth_headers(
        client,
        username="deleteuser",
        email="deleteuser@example.com",
    )

    response = client.delete(
        "/reviews/99999",
        headers=headers,
    )

    assert response.status_code == 404

    data = response.json()

    assert data["detail"] == "Review not found."

def test_delete_review_rejects_other_users_review(
    client,
    db,
):
    """
    Verify that a user cannot delete another user's review.
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

    # Authenticate the review owner.
    owner_headers = get_auth_headers(
        client,
        username="reviewowner",
        email="reviewowner@example.com",
    )

    create_response = client.post(
        f"/reviews/products/{product.id}",
        headers=owner_headers,
        json={
            "rating": 5,
            "comment": "Great product.",
        },
    )

    assert create_response.status_code == 200

    review_id = create_response.json()["id"]

    # Authenticate a different user.
    other_user_headers = get_auth_headers(
        client,
        username="anotheruser",
        email="anotheruser@example.com",
    )

    # Attempt to delete the owner's review.
    response = client.delete(
        f"/reviews/{review_id}",
        headers=other_user_headers,
    )

    assert response.status_code == 403

    data = response.json()

    assert data["detail"] == (
        "You can only delete your own review."
    )