from app.models.user import User

def test_register_login_and_get_current_user(client):
    # 1. Register
    register_response = client.post(
        "/users/register",
        json={
            "username": "integrationuser",
            "email": "integration@example.com",
            "password": "password123",
        },
    )

    print("STATUS:", register_response.status_code)
    print("BODY:", register_response.json())

    assert register_response.status_code == 200

    registered_user = register_response.json()

    assert registered_user["username"] == "integrationuser"
    assert registered_user["email"] == "integration@example.com"

    # 2. Login
    login_response = client.post(
        "/auth/login",
        json={
            "email": "integration@example.com",
            "password": "password123",
        },
    )

    assert login_response.status_code == 200

    login_data = login_response.json()

    assert "access_token" in login_data
    assert login_data["token_type"] == "bearer"

    token = login_data["access_token"]

    # 3. Use JWT to access protected endpoint
    me_response = client.get(
        "/users/me",
        headers={
            "Authorization": f"Bearer {token}",
        },
    )

    assert me_response.status_code == 200

    current_user = me_response.json()

    # 4. Verify the authenticated user
    assert current_user["username"] == "integrationuser"
    assert current_user["email"] == "integration@example.com"

def test_inactive_user_cannot_access_protected_endpoint(client, db):
    # 1. Register user
    register_response = client.post(
        "/users/register",
        json={
            "username": "inactiveuser",
            "email": "inactive@example.com",
            "password": "password123",
        },
    )

    assert register_response.status_code == 200

    # 2. Login
    login_response = client.post(
        "/auth/login",
        json={
            "email": "inactive@example.com",
            "password": "password123",
        },
    )

    assert login_response.status_code == 200

    token = login_response.json()["access_token"]

    # 3. Deactivate the user using the same test database session

    user = (
        db.query(User)
        .filter(User.email == "inactive@example.com")
        .first()
    )

    assert user is not None

    user.is_active = False
    db.commit()

    # 4. Try to access protected endpoint
    response = client.get(
        "/users/me",
        headers={
            "Authorization": f"Bearer {token}",
        },
    )

    assert response.status_code == 403