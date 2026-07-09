import pytest

from tests.utils.assertions import assert_error_response
from tests.utils.api_client import APIClient


@pytest.mark.positive
def test_register_new_user_returns_201_with_user_payload(api: APIClient):
    response = api.register("alice", "alice@example.com", "SecurePass1!")

    assert response.status_code == 201
    body = response.json()
    assert body["username"] == "alice"
    assert body["email"] == "alice@example.com"
    assert "password" not in body
    assert "hashed_password" not in body


@pytest.mark.positive
def test_login_with_valid_credentials_returns_access_token(api: APIClient, registered_user: dict):
    response = api.login(registered_user["username"], registered_user["password"])

    assert response.status_code == 200
    body = response.json()
    assert body["token_type"] == "bearer"
    assert isinstance(body["access_token"], str) and body["access_token"]


@pytest.mark.positive
def test_authenticated_request_succeeds_with_valid_token(auth_client: APIClient):
    response = auth_client.list_items()

    assert response.status_code == 200
    assert response.json() == []


@pytest.mark.negative
def test_register_with_duplicate_username_returns_409(api: APIClient, registered_user: dict):
    response = api.register(registered_user["username"], "another@example.com", "AnotherPass1!")

    assert_error_response(response, 409, error_code="USER_ALREADY_EXISTS")


@pytest.mark.negative
def test_register_with_invalid_email_returns_422(api: APIClient):
    response = api.register("bob", "not-an-email", "SecurePass1!")

    assert_error_response(response, 422, error_code="VALIDATION_ERROR")


@pytest.mark.negative
def test_register_with_short_password_returns_422(api: APIClient):
    response = api.register("bob", "bob@example.com", "short")

    assert_error_response(response, 422, error_code="VALIDATION_ERROR")


@pytest.mark.negative
def test_login_with_wrong_password_returns_401(api: APIClient, registered_user: dict):
    response = api.login(registered_user["username"], "wrong-password")

    assert_error_response(response, 401, error_code="INVALID_CREDENTIALS")


@pytest.mark.negative
def test_login_with_unknown_username_returns_401(api: APIClient):
    response = api.login("no-such-user", "whatever-password")

    assert_error_response(response, 401, error_code="INVALID_CREDENTIALS")


@pytest.mark.negative
def test_request_without_token_returns_401(api: APIClient):
    response = api.list_items()

    assert response.status_code == 401


@pytest.mark.negative
def test_request_with_malformed_token_returns_401(api: APIClient):
    response = api.with_token("not-a-real-jwt").list_items()

    assert_error_response(response, 401, error_code="HTTP_ERROR")
