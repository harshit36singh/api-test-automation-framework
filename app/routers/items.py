from fastapi import APIRouter, Depends, status

from app.auth import get_current_user
from app.database import db
from app.exceptions import APIError
from app.models import ItemCreate, ItemOut, ItemUpdate

router = APIRouter(prefix="/items", tags=["items"])


def _get_owned_item(item_id: int, current_user: dict) -> dict:
    item = db.get_item(item_id)
    if item is None:
        raise APIError(
            error_code="ITEM_NOT_FOUND",
            message=f"Item with id {item_id} was not found",
            status_code=status.HTTP_404_NOT_FOUND,
        )
    if item["owner_id"] != current_user["id"]:
        raise APIError(
            error_code="ITEM_ACCESS_FORBIDDEN",
            message="You do not have access to this item",
            status_code=status.HTTP_403_FORBIDDEN,
        )
    return item


@router.post("", response_model=ItemOut, status_code=status.HTTP_201_CREATED)
def create_item(payload: ItemCreate, current_user: dict = Depends(get_current_user)) -> ItemOut:
    item = db.create_item(current_user["id"], payload.name, payload.description, payload.price, payload.quantity)
    return ItemOut(**item)


@router.get("", response_model=list[ItemOut])
def list_items(current_user: dict = Depends(get_current_user)) -> list[ItemOut]:
    return [ItemOut(**item) for item in db.list_items(current_user["id"])]


@router.get("/{item_id}", response_model=ItemOut)
def get_item(item_id: int, current_user: dict = Depends(get_current_user)) -> ItemOut:
    item = _get_owned_item(item_id, current_user)
    return ItemOut(**item)


@router.put("/{item_id}", response_model=ItemOut)
def update_item(item_id: int, payload: ItemUpdate, current_user: dict = Depends(get_current_user)) -> ItemOut:
    _get_owned_item(item_id, current_user)
    updated = db.update_item(item_id, payload.model_dump())
    return ItemOut(**updated)


@router.delete("/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_item(item_id: int, current_user: dict = Depends(get_current_user)) -> None:
    _get_owned_item(item_id, current_user)
    db.delete_item(item_id)
