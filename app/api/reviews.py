from fastapi import APIRouter
from fastapi import Depends

from sqlalchemy.orm import Session

from app.auth.dependencies import get_current_user
from app.database.session import get_db

from app.models.user import User

from app.schemas.review import (
    ReviewCreate,
    ReviewUpdate,
    ReviewResponse,
)

from app.services.review_service import (
    create_review_service,
    list_product_reviews_service,
    update_review_service,
    delete_review_service,
)

router = APIRouter(
    prefix="/reviews",
    tags=["Reviews"],
)


@router.post(
    "/products/{product_id}",
    response_model=ReviewResponse,
)
def create_review(
    product_id: int,
    review_data: ReviewCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Create a review for a product.
    """

    return create_review_service(
        db=db,
        product_id=product_id,
        review_data=review_data,
        current_user=current_user,
    )

@router.get(
    "/products/{product_id}",
    response_model=list[ReviewResponse],
)
def list_reviews(
    product_id: int,
    db: Session = Depends(get_db),
):
    """
    List all reviews for a product.
    """

    return list_product_reviews_service(
        db=db,
        product_id=product_id,
    )

@router.patch(
    "/{review_id}",
    response_model=ReviewResponse,
)
def update_review(
    review_id: int,
    review_data: ReviewUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Update your review.
    """

    return update_review_service(
        db=db,
        review_id=review_id,
        review_data=review_data,
        current_user=current_user,
    )

@router.delete(
    "/{review_id}",
)
def delete_review(
    review_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Delete your review.
    """

    return delete_review_service(
        db=db,
        review_id=review_id,
        current_user=current_user,
    )