from datetime import datetime, timezone

from sqlalchemy import Boolean
from sqlalchemy import Column
from sqlalchemy import DateTime
from sqlalchemy import Float
from sqlalchemy import Integer
from sqlalchemy import String

from app.database.base import Base


class Coupon(Base):
    """
    Represents a promotional coupon that can be
    applied to an order.
    """

    __tablename__ = "coupons"

    id = Column(
        Integer,
        primary_key=True,
        index=True,
    )

    code = Column(
        String,
        unique=True,
        nullable=False,
    )

    discount_percent = Column(
        Float,
        nullable=False,
    )

    active = Column(
        Boolean,
        default=True,
    )

    expires_at = Column(
        DateTime,
        nullable=True,
    )

    created_at = Column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),
    )