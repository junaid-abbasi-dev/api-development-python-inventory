import requests

import cli


class FakeResponse:
    def __init__(self, payload=None, status_code=200):
        self._payload = payload or {}
        self.status_code = status_code

    def json(self):
        if self.status_code == 204:
            raise ValueError("no body")
        return self._payload


def scripted_input(answers):
    values = iter(answers)

    def _input(prompt=""):
        return next(values)

    return _input


def test_list_inventory(monkeypatch, capsys):
    def fake_get(url, params=None):
        return FakeResponse([{
            "id": 1,
            "product_name": "Organic Almond Milk",
            "price": 3.99,
            "quantity": 12,
        }])

    monkeypatch.setattr(cli.requests, "get", fake_get)
    cli.list_inventory()
    assert "Organic Almond Milk" in capsys.readouterr().out


def test_list_inventory_empty(monkeypatch, capsys):
    monkeypatch.setattr(cli.requests, "get", lambda url, params=None: FakeResponse([]))
    cli.list_inventory()
    assert "Inventory is empty." in capsys.readouterr().out


def test_view_item(monkeypatch, capsys):
    monkeypatch.setattr("builtins.input", scripted_input(["1"]))
    monkeypatch.setattr(cli.requests, "get", lambda url, params=None: FakeResponse({
        "id": 1,
        "product_name": "Organic Almond Milk",
        "brands": "Silk",
        "barcode": "025293001234",
        "price": 3.99,
        "quantity": 12,
        "ingredients_text": "Filtered water, almonds, cane sugar",
    }))
    cli.view_item()
    assert "Silk" in capsys.readouterr().out


def test_view_missing_item(monkeypatch, capsys):
    monkeypatch.setattr("builtins.input", scripted_input(["99"]))
    monkeypatch.setattr(
        cli.requests,
        "get",
        lambda url, params=None: FakeResponse({"message": "Product not found"}, 404),
    )
    cli.view_item()
    assert "404: Product not found" in capsys.readouterr().out


def test_add_item(monkeypatch, capsys):
    answers = ["Orange Juice", "Tropicana", "Oranges", "048500012345", "3.29", "15"]
    monkeypatch.setattr("builtins.input", scripted_input(answers))

    def fake_post(url, json):
        assert json["product_name"] == "Orange Juice"
        assert json["price"] == 3.29
        return FakeResponse({"id": 4, "product_name": "Orange Juice"}, 201)

    monkeypatch.setattr(cli.requests, "post", fake_post)
    cli.add_item()
    assert "Added Orange Juice as id 4" in capsys.readouterr().out


def test_add_item_rejects_bad_numbers(monkeypatch, capsys):
    answers = ["Orange Juice", "Tropicana", "Oranges", "048500012345", "abc", "15"]
    monkeypatch.setattr("builtins.input", scripted_input(answers))
    cli.add_item()
    assert "Price must be a number" in capsys.readouterr().out


def test_update_item(monkeypatch, capsys):
    monkeypatch.setattr("builtins.input", scripted_input(["1", "5.25", ""]))

    def fake_patch(url, json):
        assert json == {"price": 5.25}
        return FakeResponse({
            "product_name": "Organic Almond Milk",
            "price": 5.25,
            "quantity": 12,
        })

    monkeypatch.setattr(cli.requests, "patch", fake_patch)
    cli.update_item()
    assert "Updated Organic Almond Milk: $5.25, 12 in stock" in capsys.readouterr().out


def test_update_item_with_no_changes(monkeypatch, capsys):
    monkeypatch.setattr("builtins.input", scripted_input(["1", "", ""]))
    cli.update_item()
    assert "Nothing to update." in capsys.readouterr().out


def test_delete_item(monkeypatch, capsys):
    monkeypatch.setattr("builtins.input", scripted_input(["2"]))
    monkeypatch.setattr(cli.requests, "delete", lambda url: FakeResponse(status_code=204))
    cli.delete_item()
    assert "Deleted item 2" in capsys.readouterr().out


def test_find_by_barcode(monkeypatch, capsys):
    monkeypatch.setattr("builtins.input", scripted_input(["3017620422003"]))

    def fake_get(url, params=None):
        assert params == {"barcode": "3017620422003"}
        return FakeResponse({
            "product_name": "Nutella",
            "brands": "Ferrero",
            "barcode": "3017620422003",
            "ingredients_text": "sugar, palm oil",
        })

    monkeypatch.setattr(cli.requests, "get", fake_get)
    cli.find_on_api()
    assert "Nutella (Ferrero)" in capsys.readouterr().out


def test_find_by_name(monkeypatch, capsys):
    monkeypatch.setattr("builtins.input", scripted_input(["", "nutella"]))

    def fake_get(url, params=None):
        assert params == {"name": "nutella"}
        return FakeResponse({
            "product_name": "Nutella",
            "brands": "Ferrero",
            "barcode": "3017620422003",
            "ingredients_text": "sugar, palm oil",
        })

    monkeypatch.setattr(cli.requests, "get", fake_get)
    cli.find_on_api()
    assert "Nutella (Ferrero)" in capsys.readouterr().out


def test_add_from_barcode(monkeypatch, capsys):
    monkeypatch.setattr("builtins.input", scripted_input(["3017620422003", "4.99", "6"]))

    def fake_post(url, json):
        assert json["barcode"] == "3017620422003"
        return FakeResponse({"id": 4, "product_name": "Nutella"}, 201)

    monkeypatch.setattr(cli.requests, "post", fake_post)
    cli.add_from_barcode()
    assert "Added Nutella as id 4" in capsys.readouterr().out


def test_menu_quits(monkeypatch, capsys):
    monkeypatch.setattr("builtins.input", scripted_input(["8"]))
    cli.main()
    assert "Quit" in capsys.readouterr().out


def test_menu_rejects_bad_choice(monkeypatch, capsys):
    monkeypatch.setattr("builtins.input", scripted_input(["9", "8"]))
    cli.main()
    assert "Choose a number from 1 to 8." in capsys.readouterr().out


def test_menu_reports_connection_error(monkeypatch, capsys):
    monkeypatch.setattr("builtins.input", scripted_input(["1", "8"]))

    def fake_get(url, params=None):
        raise requests.RequestException("offline")

    monkeypatch.setattr(cli.requests, "get", fake_get)
    cli.main()
    assert "Could not reach the API" in capsys.readouterr().out
