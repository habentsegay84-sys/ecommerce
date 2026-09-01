import os

import pytest

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from fastapi.testclient import TestClient

from app.main import app as fastapi_app
from app.database.session import get_db
from app.database.base import Base

from app.models.user import User
from app.core.security import hash_password

import app.models


# ============================================================
# PostgreSQL integration-test database
# ============================================================

TEST_DATABASE_URL = os.getenv(
    "TEST_DATABASE_URL",
    "postgresql://postgres:postgres@localhost:5432/ecommerce_test",
)

engine = create_engine(
    TEST_DATABASE_URL,
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
    Provide a clean PostgreSQL database session
    for each integration test.
    """

    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)

    session = TestingSessionLocal()

    try:
        yield session

    finally:
        session.rollback()
        session.close()

        Base.metadata.drop_all(bind=engine)


# ============================================================
# Integration test users
# ============================================================

@pytest.fixture
def integration_user(db):
    """
    Create a normal user for integration tests.
    """

    user = User(
        username="integrationuser",
        email="integration@example.com",
        hashed_password=hash_password("password123"),
        role="user",
    )

    db.add(user)
    db.commit()
    db.refresh(user)

    return user


@pytest.fixture
def integration_admin(db):
    """
    Create an administrator for integration tests.
    """

    admin = User(
        username="integrationadmin",
        email="integrationadmin@example.com",
        hashed_password=hash_password("password123"),
        role="admin",
    )

    db.add(admin)
    db.commit()
    db.refresh(admin)

    return admin

# ============================================================
# FastAPI client
# ============================================================

@pytest.fixture
def client(db):
    """
    Provide a FastAPI test client connected
    to the PostgreSQL integration database.
    """

    def override_get_db():
        yield db

    fastapi_app.dependency_overrides[get_db] = override_get_db

    try:
        yield TestClient(fastapi_app)

    finally:
        fastapi_app.dependency_overrides.clear()