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
        Persist a new coupon to the database.
        """

        self.db.add(coupon)
        self.db.commit()
        self.db.refresh(coupon)

        return coupon

    def update(
        self,
        coupon: Coupon,
    ) -> Coupon:
        """
        Persist changes made to an existing coupon.
        """

        self.db.commit()
        self.db.refresh(coupon)

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
    ):
        """
        Delete a coupon from the database.
        """

        self.db.delete(coupon)
        self.db.commit()

    def get_valid_coupon(
    self,
    code: str,
    ) -> Coupon | None:
        """
        Return only an active,
        non-expired coupon.
        """

        coupon = (
            self.db.query(Coupon)
            .filter(
                Coupon.code == code,
                Coupon.active == True,
            )
            .first()
        )

        if coupon is None:
            return None

        if coupon.expires_at:
            expires_at = coupon.expires_at

            if expires_at.tzinfo is None:
                expires_at = expires_at.replace(
                    tzinfo=timezone.utc
                )

            if expires_at < datetime.now(timezone.utc):
                return None

        return coupon