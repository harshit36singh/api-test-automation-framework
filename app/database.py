"""In-memory data store. Swappable for a real database without touching route logic."""
from itertools import count
from typing import Optional


class InMemoryDB:
    def __init__(self) -> None:
        self.users: dict[int, dict] = {}
        self.items: dict[int, dict] = {}
        self._user_ids = count(1)
        self._item_ids = count(1)

    def reset(self) -> None:
        self.users.clear()
        self.items.clear()
        self._user_ids = count(1)
        self._item_ids = count(1)

    # --- users ---
    def get_user_by_username(self, username: str) -> Optional[dict]:
        return next((u for u in self.users.values() if u["username"] == username), None)

    def create_user(self, username: str, email: str, hashed_password: str) -> dict:
        user_id = next(self._user_ids)
        user = {"id": user_id, "username": username, "email": email, "hashed_password": hashed_password}
        self.users[user_id] = user
        return user

    # --- items ---
    def create_item(self, owner_id: int, name: str, description: str | None, price: float, quantity: int) -> dict:
        item_id = next(self._item_ids)
        item = {
            "id": item_id,
            "name": name,
            "description": description,
            "price": price,
            "quantity": quantity,
            "owner_id": owner_id,
        }
        self.items[item_id] = item
        return item

    def get_item(self, item_id: int) -> Optional[dict]:
        return self.items.get(item_id)

    def list_items(self, owner_id: int) -> list[dict]:
        return [i for i in self.items.values() if i["owner_id"] == owner_id]

    def update_item(self, item_id: int, updates: dict) -> Optional[dict]:
        item = self.items.get(item_id)
        if item is None:
            return None
        item.update({k: v for k, v in updates.items() if v is not None})
        return item

    def delete_item(self, item_id: int) -> bool:
        return self.items.pop(item_id, None) is not None


db = InMemoryDB()
