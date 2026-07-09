"""Shared response-shape assertions so every test validates errors the same way."""


def assert_error_response(response, status_code: int, error_code: str | None = None) -> None:
    assert response.status_code == status_code, response.text
    body = response.json()
    assert "error_code" in body, body
    assert "message" in body, body
    if error_code is not None:
        assert body["error_code"] == error_code, body


def assert_item_schema(item: dict) -> None:
    for field in ("id", "name", "price", "quantity", "owner_id"):
        assert field in item, item
    assert isinstance(item["id"], int)
    assert isinstance(item["price"], (int, float))
    assert isinstance(item["quantity"], int)
