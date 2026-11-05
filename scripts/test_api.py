import os
import time
import pytest
import requests

API_URL = os.getenv("API_URL", "http://localhost:8000")

@pytest.fixture(scope="session", autouse=True)
def wait_for_api():
    """Wait until the API is healthy before running tests."""
    for _ in range(15):
        try:
            res = requests.get(f"{API_URL}/health", timeout=3)
            if res.status_code == 200:
                return
        except requests.exceptions.RequestException:
            pass
        time.sleep(2)
    pytest.fail("API did not become ready in time")

def test_root_endpoint():
    res = requests.get(f"{API_URL}/")
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "Online"
    assert "Apache CouchDB" in data["database"]

def test_create_and_get_product():
    payload = {
        "name": "Mechanical Keyboard RGB",
        "category": "Accessories",
        "price": 89.99,
        "stock": 30,
        "tags": ["gaming", "keyboard", "mechanical"],
        "specs": {"switches": "Cherry MX Red", "wireless": True},
        "status": "active"
    }
    
    # 1. Create product
    create_res = requests.post(f"{API_URL}/products", json=payload)
    assert create_res.status_code == 201
    created_product = create_res.json()
    product_id = created_product["id"]
    assert "rev" in created_product
    assert created_product["name"] == payload["name"]

    # 2. Get product by ID
    get_res = requests.get(f"{API_URL}/products/{product_id}")
    assert get_res.status_code == 200
    fetched = get_res.json()
    assert fetched["id"] == product_id
    assert fetched["specs"]["switches"] == "Cherry MX Red"

    # 3. Update product
    update_payload = {"price": 79.99, "stock": 25}
    put_res = requests.put(f"{API_URL}/products/{product_id}", json=update_payload)
    assert put_res.status_code == 200
    updated = put_res.json()
    assert updated["price"] == 79.99
    assert updated["stock"] == 25

    # 4. Delete product
    del_res = requests.delete(f"{API_URL}/products/{product_id}")
    assert del_res.status_code == 204

    # 5. Verify deletion
    verify_res = requests.get(f"{API_URL}/products/{product_id}")
    assert verify_res.status_code == 404
