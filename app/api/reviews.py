from fastapi import APIRouter
from fastapi import Depends
from fastapi import HTTPException

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

    The service layer handles the business rules, while this
    API layer translates domain errors into appropriate HTTP
    responses.
    """

    try:
        return create_review_service(
            db=db,
            product_id=product_id,
            review_data=review_data,
            current_user=current_user,
        )

    except ValueError as e:
        if str(e) == "Product not found.":
            raise HTTPException(
                status_code=404,
                detail=str(e),
            )

        if str(e) == "You have already reviewed this product.":
            raise HTTPException(
                status_code=400,
                detail=str(e),
            )

        raise HTTPException(
            status_code=400,
            detail=str(e),
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

    The API layer translates service-level validation
    errors into appropriate HTTP responses.
    """

    try:
        return list_product_reviews_service(
            db=db,
            product_id=product_id,
        )

    except ValueError as e:
        if str(e) == "Product not found.":
            raise HTTPException(
                status_code=404,
                detail=str(e),
            )

        raise HTTPException(
            status_code=400,
            detail=str(e),
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
    Update the authenticated user's review.

    The service layer enforces ownership rules, while the API
    layer translates service errors into appropriate HTTP responses.
    """

    try:
        return update_review_service(
            db=db,
            review_id=review_id,
            review_data=review_data,
            current_user=current_user,
        )

    except ValueError as e:
        if str(e) == "Review not found.":
            raise HTTPException(
                status_code=404,
                detail=str(e),
            )

        if str(e) == "You can only update your own review.":
            raise HTTPException(
                status_code=403,
                detail=str(e),
            )

        raise HTTPException(
            status_code=400,
            detail=str(e),
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
    Delete the authenticated user's review.

    The service layer enforces review ownership and existence,
    while the API layer translates those business errors into
    appropriate HTTP responses.
    """

    try:
        return delete_review_service(
            db=db,
            review_id=review_id,
            current_user=current_user,
        )

    except ValueError as e:
        if str(e) == "Review not found.":
            raise HTTPException(
                status_code=404,
                detail=str(e),
            )

        if str(e) == "You can only delete your own review.":
            raise HTTPException(
                status_code=403,
                detail=str(e),
            )

        raise HTTPException(
            status_code=400,
            detail=str(e),
        )

