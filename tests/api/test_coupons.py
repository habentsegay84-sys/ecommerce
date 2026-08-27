from tests.utils.auth import (
    get_admin_auth_headers,
    get_auth_headers,
)


def test_admin_can_create_coupon(
    client,
    db,
    admin_user,
):
    """
    Verify that an authenticated administrator can
    create a new coupon through the API.
    """

    headers = get_admin_auth_headers(
        client,
        db,
    )

    response = client.post(
        "/coupons",
        headers=headers,
        json={
            "code": "SUMMER30",
            "discount_percent": 30,
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["code"] == "SUMMER30"
    assert data["discount_percent"] == 30
    assert data["active"] is True

def test_normal_user_cannot_create_coupon(
    client,
    test_user,
):
    """
    Verify that a normal user cannot create a coupon.
    """

    headers = get_auth_headers(
        client,
    )

    response = client.post(
        "/coupons",
        headers=headers,
        json={
            "code": "USER30",
            "discount_percent": 30,
        },
    )

    assert response.status_code == 403

def test_admin_cannot_create_duplicate_coupon(
    client,
    admin_user,
):
    headers = get_admin_auth_headers(
        client,
        db=None,
    )

    first_response = client.post(
        "/coupons",
        headers=headers,
        json={
            "code": "SUMMER30",
            "discount_percent": 30,
        },
    )

    assert first_response.status_code == 200

    second_response = client.post(
        "/coupons",
        headers=headers,
        json={
            "code": "SUMMER30",
            "discount_percent": 20,
        },
    )

    assert second_response.status_code == 400
    assert second_response.json()["detail"] == "Coupon code already exists."

def test_admin_can_list_coupons(
    client,
    admin_user,
):
    headers = get_admin_auth_headers(
        client,
        db=None,
    )

    client.post(
        "/coupons",
        headers=headers,
        json={
            "code": "SUMMER30",
            "discount_percent": 30,
        },
    )

    client.post(
        "/coupons",
        headers=headers,
        json={
            "code": "WINTER20",
            "discount_percent": 20,
        },
    )

    response = client.get(
        "/coupons",
        headers=headers,
    )

    assert response.status_code == 200

    data = response.json()

    assert len(data) == 2
    assert data[0]["code"] == "WINTER20"
    assert data[1]["code"] == "SUMMER30"

def test_normal_user_cannot_list_coupons(
    client,
):
    """
    Verify that a normal user cannot list coupons.
    """

    headers = get_auth_headers(
        client,
    )

    response = client.get(
        "/coupons",
        headers=headers,
    )

    assert response.status_code == 403

def test_admin_can_update_coupon(
    client,
    admin_user,
):
    """
    Verify that an administrator can update a coupon.
    """

    headers = get_admin_auth_headers(
        client,
        db=None,
    )

    create_response = client.post(
        "/coupons",
        headers=headers,
        json={
            "code": "SUMMER30",
            "discount_percent": 30,
        },
    )

    assert create_response.status_code == 200

    coupon_id = create_response.json()["id"]

    response = client.patch(
        f"/coupons/{coupon_id}",
        headers=headers,
        json={
            "discount_percent": 40,
            "active": False,
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["id"] == coupon_id
    assert data["code"] == "SUMMER30"
    assert data["discount_percent"] == 40
    assert data["active"] is False

def test_normal_user_cannot_update_coupon(
    client,
    admin_user,
):
    """
    Verify that a normal user cannot update a coupon.
    """

    admin_headers = get_admin_auth_headers(
        client,
        db=None,
    )

    create_response = client.post(
        "/coupons",
        headers=admin_headers,
        json={
            "code": "SUMMER30",
            "discount_percent": 30,
        },
    )

    assert create_response.status_code == 200

    coupon_id = create_response.json()["id"]

    user_headers = get_auth_headers(
        client,
    )

    response = client.patch(
        f"/coupons/{coupon_id}",
        headers=user_headers,
        json={
            "discount_percent": 50,
        },
    )

    assert response.status_code == 403

def test_admin_can_update_coupon(
    client,
    admin_user,
):
    """
    Verify that an administrator can update a coupon.
    """

    headers = get_admin_auth_headers(
        client,
        db=None,
    )

    create_response = client.post(
        "/coupons",
        headers=headers,
        json={
            "code": "SUMMER30",
            "discount_percent": 30,
        },
    )

    assert create_response.status_code == 200

    coupon_id = create_response.json()["id"]

    response = client.patch(
        f"/coupons/{coupon_id}",
        headers=headers,
        json={
            "discount_percent": 50,
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["id"] == coupon_id
    assert data["code"] == "SUMMER30"
    assert data["discount_percent"] == 50
    assert data["active"] is True

def test_admin_cannot_update_nonexistent_coupon(
    client,
    admin_user,
):
    """
    Verify that updating a nonexistent coupon returns 404.
    """

    headers = get_admin_auth_headers(
        client,
        db=None,
    )

    response = client.patch(
        "/coupons/9999",
        headers=headers,
        json={
            "discount_percent": 50,
        },
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Coupon not found."

def test_admin_can_delete_coupon(
    client,
    admin_user,
):
    """
    Verify that an administrator can delete a coupon.
    """

    headers = get_admin_auth_headers(
        client,
        db=None,
    )

    create_response = client.post(
        "/coupons",
        headers=headers,
        json={
            "code": "DELETE20",
            "discount_percent": 20,
        },
    )

    assert create_response.status_code == 200

    coupon_id = create_response.json()["id"]

    response = client.delete(
        f"/coupons/{coupon_id}",
        headers=headers,
    )

    assert response.status_code == 200

    assert response.json() == {
        "message": "Coupon deleted successfully."
    }

    list_response = client.get(
        "/coupons",
        headers=headers,
    )

    assert list_response.status_code == 200

    coupons = list_response.json()

    assert all(
        coupon["id"] != coupon_id
        for coupon in coupons
    )


def test_admin_cannot_delete_nonexistent_coupon(
    client,
    admin_user,
):
    """
    Verify that deleting a nonexistent coupon
    returns HTTP 404.
    """

    headers = get_admin_auth_headers(
        client,
        db=None,
    )

    response = client.delete(
        "/coupons/99999",
        headers=headers,
    )

    assert response.status_code == 404

    assert response.json()["detail"] == "Coupon not found."