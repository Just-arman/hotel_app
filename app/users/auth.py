from datetime import datetime, timedelta, timezone
from jose import jwt
from passlib.context import CryptContext
from pydantic import EmailStr
from fastapi import Response

from app.config import settings
from app.users.dao import UsersDAO


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain_password, hashed_password) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def set_tokens(response: Response, user_id: int) -> None:
    access_token = create_access_token({"sub": str(user_id)})
    refresh_token = create_refresh_token({"sub": str(user_id)})
    cookie_params = {"httponly": True, "secure": True, "samesite": "lax"}

    response.set_cookie("hotels_access_token", access_token, **cookie_params)
    response.set_cookie("hotels_refresh_token", refresh_token, **cookie_params)


def _create_token(data: dict, token_type: str, expires_delta: timedelta) -> str:
    to_encode = data.copy()
    expire = datetime.now(timezone.utc).replace(tzinfo=None) + expires_delta
    to_encode.update({"exp": expire, "type": token_type})
    return jwt.encode(to_encode, settings.SECRET_KEY, settings.ALGORITHM)


def create_access_token(data: dict) -> str:
    return _create_token(data, token_type="access", expires_delta=timedelta(hours=1))


def create_refresh_token(data: dict) -> str:
    return _create_token(data, token_type="refresh", expires_delta=timedelta(hours=24))


async def authenticate_user(email: EmailStr, password: str):
    user = await UsersDAO.find_one_or_none(email=email)
    if not (user and verify_password(password, user.hashed_password)):
        return None
    return user