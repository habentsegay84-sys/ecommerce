from fastapi.testclient import TestClient


def get_auth_headers(
    client: TestClient,
):
    """
    Creates a test user, logs in,
    and returns JWT authentication headers.
    """

    # Register test user
    client.post(
        "/users/register",
        json={
            "username": "testuser",
            "email": "test@example.com",
            "password": "password123",
        },
    )

    # Login user
    response = client.post(
        "/auth/login",
        json={
            "email": "test@example.com",
            "password": "password123",
        },
    )

    token = response.json()["access_token"]

    return {
        "Authorization": f"Bearer {token}"
    }