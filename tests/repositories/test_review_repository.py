import pytest

from app.models.review import Review
from app.models.product import Product
from app.models.category import Category

from app.repositories.review_repository import ReviewRepository


# ============================================================
# Test helpers
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
    Create a product used by repository tests.
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
# create()
# ============================================================

def test_create_review(db, test_user):
    """
    Verify that the repository persists a new review.
    """

    category = create_category(db)
    product = create_product(db, category)

    repository = ReviewRepository(db)

    review = Review(
        rating=5,
        comment="Excellent",
        product_id=product.id,
        user_id=test_user.id,
    )

    result = repository.create(review)

    assert result.id is not None
    assert result.rating == 5
    assert result.comment == "Excellent"
    assert result.product_id == product.id
    assert result.user_id == test_user.id


# ============================================================
# get_user_review()
# ============================================================

def test_get_user_review_returns_review(
    db,
    test_user,
):
    """
    Verify that a user's review for a product can be retrieved.
    """

    category = create_category(db)
    product = create_product(db, category)

    review = create_review(
        db=db,
        product=product,
        user=test_user,
    )

    repository = ReviewRepository(db)

    result = repository.get_user_review(
        product_id=product.id,
        user_id=test_user.id,
    )

    assert result is not None
    assert result.id == review.id


def test_get_user_review_returns_none_when_not_found(
    db,
    test_user,
):
    """
    Verify that no review returns None.
    """

    category = create_category(db)
    product = create_product(db, category)

    repository = ReviewRepository(db)

    result = repository.get_user_review(
        product_id=product.id,
        user_id=test_user.id,
    )

    assert result is None


# ============================================================
# list_product_reviews()
# ============================================================

def test_list_product_reviews(
    db,
    test_user,
    another_user,
):
    """
    Verify that all reviews belonging to a product
    are returned.
    """

    category = create_category(db)
    product = create_product(db, category)

    review_one = create_review(
        db=db,
        product=product,
        user=test_user,
        rating=5,
        comment="Excellent",
    )

    review_two = create_review(
        db=db,
        product=product,
        user=another_user,
        rating=4,
        comment="Very good",
    )

    repository = ReviewRepository(db)

    reviews = repository.list_product_reviews(
        product.id,
    )

    assert len(reviews) == 2

    review_ids = {
        review.id
        for review in reviews
    }

    assert review_one.id in review_ids
    assert review_two.id in review_ids


def test_list_product_reviews_returns_empty_list(
    db,
    test_user,
):
    """
    Verify that a product without reviews returns
    an empty list.
    """

    category = create_category(db)
    product = create_product(db, category)

    repository = ReviewRepository(db)

    reviews = repository.list_product_reviews(
        product.id,
    )

    assert reviews == []


# ============================================================
# get_by_id()
# ============================================================

def test_get_review_by_id(
    db,
    test_user,
):
    """
    Verify that a review can be retrieved by its ID.
    """

    category = create_category(db)
    product = create_product(db, category)

    review = create_review(
        db=db,
        product=product,
        user=test_user,
    )

    repository = ReviewRepository(db)

    result = repository.get_by_id(
        review.id,
    )

    assert result is not None
    assert result.id == review.id


def test_get_review_by_id_returns_none(
    db,
):
    """
    Verify that an unknown review ID returns None.
    """

    repository = ReviewRepository(db)

    result = repository.get_by_id(
        99999,
    )

    assert result is None


# ============================================================
# update()
# ============================================================

def test_update_review(
    db,
    test_user,
):
    """
    Verify that the repository persists changes to a review.
    """

    category = create_category(db)
    product = create_product(db, category)

    review = create_review(
        db=db,
        product=product,
        user=test_user,
        rating=3,
        comment="Okay",
    )

    review.rating = 5
    review.comment = "Excellent"

    repository = ReviewRepository(db)

    result = repository.update(review)

    assert result.rating == 5
    assert result.comment == "Excellent"

    refreshed = repository.get_by_id(
        review.id,
    )

    assert refreshed.rating == 5
    assert refreshed.comment == "Excellent"


# ============================================================
# delete()
# ============================================================

def test_delete_review(
    db,
    test_user,
):
    """
    Verify that the repository permanently removes
    a review from the database.
    """

    category = create_category(db)
    product = create_product(db, category)

    review = create_review(
        db=db,
        product=product,
        user=test_user,
    )

    repository = ReviewRepository(db)

    repository.delete(review)

    result = repository.get_by_id(
        review.id,
    )

    assert result is None