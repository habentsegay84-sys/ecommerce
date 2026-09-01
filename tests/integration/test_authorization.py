def test_unauthenticated_user_cannot_access_me(client):
    response = client.get("/users/me")


    assert response.status_code == 401


def test_invalid_token_is_rejected(client):
    response = client.get(
    "/users/me",
    headers={
    "Authorization": "Bearer invalid-token",
    },
    )

    assert response.status_code == 401


def test_normal_user_cannot_access_admin_products(
    client,
    integration_user,
    ):
    login_response = client.post(
    "/auth/login",
    json={
    "email": integration_user.email,
    "password": "password123",
    },
    )


    assert login_response.status_code == 200

    token = login_response.json()["access_token"]

    response = client.get(
        "/admin/products",
        headers={
            "Authorization": f"Bearer {token}",
        },
    )

    assert response.status_code == 403


def test_admin_can_access_admin_products(
    client,
    integration_admin,
    ):
    login_response = client.post(
    "/auth/login",
    json={
    "email": integration_admin.email,
    "password": "password123",
    },
    )


    assert login_response.status_code == 200

    token = login_response.json()["access_token"]

    response = client.get(
        "/admin/products",
        headers={
            "Authorization": f"Bearer {token}",
        },
    )

    assert response.status_code == 200

