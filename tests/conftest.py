import pytest
from fastapi.testclient import TestClient

from app.database import db
from app.main import app
from tests.utils.api_client import APIClient


@pytest.fixture(autouse=True)
def reset_db():
    db.reset()
    yield
    db.reset()


@pytest.fixture
def client() -> TestClient:
    return TestClient(app)


@pytest.fixture
def api(client: TestClient) -> APIClient:
    return APIClient(client)


@pytest.fixture
def registered_user(api: APIClient) -> dict:
    username, email, password = "jdoe", "jdoe@example.com", "S3curePass!"
    response = api.register(username, email, password)
    assert response.status_code == 201
    return {"username": username, "email": email, "password": password, "user": response.json()}


@pytest.fixture
def auth_client(api: APIClient, registered_user: dict) -> APIClient:
    login_response = api.login(registered_user["username"], registered_user["password"])
    token = login_response.json()["access_token"]
    return api.with_token(token)
