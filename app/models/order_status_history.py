from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from app.database.base import Base


class OrderStatusHistory(Base):

    __tablename__ = "order_status_history"

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

    old_status = Column(
        String,
        nullable=True,
    )

    new_status = Column(
        String,
        nullable=False,
    )

    changed_by = Column(
        Integer,
        ForeignKey("users.id"),
        nullable=False,
    )

    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
    )


    order = relationship(
        "Order",
        back_populates="status_history",
    )


    user = relationship(
        "User",
    )