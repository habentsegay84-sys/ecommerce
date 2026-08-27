import pytest

from app.models.review import Review
from app.models.product import Product
from app.models.category import Category
from app.models.user import User

from app.schemas.review import (
    ReviewCreate,
    ReviewUpdate,
)

from app.services.review_service import (
    create_review_service,
    list_product_reviews_service,
    update_review_service,
    delete_review_service,
)


# ============================================================
# Helpers
# ============================================================

def create_category(db):
    """
    Create a category required by the product relationship.
    """

    category = Category(
        name="Electronics",
    )

    db.add(category)
    db.commit()
    db.refresh(category)

    return category


def create_product(db, category):
    """
    Create a product used by review service tests.
    """

    product = Product(
        name="Laptop",
        description="Test laptop",
        price=1200,
        stock=10,
        category_id=category.id,
    )

    db.add(product)
    db.commit()
    db.refresh(product)

    return product


def create_review(
    db,
    product,
    user,
    rating=5,
    comment="Excellent product",
):
    """
    Create a review directly in the test database.
    """

    review = Review(
        rating=rating,
        comment=comment,
        product_id=product.id,
        user_id=user.id,
    )

    db.add(review)
    db.commit()
    db.refresh(review)

    return review


# ============================================================
# create_review_service
# ============================================================

def test_create_review_service_success(
    db,
    test_user,
):
    """
    Verify that an authenticated user can create
    a review for an existing product.
    """

    category = create_category(db)
    product = create_product(db, category)

    review_data = ReviewCreate(
        rating=5,
        comment="Excellent product",
    )

    review = create_review_service(
        db=db,
        product_id=product.id,
        review_data=review_data,
        current_user=test_user,
    )

    assert review.id is not None
    assert review.product_id == product.id
    assert review.user_id == test_user.id
    assert review.rating == 5
    assert review.comment == "Excellent product"


def test_create_review_service_product_not_found(
    db,
    test_user,
):
    """
    Verify that creating a review for a nonexistent
    product raises the expected validation error.
    """

    review_data = ReviewCreate(
        rating=5,
        comment="Excellent product",
    )

    with pytest.raises(
        ValueError,
        match="Product not found.",
    ):
        create_review_service(
            db=db,
            product_id=99999,
            review_data=review_data,
            current_user=test_user,
        )


def test_create_review_service_prevents_duplicate_review(
    db,
    test_user,
):
    """
    Verify that a user cannot submit more than one
    review for the same product.
    """

    category = create_category(db)
    product = create_product(db, category)

    create_review(
        db=db,
        product=product,
        user=test_user,
    )

    review_data = ReviewCreate(
        rating=4,
        comment="Second review",
    )

    with pytest.raises(
        ValueError,
        match="You have already reviewed this product.",
    ):
        create_review_service(
            db=db,
            product_id=product.id,
            review_data=review_data,
            current_user=test_user,
        )


# ============================================================
# list_product_reviews_service
# ============================================================

def test_list_product_reviews_service_success(
    db,
    test_user,
    another_user,
):
    """
    Verify that all reviews for an existing product
    are returned.
    """

    category = create_category(db)
    product = create_product(db, category)

    create_review(
        db=db,
        product=product,
        user=test_user,
        rating=5,
        comment="Excellent",
    )

    create_review(
        db=db,
        product=product,
        user=another_user,
        rating=4,
        comment="Very good",
    )

    reviews = list_product_reviews_service(
        db=db,
        product_id=product.id,
    )

    assert len(reviews) == 2

    ratings = {
        review.rating
        for review in reviews
    }

    assert ratings == {4, 5}


def test_list_product_reviews_service_product_not_found(
    db,
):
    """
    Verify that requesting reviews for a nonexistent
    product raises the expected validation error.
    """

    with pytest.raises(
        ValueError,
        match="Product not found.",
    ):
        list_product_reviews_service(
            db=db,
            product_id=99999,
        )


def test_list_product_reviews_service_empty(
    db,
):
    """
    Verify that an existing product with no reviews
    returns an empty list.
    """

    category = create_category(db)
    product = create_product(db, category)

    reviews = list_product_reviews_service(
        db=db,
        product_id=product.id,
    )

    assert reviews == []


# ============================================================
# update_review_service
# ============================================================

def test_update_review_service_success(
    db,
    test_user,
):
    """
    Verify that a user can update their own review.
    """

    category = create_category(db)
    product = create_product(db, category)

    review = create_review(
        db=db,
        product=product,
        user=test_user,
        rating=3,
        comment="It is okay",
    )

    update_data = ReviewUpdate(
        rating=5,
        comment="Actually excellent",
    )

    updated_review = update_review_service(
        db=db,
        review_id=review.id,
        review_data=update_data,
        current_user=test_user,
    )

    assert updated_review.rating == 5
    assert updated_review.comment == "Actually excellent"


def test_update_review_service_partial_update(
    db,
    test_user,
):
    """
    Verify that only supplied fields are changed
    during a partial review update.
    """

    category = create_category(db)
    product = create_product(db, category)

    review = create_review(
        db=db,
        product=product,
        user=test_user,
        rating=3,
        comment="Original comment",
    )

    update_data = ReviewUpdate(
        rating=5,
    )

    updated_review = update_review_service(
        db=db,
        review_id=review.id,
        review_data=update_data,
        current_user=test_user,
    )

    assert updated_review.rating == 5
    assert updated_review.comment == "Original comment"


def test_update_review_service_review_not_found(
    db,
    test_user,
):
    """
    Verify that updating a nonexistent review
    raises the expected validation error.
    """

    update_data = ReviewUpdate(
        rating=5,
    )

    with pytest.raises(
        ValueError,
        match="Review not found.",
    ):
        update_review_service(
            db=db,
            review_id=99999,
            review_data=update_data,
            current_user=test_user,
        )


def test_update_review_service_rejects_other_users_review(
    db,
    test_user,
    another_user,
):
    """
    Verify that a user cannot modify another user's review.
    """

    category = create_category(db)
    product = create_product(db, category)

    review = create_review(
        db=db,
        product=product,
        user=another_user,
    )

    update_data = ReviewUpdate(
        rating=1,
        comment="Unauthorized change",
    )

    with pytest.raises(
        ValueError,
        match="You can only update your own review.",
    ):
        update_review_service(
            db=db,
            review_id=review.id,
            review_data=update_data,
            current_user=test_user,
        )


# ============================================================
# delete_review_service
# ============================================================

def test_delete_review_service_success(
    db,
    test_user,
):
    """
    Verify that a user can delete their own review.
    """

    category = create_category(db)
    product = create_product(db, category)

    review = create_review(
        db=db,
        product=product,
        user=test_user,
    )

    result = delete_review_service(
        db=db,
        review_id=review.id,
        current_user=test_user,
    )

    assert result == {
        "message": "Review deleted successfully."
    }

    deleted_review = (
        db.query(Review)
        .filter(Review.id == review.id)
        .first()
    )

    assert deleted_review is None


def test_delete_review_service_review_not_found(
    db,
    test_user,
):
    """
    Verify that deleting a nonexistent review
    raises the expected validation error.
    """

    with pytest.raises(
        ValueError,
        match="Review not found.",
    ):
        delete_review_service(
            db=db,
            review_id=99999,
            current_user=test_user,
        )


def test_delete_review_service_rejects_other_users_review(
    db,
    test_user,
    another_user,
):
    """
    Verify that a user cannot delete another user's review.
    """

    category = create_category(db)
    product = create_product(db, category)

    review = create_review(
        db=db,
        product=product,
        user=another_user,
    )

    with pytest.raises(
        ValueError,
        match="You can only delete your own review.",
    ):
        delete_review_service(
            db=db,
            review_id=review.id,
            current_user=test_user,
        )

    # The original review must still exist.
    remaining_review = (
        db.query(Review)
        .filter(Review.id == review.id)
        .first()
    )

    assert remaining_review is not None