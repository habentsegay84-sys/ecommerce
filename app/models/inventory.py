from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from app.database.base import Base


class InventoryLog(Base):

    __tablename__ = "inventory_logs"

    id = Column(
        Integer,
        primary_key=True,
        index=True,
    )

    product_id = Column(
        Integer,
        ForeignKey("products.id"),
        nullable=False,
    )

    old_stock = Column(
        Integer,
        nullable=False,
    )

    new_stock = Column(
        Integer,
        nullable=False,
    )

    change_type = Column(
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


    product = relationship(
        "Product"
    )

    user = relationship(
        "User"
    )