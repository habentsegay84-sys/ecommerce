from sqlalchemy.orm import Session

from app.models.review import Review
from app.models.user import User

from app.schemas.review import (
    ReviewCreate,
    ReviewUpdate,
)

from app.repositories.product_repository import ProductRepository
from app.repositories.review_repository import ReviewRepository


def create_review_service(
    db: Session,
    product_id: int,
    review_data: ReviewCreate,
    current_user: User,
):
    """
    Create a review for a product.
    """

    product_repository = ProductRepository(db)
    review_repository = ReviewRepository(db)

    product = product_repository.get_by_id(
        product_id,
    )

    if product is None:
        raise ValueError(
            "Product not found."
        )

    existing_review = review_repository.get_user_review(
        product_id=product_id,
        user_id=current_user.id,
    )

    if existing_review:
        raise ValueError(
            "You have already reviewed this product."
        )

    review = Review(
        rating=review_data.rating,
        comment=review_data.comment,
        user_id=current_user.id,
        product_id=product.id,
    )

    return review_repository.create(review)

def list_product_reviews_service(
    db: Session,
    product_id: int,
):
    """
    Return all reviews for a product.
    """

    product_repository = ProductRepository(db)
    review_repository = ReviewRepository(db)

    product = product_repository.get_by_id(
        product_id,
    )

    if product is None:
        raise ValueError(
            "Product not found."
        )

    return review_repository.list_product_reviews(
        product_id,
    )

def update_review_service(
    db: Session,
    review_id: int,
    review_data: ReviewUpdate,
    current_user: User,
):
    """
    Update the authenticated user's review.
    """

    repository = ReviewRepository(db)

    review = repository.get_by_id(
        review_id,
    )

    if review is None:
        raise ValueError(
            "Review not found."
        )

    if review.user_id != current_user.id:
        raise ValueError(
            "You can only update your own review."
        )

    if review_data.rating is not None:
        review.rating = review_data.rating

    if review_data.comment is not None:
        review.comment = review_data.comment

    return repository.update(review)