from fastapi import Depends, Request
from jose import ExpiredSignatureError, JWTError, jwt

from app.config import settings
from app.exceptions import (
    IncorrectTokenFormatException,
    TokenAbsentException,
    TokenExpiredException,
    UserIsNotPresentException,
)
from app.users.dao import UserDAO
from app.logger import log
from app.users.models import Users


def get_token(request: Request):
    token = request.cookies.get("booking_access_token")
    # log.debug(f"Токен: {token}")
    if not token:
        raise TokenAbsentException
    return token


async def get_current_user(token: str = Depends(get_token)):
    try:
        payload = jwt.decode(
            token, settings.SECRET_KEY, settings.ALGORITHM
        )
    except ExpiredSignatureError:
        # Как позже выяснилось, ключ exp автоматически проверяется
        # командой jwt.decode, поэтому отдельно проверять это не нужно
        raise TokenExpiredException
    except JWTError:
        raise IncorrectTokenFormatException
    user_id: str = payload.get("sub")
    if not user_id:
        raise UserIsNotPresentException
    user = await UserDAO.find_one_or_none(id=int(user_id))
    if not user:
        raise UserIsNotPresentException
    return user


async def get_current_admin_user(current_user: Users = Depends(get_current_user)):
    # if current_user.role != "admin":
    #     raise UserIsNotPresentException
    return current_user
