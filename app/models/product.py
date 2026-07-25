from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.database.base import Base


class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True)

    name = Column(String(150), nullable=False)

    description = Column(String(500), nullable=True)

    price = Column(
        Float,
        nullable=False,
    )

    stock = Column(
        Integer,
        nullable=False,
        default=0,
    )

    image_url = Column(String(255), nullable=True)

    is_deleted = Column(
        Boolean,
        nullable=False,
        default=False,
    )

    category_id = Column(
        Integer,
        ForeignKey("categories.id"),
        nullable=False,
    )

    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
    )

    category = relationship(
        "Category",
        back_populates="products",
    )

    cart_items = relationship(
        "CartItem",
        back_populates="product",
    )

    order_items = relationship(
        "OrderItem",
        back_populates="product",
    )

    inventory_logs = relationship(
        "InventoryLog",
        back_populates="product",
        cascade="all, delete-orphan",
    )

    reviews = relationship(
        "Review",
        back_populates="product",
        cascade="all, delete-orphan",
    )