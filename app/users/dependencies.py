from fastapi import Depends, Request
from jose import ExpiredSignatureError, JWTError, jwt

from app.config import settings
from app.exceptions import (
    IncorrectTokenFormatException,
    IncorrectTokenTypeException,
    TokenAbsentException,
    TokenExpiredException,
    UserIsNotAdminException,
    UserIsNotPresentException,
)
from app.users.dao import UsersDAO
from app.logger import log
from app.users.models import Users


def get_access_token(request: Request):
    token = request.cookies.get("hotels_access_token")
    # log.debug(f"Токен: {token}")
    if not token:
        raise TokenAbsentException
    return token


def get_refresh_token(request: Request):
    token = request.cookies.get("hotels_refresh_token")
    if not token:
        raise TokenAbsentException
    return token


async def _get_user_from_token(token: str, expected_type: str) -> Users:
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, settings.ALGORITHM)
    except ExpiredSignatureError:
        raise TokenExpiredException
    except JWTError:
        raise IncorrectTokenFormatException

    if payload.get("type") != expected_type:
        raise IncorrectTokenTypeException

    user_id = payload.get("sub")
    # log.debug(f"{user_id=}")
    if not user_id:
        raise UserIsNotPresentException

    user = await UsersDAO.find_one_or_none(id=int(user_id))
    if not user:
        raise UserIsNotPresentException
    return user


async def get_current_user(token: str = Depends(get_access_token)) -> Users:
    return await _get_user_from_token(token, expected_type="access")


async def check_refresh_token(token: str = Depends(get_refresh_token)) -> Users:
    return await _get_user_from_token(token, expected_type="refresh")


async def get_current_admin_user(current_user: Users = Depends(get_current_user)):
    if current_user.role.name != "Admin":
        raise UserIsNotAdminException
    return current_user
