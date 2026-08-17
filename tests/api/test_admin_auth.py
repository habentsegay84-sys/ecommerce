from tests.utils.auth import get_auth_headers

def test_normal_user_cannot_access_admin_products(client):
    headers = get_auth_headers(client)

    response = client.get(
        "/admin/products",
        headers=headers,
    )

    assert response.status_code == 403
