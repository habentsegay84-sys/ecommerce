from sqlalchemy import (
    Column,
    Integer,
    Float,
    String,
    DateTime,
    ForeignKey,
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.database.base import Base


class Payment(Base):

    __tablename__ = "payments"

    id = Column(
        Integer,
        primary_key=True,
        index=True,
    )

    order_id = Column(
        Integer,
        ForeignKey("orders.id"),
        nullable=False,
    )

    amount = Column(
        Float,
        nullable=False,
    )

    payment_method = Column(
        String,
        nullable=False,
    )

    status = Column(
        String,
        default="pending",
    )

    transaction_reference = Column(
        String,
        nullable=True,
    )

    paid_at = Column(
        DateTime(timezone=True),
        nullable=True,
    )

    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
    )

    order = relationship(
        "Order",
        back_populates="payment",
    )