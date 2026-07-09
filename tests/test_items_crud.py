import pytest

from tests.utils.assertions import assert_error_response, assert_item_schema
from tests.utils.api_client import APIClient


@pytest.mark.positive
def test_create_item_returns_201_with_expected_schema(auth_client: APIClient):
    response = auth_client.create_item(name="Widget", price=9.99, description="A useful widget", quantity=5)

    assert response.status_code == 201
    body = response.json()
    assert_item_schema(body)
    assert body["name"] == "Widget"
    assert body["price"] == 9.99
    assert body["quantity"] == 5


@pytest.mark.positive
def test_list_items_returns_only_items_owned_by_caller(auth_client: APIClient, api: APIClient):
    auth_client.create_item(name="Widget A", price=1.0)
    auth_client.create_item(name="Widget B", price=2.0)

    other_user = api.register_and_login("other", "other@example.com", "SecurePass1!")
    other_user.create_item(name="Not Visible", price=3.0)

    response = auth_client.list_items()

    assert response.status_code == 200
    names = {item["name"] for item in response.json()}
    assert names == {"Widget A", "Widget B"}


@pytest.mark.positive
def test_get_item_by_id_returns_the_created_item(auth_client: APIClient):
    created = auth_client.create_item(name="Widget", price=5.0).json()

    response = auth_client.get_item(created["id"])

    assert response.status_code == 200
    assert response.json() == created


@pytest.mark.positive
def test_update_item_applies_partial_changes(auth_client: APIClient):
    created = auth_client.create_item(name="Widget", price=5.0, quantity=1).json()

    response = auth_client.update_item(created["id"], price=7.5)

    assert response.status_code == 200
    body = response.json()
    assert body["price"] == 7.5
    assert body["name"] == "Widget"
    assert body["quantity"] == 1


@pytest.mark.positive
def test_delete_item_returns_204_and_removes_it(auth_client: APIClient):
    created = auth_client.create_item(name="Widget", price=5.0).json()

    delete_response = auth_client.delete_item(created["id"])
    get_response = auth_client.get_item(created["id"])

    assert delete_response.status_code == 204
    assert get_response.status_code == 404


@pytest.mark.negative
def test_create_item_with_negative_price_returns_422(auth_client: APIClient):
    response = auth_client.create_item(name="Widget", price=-1.0)

    assert_error_response(response, 422, error_code="VALIDATION_ERROR")


@pytest.mark.negative
def test_create_item_with_empty_name_returns_422(auth_client: APIClient):
    response = auth_client.create_item(name="", price=5.0)

    assert_error_response(response, 422, error_code="VALIDATION_ERROR")


@pytest.mark.negative
def test_get_nonexistent_item_returns_404(auth_client: APIClient):
    response = auth_client.get_item(999999)

    assert_error_response(response, 404, error_code="ITEM_NOT_FOUND")


@pytest.mark.negative
def test_get_item_owned_by_another_user_returns_403(auth_client: APIClient, api: APIClient):
    created = auth_client.create_item(name="Widget", price=5.0).json()
    other_user = api.register_and_login("intruder", "intruder@example.com", "SecurePass1!")

    response = other_user.get_item(created["id"])

    assert_error_response(response, 403, error_code="ITEM_ACCESS_FORBIDDEN")


@pytest.mark.negative
def test_update_nonexistent_item_returns_404(auth_client: APIClient):
    response = auth_client.update_item(999999, price=1.0)

    assert_error_response(response, 404, error_code="ITEM_NOT_FOUND")


@pytest.mark.negative
def test_delete_item_owned_by_another_user_returns_403(auth_client: APIClient, api: APIClient):
    created = auth_client.create_item(name="Widget", price=5.0).json()
    other_user = api.register_and_login("intruder2", "intruder2@example.com", "SecurePass1!")

    response = other_user.delete_item(created["id"])

    assert_error_response(response, 403, error_code="ITEM_ACCESS_FORBIDDEN")
