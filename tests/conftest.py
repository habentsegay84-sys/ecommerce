
import os

os.environ["DATABASE_URL"] = (
    "postgresql://postgres:postgres@localhost:5432/ecommerce"
)

import pytest

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.database.base import Base

from app.models.user import User
from app.models.order import Order

from fastapi.testclient import TestClient

from app.main import app



@pytest.fixture
def client():
    """
    Provides a FastAPI test client.
    """

    return TestClient(app)


# Test database
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"


engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={
        "check_same_thread": False
    },
)


TestingSessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
)


@pytest.fixture
def db():
    """
    Creates a fresh database session
    for every test.
    """

    Base.metadata.create_all(
        bind=engine
    )

    session = TestingSessionLocal()

    try:
        yield session

    finally:
        session.close()

        Base.metadata.drop_all(
            bind=engine
        )

@pytest.fixture
def test_user(db):
    """
    Create a user for testing.
    """

    user = User(
        username="testuser",
        email="test@example.com",
        hashed_password="password123",
    )

    db.add(user)
    db.commit()
    db.refresh(user)

    return user

@pytest.fixture
def test_order(
    db,
    test_user,
):
    """
    Create a pending order for testing.
    """

    order = Order(
        user_id=test_user.id,
        total_price=100,
        status="pending",
    )

    db.add(order)
    db.commit()
    db.refresh(order)

    return order

@pytest.fixture
def another_user(db):
    """
    Creates another user for security testing.
    """

    user = User(
        username="anotheruser",
        email="another@example.com",
        hashed_password="password123",
    )

    db.add(user)
    db.commit()
    db.refresh(user)

    return user