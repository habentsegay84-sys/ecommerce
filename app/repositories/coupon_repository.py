from sqlalchemy.orm import Session

from app.models.coupon import Coupon
from datetime import datetime, timezone


class CouponRepository:
    """
    Repository responsible for all database operations
    related to coupons.
    """

    def __init__(self, db: Session):
        """
        Store the active database session.
        """
        self.db = db

    def get_by_code(
        self,
        code: str,
    ) -> Coupon | None:
        """
        Retrieve a coupon by its unique code.
        """

        return (
            self.db.query(Coupon)
            .filter(Coupon.code == code)
            .first()
        )

    def create(
        self,
        coupon: Coupon,
    ) -> Coupon:
        """
        Add a new coupon to the current transaction.

        The service layer is responsible for
        committing or rolling back the transaction.
        """

        self.db.add(coupon)
        self.db.flush()

        return coupon

    def update(
        self,
        coupon: Coupon,
    ) -> Coupon:
        """
        Update a coupon within the current transaction.

        The service layer is responsible for
        committing or rolling back the transaction.
        """

        self.db.flush()

        return coupon

    def list_all(self) -> list[Coupon]:
        """
        Retrieve all coupons ordered by newest first.
        """

        return (
            self.db.query(Coupon)
            .order_by(Coupon.created_at.desc())
            .all()
        )

    def get_by_id(
        self,
        coupon_id: int,
    ) -> Coupon | None:
        """
        Retrieve a coupon by its ID.
        """

        return (
            self.db.query(Coupon)
            .filter(Coupon.id == coupon_id)
            .first()
        )


    def delete(
        self,
        coupon: Coupon,
    ) -> None:
        """
        Delete a coupon within the current transaction.

        The service layer is responsible for
        committing or rolling back the transaction.
        """

        self.db.delete(coupon)
        self.db.flush()

    def get_active_coupon(
        self,
        code: str,
    ) -> Coupon | None:
        """
        Return an active coupon by code.
        """

        return (
            self.db.query(Coupon)
            .filter(
                Coupon.code == code,
                Coupon.active == True,
            )
            .first()
        )