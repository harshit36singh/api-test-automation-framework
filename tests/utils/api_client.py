"""Reusable API client wrapper so tests call intent-revealing methods instead of
repeating raw request/URL/header plumbing everywhere."""
from fastapi.testclient import TestClient


class APIClient:
    def __init__(self, client: TestClient, token: str | None = None):
        self._client = client
        self.token = token

    def _auth_headers(self) -> dict:
        return {"Authorization": f"Bearer {self.token}"} if self.token else {}

    def with_token(self, token: str) -> "APIClient":
        return APIClient(self._client, token)

    # --- auth workflows ---
    def register(self, username: str, email: str, password: str):
        return self._client.post(
            "/auth/register",
            json={"username": username, "email": email, "password": password},
        )

    def login(self, username: str, password: str):
        return self._client.post(
            "/auth/login",
            data={"username": username, "password": password},
        )

    def register_and_login(self, username: str, email: str, password: str) -> "APIClient":
        register_response = self.register(username, email, password)
        assert register_response.status_code == 201, register_response.text
        login_response = self.login(username, password)
        assert login_response.status_code == 200, login_response.text
        token = login_response.json()["access_token"]
        return self.with_token(token)

    # --- items CRUD workflows ---
    def create_item(self, name: str, price: float, description: str | None = None, quantity: int = 0):
        return self._client.post(
            "/items",
            json={"name": name, "description": description, "price": price, "quantity": quantity},
            headers=self._auth_headers(),
        )

    def list_items(self):
        return self._client.get("/items", headers=self._auth_headers())

    def get_item(self, item_id: int):
        return self._client.get(f"/items/{item_id}", headers=self._auth_headers())

    def update_item(self, item_id: int, **fields):
        return self._client.put(f"/items/{item_id}", json=fields, headers=self._auth_headers())

    def delete_item(self, item_id: int):
        return self._client.delete(f"/items/{item_id}", headers=self._auth_headers())
