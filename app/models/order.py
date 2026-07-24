from sqlalchemy import Column, DateTime, Float, ForeignKey, Integer, String
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.database.base import Base


class Order(Base):
    __tablename__ = "orders"

    id = Column(Integer, primary_key=True, index=True)

    user_id = Column(
        Integer,
        ForeignKey("users.id"),
        nullable=False,
    )

    total_price = Column(
        Float,
        nullable=False,
        default=0,
    )

    status = Column(
        String,
        nullable=False,
        default="pending",
    )

    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
    )

    user = relationship(
        "User",
        back_populates="orders",
    )

    payment = relationship(
        "Payment",
        back_populates="order",
        uselist=False,
    )

    items = relationship(
        "OrderItem",
        back_populates="order",
        cascade="all, delete-orphan",
    )

    status_history = relationship(
        "OrderStatusHistory",
        back_populates="order",
        cascade="all, delete-orphan",
    )
    coupon_id = Column(
        Integer,
        ForeignKey("coupons.id"),
        nullable=True,
    )

    coupon = relationship(
        "Coupon"
    )