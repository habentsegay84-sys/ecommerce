from datetime import datetime, timedelta, timezone

from jose import jwt

from app.core.config import SECRET_KEY, ALGORITHM
from tests.utils.auth import get_auth_headers

def test_get_me_with_auth(client):
    headers = get_auth_headers(client)

    response = client.get(
        "/users/me",
        headers=headers,
    )

    assert response.status_code == 200

    data = response.json()

    assert data["username"] == "testuser"
    assert data["email"] == "test@example.com"


def test_get_me_without_auth(client):
    response = client.get("/users/me")

    assert response.status_code == 401


def test_get_me_with_invalid_token(client):
    response = client.get(
        "/users/me",
        headers={
            "Authorization": "Bearer invalid-token"
        },
    )

    assert response.status_code == 401

def test_get_me_with_wrong_token_type(client):
    token = jwt.encode(
        {
            "sub": "1",
            "type": "refresh",
        },
        SECRET_KEY,
        algorithm=ALGORITHM,
    )

    response = client.get(
        "/users/me",
        headers={
            "Authorization": f"Bearer {token}"
        },
    )

    assert response.status_code == 401

def test_get_me_with_expired_token(client):
    token = jwt.encode(
        {
            "sub": "1",
            "type": "access",
            "exp": datetime.now(timezone.utc) - timedelta(minutes=1),
        },
        SECRET_KEY,
        algorithm=ALGORITHM,
    )

    response = client.get(
        "/users/me",
        headers={
            "Authorization": f"Bearer {token}"
        },
    )

    assert response.status_code == 401


def test_get_me_with_token_without_exp(client):
    token = jwt.encode(
        {
            "sub": "1",
            "type": "access",
        },
        SECRET_KEY,
        algorithm=ALGORITHM,
    )

    response = client.get(
        "/users/me",
        headers={
            "Authorization": f"Bearer {token}"
        },
    )

    assert response.status_code == 401
