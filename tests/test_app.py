import copy

import pytest
import requests

import app as app_module
from app import app, inventory

SEED = copy.deepcopy(inventory)

SAMPLE_PRODUCT = {
    "product_name": "Nutella",
    "brands": "Ferrero",
    "ingredients_text": "sugar, palm oil",
    "barcode": "3017620422003",
}


class FakeResponse:
    def __init__(self, payload, status_code=200):
        self._payload = payload
        self.status_code = status_code

    def json(self):
        return self._payload

    def raise_for_status(self):
        if self.status_code >= 400:
            raise requests.HTTPError("request failed")


@pytest.fixture(autouse=True)
def reset_inventory():
    inventory.clear()
    inventory.extend(copy.deepcopy(SEED))


@pytest.fixture
def client():
    return app.test_client()


def test_get_inventory(client):
    response = client.get("/inventory")
    data = response.get_json()
    assert response.status_code == 200
    assert len(data) == 3
    assert data[0]["product_name"] == "Organic Almond Milk"


def test_get_one_item(client):
    response = client.get("/inventory/2")
    data = response.get_json()
    assert response.status_code == 200
    assert data["product_name"] == "Peanut Butter"


def test_get_missing_item(client):
    response = client.get("/inventory/99")
    assert response.status_code == 404
    assert response.get_json()["message"] == "Product not found"


def test_post_item(client):
    response = client.post("/inventory", json={
        "product_name": "Orange Juice",
        "brands": "Tropicana",
        "ingredients_text": "Oranges",
        "barcode": "048500012345",
        "price": 3.29,
        "quantity": 15,
    })
    data = response.get_json()
    assert response.status_code == 201
    assert data["id"] == 4
    assert data["product_name"] == "Orange Juice"
    assert len(inventory) == 4


def test_patch_price_and_quantity(client):
    response = client.patch("/inventory/1", json={"price": 5.25})
    data = response.get_json()
    assert response.status_code == 200
    assert data["price"] == 5.25
    assert data["quantity"] == 12


def test_patch_missing_item(client):
    response = client.patch("/inventory/99", json={"price": 1})
    assert response.status_code == 404


def test_delete_item(client):
    response = client.delete("/inventory/2")
    assert response.status_code == 204
    assert all(item["id"] != 2 for item in inventory)


def test_delete_missing_item(client):
    response = client.delete("/inventory/99")
    assert response.status_code == 404
    assert len(inventory) == 3


def test_lookup_requires_barcode_or_name(client):
    response = client.get("/lookup")
    assert response.status_code == 400


def test_lookup_by_barcode(client, monkeypatch):
    def fake_get(url, headers=None, params=None, timeout=None):
        return FakeResponse({
            "status": 1,
            "product": {
                "product_name": "Nutella",
                "brands": "Ferrero",
                "ingredients_text": "sugar, palm oil",
            },
        })

    monkeypatch.setattr(app_module.requests, "get", fake_get)
    response = client.get("/lookup", query_string={"barcode": "3017620422003"})
    data = response.get_json()
    assert response.status_code == 200
    assert data["product_name"] == "Nutella"
    assert data["barcode"] == "3017620422003"


def test_lookup_by_name(client, monkeypatch):
    def fake_get(url, headers=None, params=None, timeout=None):
        return FakeResponse({
            "products": [{
                "product_name": "Nutella",
                "brands": "Ferrero",
                "ingredients_text": "sugar, palm oil",
                "code": "3017620422003",
            }]
        })

    monkeypatch.setattr(app_module.requests, "get", fake_get)
    response = client.get("/lookup", query_string={"name": "nutella"})
    assert response.status_code == 200
    assert response.get_json()["barcode"] == "3017620422003"


def test_lookup_not_found(client, monkeypatch):
    def fake_get(url, headers=None, params=None, timeout=None):
        return FakeResponse({"status": 0})

    monkeypatch.setattr(app_module.requests, "get", fake_get)
    response = client.get("/lookup", query_string={"barcode": "000"})
    assert response.status_code == 404


def test_lookup_api_failure(client, monkeypatch):
    def fake_get(url, headers=None, params=None, timeout=None):
        raise requests.RequestException("offline")

    monkeypatch.setattr(app_module.requests, "get", fake_get)
    response = client.get("/lookup", query_string={"barcode": "3017620422003"})
    assert response.status_code == 502


def test_add_from_barcode(client, monkeypatch):
    def fake_get(url, headers=None, params=None, timeout=None):
        return FakeResponse({
            "status": 1,
            "product": {
                "product_name": SAMPLE_PRODUCT["product_name"],
                "brands": SAMPLE_PRODUCT["brands"],
                "ingredients_text": SAMPLE_PRODUCT["ingredients_text"],
            },
        })

    monkeypatch.setattr(app_module.requests, "get", fake_get)
    response = client.post("/inventory/from-barcode", json={
        "barcode": "3017620422003",
        "price": 4.99,
        "quantity": 6,
    })
    data = response.get_json()
    assert response.status_code == 201
    assert data["id"] == 4
    assert data["product_name"] == "Nutella"
    assert data["price"] == 4.99
    assert len(inventory) == 4
