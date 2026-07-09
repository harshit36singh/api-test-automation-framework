from fastapi import APIRouter, status
from fastapi.security import OAuth2PasswordRequestForm
from fastapi import Depends

from app.auth import create_access_token, hash_password, verify_password
from app.database import db
from app.exceptions import APIError
from app.models import Token, UserOut, UserRegister

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=UserOut, status_code=status.HTTP_201_CREATED)
def register(payload: UserRegister) -> UserOut:
    if db.get_user_by_username(payload.username) is not None:
        raise APIError(
            error_code="USER_ALREADY_EXISTS",
            message=f"Username '{payload.username}' is already taken",
            status_code=status.HTTP_409_CONFLICT,
        )
    user = db.create_user(payload.username, payload.email, hash_password(payload.password))
    return UserOut(**user)


@router.post("/login", response_model=Token)
def login(form_data: OAuth2PasswordRequestForm = Depends()) -> Token:
    user = db.get_user_by_username(form_data.username)
    if user is None or not verify_password(form_data.password, user["hashed_password"]):
        raise APIError(
            error_code="INVALID_CREDENTIALS",
            message="Incorrect username or password",
            status_code=status.HTTP_401_UNAUTHORIZED,
        )
    access_token = create_access_token(data={"sub": user["username"]})
    return Token(access_token=access_token)
