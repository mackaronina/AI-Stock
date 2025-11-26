import uuid
from typing import Annotated

import jwt
from fastapi import Depends, HTTPException, Request
from jwt import InvalidTokenError

from app.config import SETTINGS
from app.dao.dao import UserDAO, ImageDAO
from app.database import User, Image
from app.exceptions import UserNotLoggedInException, ImageNotFoundException, UserNotFoundException


async def get_current_user(request: Request) -> User:
    try:
        token = request.cookies.get(SETTINGS.AUTH.COOKIE_NAME)
        if not token:
            raise UserNotLoggedInException()
        payload = jwt.decode(token, SETTINGS.AUTH.SECRET_KEY.get_secret_value(), algorithms=[SETTINGS.AUTH.ALGORITHM])
        user_id = payload.get('sub')
        if user_id is None:
            raise UserNotLoggedInException()
        user = await UserDAO.find_one_or_none_by_id(uuid.UUID(user_id))
        if user is None:
            raise UserNotLoggedInException()
        return user
    except (InvalidTokenError, ValueError):
        raise UserNotLoggedInException()


CurrentUser = Annotated[User, Depends(get_current_user)]


async def get_current_user_or_none(request: Request) -> User | None:
    try:
        return await get_current_user(request)
    except HTTPException:
        return None


OptionalCurrentUser = Annotated[User | None, Depends(get_current_user_or_none)]


async def get_image_by_id(image_id: uuid.UUID, current_user: OptionalCurrentUser) -> Image:
    image = await ImageDAO.find_one_or_none_by_id(image_id)
    if not image:
        raise ImageNotFoundException()
    if not image.is_public and (current_user is None or current_user.id != image.author_id):
        raise ImageNotFoundException()
    return image


ImageById = Annotated[Image, Depends(get_image_by_id)]


async def get_user_by_id(user_id: uuid.UUID) -> User:
    user = await UserDAO.find_one_or_none_by_id(user_id)
    if not user:
        raise UserNotFoundException()
    return user


UserById = Annotated[User, Depends(get_user_by_id)]
