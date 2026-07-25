from datetime import datetime

from sqlalchemy import Column
from sqlalchemy import DateTime
from sqlalchemy import ForeignKey
from sqlalchemy import Integer
from sqlalchemy import Text
from sqlalchemy.orm import relationship

from app.database.base import Base


class Review(Base):
    """
    Review left by a user for a product.
    """

    __tablename__ = "reviews"

    id = Column(
        Integer,
        primary_key=True,
        index=True,
    )

    rating = Column(
        Integer,
        nullable=False,
    )

    comment = Column(
        Text,
        nullable=True,
    )

    user_id = Column(
        Integer,
        ForeignKey("users.id"),
        nullable=False,
    )

    product_id = Column(
        Integer,
        ForeignKey("products.id"),
        nullable=False,
    )

    created_at = Column(
        DateTime,
        default=datetime.utcnow,
    )

    user = relationship(
        "User",
        back_populates="reviews",
    )
    product = relationship(
        "Product",
        back_populates="reviews",
    )