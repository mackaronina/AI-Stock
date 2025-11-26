from datetime import datetime, timezone, timedelta

import jwt
from passlib.context import CryptContext

from app.config import SETTINGS
from app.dao.dao import UserDAO
from app.database import User
from app.exceptions import CredentialsException

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
    expire = datetime.now(timezone.utc) + timedelta(minutes=SETTINGS.AUTH.TOKEN_EXPIRE_MINUTES)
    data = {'sub': str(user.id), 'exp': expire}
    encoded_jwt = jwt.encode(data, SETTINGS.AUTH.SECRET_KEY.get_secret_value(), algorithm=SETTINGS.AUTH.ALGORITHM)
    return encoded_jwt
