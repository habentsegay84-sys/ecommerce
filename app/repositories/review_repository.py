from sqlalchemy.orm import Session

from app.models.review import Review


class ReviewRepository:
    """
    Repository responsible for review database operations.
    """

    def __init__(
        self,
        db: Session,
    ):
        self.db = db

    def create(
        self,
        review: Review,
    ) -> Review:
        """
        Save a review.
        """

        self.db.add(review)
        self.db.commit()
        self.db.refresh(review)

        return review

    def get_user_review(
        self,
        product_id: int,
        user_id: int,
    ) -> Review | None:
        """
        Return a user's review for a product.
        """

        return (
            self.db.query(Review)
            .filter(
                Review.product_id == product_id,
                Review.user_id == user_id,
            )
            .first()
        )

    def list_product_reviews(
        self,
        product_id: int,
    ) -> list[Review]:
        """
        Return all reviews for a product.
        """

        return (
            self.db.query(Review)
            .filter(
                Review.product_id == product_id,
            )
            .all()
        )

    def update(
        self,
        review: Review,
    ) -> Review:
        """
        Save changes to a review.
        """

        self.db.commit()
        self.db.refresh(review)

        return review

    def delete(
        self,
        review: Review,
    ):
        """
        Delete a review.
        """

        self.db.delete(review)
        self.db.commit()

    def get_by_id(
        self,
        review_id: int,
    ) -> Review | None:
        """
        Retrieve a review by its ID.
        """

        return (
            self.db.query(Review)
            .filter(
                Review.id == review_id,
            )
            .first()
        )