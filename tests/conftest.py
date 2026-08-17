import os

os.environ["DATABASE_URL"] = (
    "postgresql://postgres:postgres@localhost:5432/ecommerce"
)

import pytest

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from fastapi.testclient import TestClient

from app.database.base import Base
from app.database.session import get_db

from app.main import app

from app.models.user import User
from app.models.order import Order

from app.core.security import hash_password
from app.models.payment import Payment


# ============================================================
# Test database
# ============================================================

SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={
        "check_same_thread": False,
    },
    poolclass=StaticPool,
)

TestingSessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
)


# ============================================================
# Database fixture
# ============================================================

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


# ============================================================
# FastAPI client
# ============================================================

@pytest.fixture
def client(db):
    """
    Provides a FastAPI test client using
    the test database.
    """

    def override_get_db():
        yield db

    app.dependency_overrides[get_db] = override_get_db

    yield TestClient(app)

    app.dependency_overrides.clear()

# ============================================================
# Test user
# ============================================================

@pytest.fixture
def test_user(db):
    """
    Create a user for testing.
    """

    user = User(
        username="testuser",
        email="test@example.com",
        hashed_password=hash_password("password123")
    )

    db.add(user)
    db.commit()
    db.refresh(user)

    return user


# ============================================================
# Test order
# ============================================================

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
def test_payment(
    db,
    test_order,
):
    """
    Create a pending payment for the test order.
    """

    payment = Payment(
        order_id=test_order.id,
        amount=test_order.total_price,
        payment_method="cash",
        status="pending",
        transaction_reference="test-transaction-123",
    )

    db.add(payment)
    db.commit()
    db.refresh(payment)

    return payment


# ============================================================
# Another user
# ============================================================

@pytest.fixture
def another_user(db):
    """
    Creates another user for security testing.
    """

    user = User(
        username="anotheruser",
        email="another@example.com",
        hashed_password=hash_password("password123"),
    )

    db.add(user)
    db.commit()
    db.refresh(user)

    return user

@pytest.fixture
def admin_user(db):
    """
    Create an administrator user for testing.
    """

    user = User(
        username="adminuser",
        email="admin@example.com",
        hashed_password=hash_password("password123"),
        role="admin",
    )

    db.add(user)
    db.commit()
    db.refresh(user)

    return user

@pytest.fixture
def test_payment(db, test_order):
    """
    Create a pending payment for the test order.
    """

    payment = Payment(
        order_id=test_order.id,
        amount=test_order.total_price,
        payment_method="cash",
        status="pending",
        transaction_reference="test-transaction-123",
    )

    db.add(payment)
    db.commit()
    db.refresh(payment)

    return payment