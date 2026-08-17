from tests.utils.auth import get_auth_headers
from tests.utils.auth import get_admin_auth_headers

def test_payment_endpoint_with_auth(
    client,
    test_user,
    test_order,
):
    """
    Test that an authenticated user can pay
    for their own order.
    """

    headers = get_auth_headers(client)

    response = client.post(
        f"/payments/{test_order.id}/pay",
        headers=headers,
        json={
            "payment_method": "cash",
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["order_id"] == test_order.id
    assert data["amount"] == 100
    assert data["payment_method"] == "cash"

def test_user_cannot_pay_another_users_order(
    client,
    test_order,
    another_user,
):
    """
    A user must not be able to pay for
    another user's order.
    """

    headers = get_auth_headers(
        client,
        username="anotheruser",
        email="another@example.com",
    )

    response = client.post(
        f"/payments/{test_order.id}/pay",
        headers=headers,
        json={
            "payment_method": "cash",
        },
    )

    assert response.status_code == 404

def test_user_cannot_pay_same_order_twice(
    client,
    test_order,
):
    """
    A user must not be able to pay the same order twice.
    """

    headers = get_auth_headers(client)

    # First payment
    first_response = client.post(
        f"/payments/{test_order.id}/pay",
        headers=headers,
        json={
            "payment_method": "cash",
        },
    )

    assert first_response.status_code == 200

    # Second payment attempt
    second_response = client.post(
        f"/payments/{test_order.id}/pay",
        headers=headers,
        json={
            "payment_method": "cash",
        },
    )

    assert second_response.status_code == 400

def test_admin_can_update_payment_status(
    client,
    db,
    admin_user,
    test_payment,
):
    """
    Admin can change a payment from pending
    to successful and the order moves to processing.
    """

    headers = get_admin_auth_headers(
        client,
        db,
    )

    response = client.patch(
        f"/payments/{test_payment.id}/status",
        headers=headers,
        json={
            "status": "successful"
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["id"] == test_payment.id
    assert data["status"] == "successful"

    db.refresh(test_payment)
    db.refresh(test_payment.order)

    assert test_payment.status == "successful"
    assert test_payment.order.status == "processing"
    assert test_payment.paid_at is not None

