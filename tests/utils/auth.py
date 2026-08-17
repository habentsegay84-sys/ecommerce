from fastapi.testclient import TestClient


from fastapi.testclient import TestClient


def get_auth_headers(
    client: TestClient,
    username: str = "testuser",
    email: str = "test@example.com",
    password: str = "password123",
):
    register_response = client.post(
        "/users/register",
        json={
            "username": username,
            "email": email,
            "password": password,
        },
    )

    print("REGISTER:", register_response.status_code)
    print("REGISTER BODY:", register_response.json())

    response = client.post(
        "/auth/login",
        json={
            "email": email,
            "password": password,
        },
    )

    print("LOGIN:", response.status_code)
    print("LOGIN BODY:", response.json())

    assert response.status_code == 200

    token = response.json()["access_token"]

    return {
        "Authorization": f"Bearer {token}"
    }

def get_admin_auth_headers(
    client: TestClient,
    db,
):
    """
    Authenticate the existing administrator test fixture
    and return JWT authentication headers.
    """

    response = client.post(
        "/auth/login",
        json={
            "email": "admin@example.com",
            "password": "password123",
        },
    )

    assert response.status_code == 200

    token = response.json()["access_token"]

    return {
        "Authorization": f"Bearer {token}"
    }