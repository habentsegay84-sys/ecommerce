from tests.utils.auth import get_auth_headers


def test_payment_endpoint_with_auth(client):
    """
    Test payment endpoint with authentication.
    """

    headers = get_auth_headers(client)

    response = client.post(
        "/payments/999/pay",
        headers=headers,
        json={
            "payment_method": "cash"
        },
    )

    assert response.status_code == 404