import uuid
from datetime import datetime, timezone, timedelta

import jwt
from fastapi import Response, Request
from jwt import InvalidTokenError
from passlib.context import CryptContext

from app.config import SETTINGS
from app.dao.dao import UserDAO
from app.database import User
from app.exceptions import CredentialsException, UserNotFoundException

pwd_context = CryptContext(schemes=['bcrypt'], deprecated='auto')


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)


async def authenticate_user(username: str, password: str) -> User:
    user = await UserDAO.find_one_or_none(username=username)
    if not user:
        raise CredentialsException()
    if not verify_password(password, user.hashed_password):
        raise CredentialsException()
    return user


def create_access_token(user: User) -> str:
    expire = datetime.now(timezone.utc) + timedelta(minutes=SETTINGS.AUTH.ACCESS_TOKEN_EXPIRE_MINUTES)
    data = {'sub': str(user.id), 'exp': expire, 'type': 'access'}
    encoded_jwt = jwt.encode(data, SETTINGS.AUTH.SECRET_KEY.get_secret_value(), algorithm=SETTINGS.AUTH.ALGORITHM)
    return encoded_jwt


def create_refresh_token(user: User) -> str:
    expire = datetime.now(timezone.utc) + timedelta(days=SETTINGS.AUTH.REFRESH_TOKEN_EXPIRE_DAYS)
    data = {'sub': str(user.id), 'exp': expire, 'type': 'refresh'}
    encoded_jwt = jwt.encode(data, SETTINGS.AUTH.SECRET_KEY.get_secret_value(), algorithm=SETTINGS.AUTH.ALGORITHM)
    return encoded_jwt


async def get_user_by_token(token: str, token_type: str) -> User:
    payload = jwt.decode(token, SETTINGS.AUTH.SECRET_KEY.get_secret_value(),
                         algorithms=[SETTINGS.AUTH.ALGORITHM])
    if payload['type'] != token_type:
        raise InvalidTokenError()
    user_id = payload['sub']
    user = await UserDAO.find_one_or_none_by_id(uuid.UUID(user_id))
    if user is None:
        raise UserNotFoundException()
    return user


# The following methods can be modified to store tokens in headers

def delete_access_token(response: Response) -> None:
    response.delete_cookie(key=SETTINGS.AUTH.ACCESS_TOKEN_COOKIE_NAME)


def delete_refresh_token(response: Response) -> None:
    response.delete_cookie(key=SETTINGS.AUTH.REFRESH_TOKEN_COOKIE_NAME)


def set_access_token(user: User, response: Response) -> None:
    access_token = create_access_token(user)
    response.set_cookie(key=SETTINGS.AUTH.ACCESS_TOKEN_COOKIE_NAME, value=access_token, httponly=True)


def set_refresh_token(user: User, response: Response) -> None:
    refresh_token = create_refresh_token(user)
    response.set_cookie(key=SETTINGS.AUTH.REFRESH_TOKEN_COOKIE_NAME, value=refresh_token, httponly=True)


def get_access_token(request: Request) -> str:
    return request.cookies[SETTINGS.AUTH.ACCESS_TOKEN_COOKIE_NAME]


def get_refresh_token(request: Request) -> str:
    return request.cookies[SETTINGS.AUTH.REFRESH_TOKEN_COOKIE_NAME]
