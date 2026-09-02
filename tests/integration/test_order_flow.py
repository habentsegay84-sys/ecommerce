def test_order_flow_product_setup(
    client,
    integration_admin,
    integration_user,
):
    # --------------------------------------------------------
    # 1. Admin login
    # --------------------------------------------------------

    login_response = client.post(
        "/auth/login",
        json={
            "email": integration_admin.email,
            "password": "password123",
        },
    )

    assert login_response.status_code == 200

    admin_token = login_response.json()["access_token"]

    admin_headers = {
        "Authorization": f"Bearer {admin_token}",
    }

    # --------------------------------------------------------
    # 2. Admin creates category
    # --------------------------------------------------------

    category_response = client.post(
        "/categories",
        json={
            "name": "Integration Electronics",
            "description": "Category for order-flow testing",
        },
        headers=admin_headers,
    )

    assert category_response.status_code == 201

    category = category_response.json()
    category_id = category["id"]

    assert category["name"] == "Integration Electronics"
    assert category_id > 0

    # --------------------------------------------------------
    # 3. Admin creates product
    # --------------------------------------------------------

    product_response = client.post(
        "/admin/products",
        json={
            "name": "Integration Test Laptop",
            "description": "Product for order-flow testing",
            "price": 1000.00,
            "stock": 10,
            "image_url": None,
            "category_id": category_id,
        },
        headers=admin_headers,
    )

    assert product_response.status_code == 201

    product = product_response.json()
    product_id = product["id"]

    assert product["name"] == "Integration Test Laptop"
    assert float(product["price"]) == 1000.00
    assert product["stock"] == 10
    assert product["category"]["id"] == category_id
    assert product_id > 0

    # --------------------------------------------------------
    # 4. Customer login
    # --------------------------------------------------------

    customer_login_response = client.post(
        "/auth/login",
        json={
            "email": integration_user.email,
            "password": "password123",
        },
    )

    assert customer_login_response.status_code == 200

    customer_token = customer_login_response.json()["access_token"]

    customer_headers = {
        "Authorization": f"Bearer {customer_token}",
    }

    # --------------------------------------------------------
    # 5. Customer views the product
    # --------------------------------------------------------

    product_view_response = client.get(
        f"/products/{product_id}",
    )

    assert product_view_response.status_code == 200

    viewed_product = product_view_response.json()

    assert viewed_product["id"] == product_id
    assert viewed_product["name"] == "Integration Test Laptop"
    assert float(viewed_product["price"]) == 1000.00
    assert viewed_product["stock"] == 10

    # --------------------------------------------------------
    # 6. Customer adds product to cart
    # --------------------------------------------------------

    add_to_cart_response = client.post(
        "/cart/add",
        json={
            "product_id": product_id,
            "quantity": 2,
        },
        headers=customer_headers,
    )

    assert add_to_cart_response.status_code == 200
    assert add_to_cart_response.json()["message"] == "Product added to cart"

    # --------------------------------------------------------
    # 7. Customer views cart
    # --------------------------------------------------------

    cart_response = client.get(
        "/cart",
        headers=customer_headers,
    )

    assert cart_response.status_code == 200

    cart = cart_response.json()

    assert len(cart["items"]) == 1

    cart_item = cart["items"][0]

    assert cart_item["product_id"] == product_id
    assert cart_item["product_name"] == "Integration Test Laptop"
    assert float(cart_item["price"]) == 1000.00
    assert cart_item["quantity"] == 2
    assert float(cart_item["subtotal"]) == 2000.00
    assert float(cart["total"]) == 2000.00

    # --------------------------------------------------------
    # 8. Customer updates cart quantity
    # --------------------------------------------------------

    update_cart_response = client.patch(
        f"/cart/items/{product_id}",
        json={
            "quantity": 3,
        },
        headers=customer_headers,
    )

    assert update_cart_response.status_code == 200

    updated_cart_item = update_cart_response.json()

    assert updated_cart_item["product_id"] == product_id
    assert updated_cart_item["quantity"] == 3

    # --------------------------------------------------------
    # 9. Verify updated cart
    # --------------------------------------------------------

    updated_cart_response = client.get(
        "/cart",
        headers=customer_headers,
    )

    assert updated_cart_response.status_code == 200

    updated_cart = updated_cart_response.json()

    assert len(updated_cart["items"]) == 1

    updated_item = updated_cart["items"][0]

    assert updated_item["product_id"] == product_id
    assert updated_item["quantity"] == 3
    assert float(updated_item["subtotal"]) == 3000.00
    assert float(updated_cart["total"]) == 3000.00

    # --------------------------------------------------------
    # 10. Customer checks out
    # --------------------------------------------------------

    checkout_response = client.post(
        "/orders/checkout",
        json={},
        headers=customer_headers,
    )

    assert checkout_response.status_code == 200

    checkout_data = checkout_response.json()

    assert checkout_data["message"] == "Order created successfully"

    order_id = checkout_data["order_id"]

    assert order_id > 0
    assert float(checkout_data["total_price"]) == 3000.00

    # --------------------------------------------------------
    # 11. Verify cart is empty after checkout
    # --------------------------------------------------------

    empty_cart_response = client.get(
        "/cart",
        headers=customer_headers,
    )

    assert empty_cart_response.status_code == 200

    empty_cart = empty_cart_response.json()

    assert empty_cart["items"] == []
    assert float(empty_cart["total"]) == 0.00

    # --------------------------------------------------------
    # 12. Verify order was created
    # --------------------------------------------------------

    order_response = client.get(
        f"/orders/{order_id}",
        headers=customer_headers,
    )

    assert order_response.status_code == 200

    order = order_response.json()

    assert order["id"] == order_id
    assert float(order["total_price"]) == 3000.00
    assert order["status"] == "pending"

    assert len(order["items"]) == 1

    order_item = order["items"][0]

    assert order_item["product_id"] == product_id
    assert order_item["product_name"] == "Integration Test Laptop"
    assert order_item["quantity"] == 3
    assert float(order_item["price"]) == 1000.00
    assert float(order_item["subtotal"]) == 3000.00

    # --------------------------------------------------------
    # 13. Verify order appears in order history
    # --------------------------------------------------------

    orders_response = client.get(
        "/orders",
        headers=customer_headers,
    )

    assert orders_response.status_code == 200

    orders = orders_response.json()

    assert len(orders) == 1
    assert orders[0]["id"] == order_id
    assert orders[0]["status"] == "pending"

    # --------------------------------------------------------
    # 14. Verify inventory was reduced
    # --------------------------------------------------------

    product_after_checkout_response = client.get(
        f"/products/{product_id}",
    )

    assert product_after_checkout_response.status_code == 200

    product_after_checkout = (
        product_after_checkout_response.json()
    )

    assert product_after_checkout["stock"] == 7

    # --------------------------------------------------------
    # 15. Customer creates payment
    # --------------------------------------------------------

    payment_response = client.post(
        f"/payments/{order_id}/pay",
        json={
            "payment_method": "card",
        },
        headers=customer_headers,
    )

    assert payment_response.status_code == 200

    payment = payment_response.json()

    payment_id = payment["id"]

    assert payment_id > 0
    assert payment["order_id"] == order_id
    assert float(payment["amount"]) == 3000.00
    assert payment["payment_method"] == "card"

    # Payment must start as pending.
    assert payment["status"] == "pending"

    assert payment["transaction_reference"] is not None
    assert payment["paid_at"] is None

    # --------------------------------------------------------
    # 16. Admin marks payment as successful
    # --------------------------------------------------------

    payment_status_response = client.patch(
        f"/payments/{payment_id}/status",
        json={
            "status": "successful",
        },
        headers=admin_headers,
    )

    assert payment_status_response.status_code == 200

    successful_payment = payment_status_response.json()

    assert successful_payment["id"] == payment_id
    assert successful_payment["order_id"] == order_id
    assert successful_payment["status"] == "successful"

    assert successful_payment["paid_at"] is not None

    # --------------------------------------------------------
    # 17. Verify order changed to processing
    # --------------------------------------------------------

    final_order_response = client.get(
        f"/orders/{order_id}",
        headers=customer_headers,
    )

    assert final_order_response.status_code == 200

    final_order = final_order_response.json()

    assert final_order["id"] == order_id
    assert final_order["status"] == "processing"

    assert float(final_order["total_price"]) == 3000.00

    # --------------------------------------------------------
    # 18. Verify payment cannot be created twice
    # --------------------------------------------------------

    duplicate_payment_response = client.post(
        f"/payments/{order_id}/pay",
        json={
            "payment_method": "card",
        },
        headers=customer_headers,
    )

    assert duplicate_payment_response.status_code == 400



