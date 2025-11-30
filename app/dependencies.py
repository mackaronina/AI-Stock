import uuid
from typing import Annotated

import jwt
from fastapi import Depends, HTTPException, Request
from jwt import InvalidTokenError

from app.config import SETTINGS
from app.dao.dao import UserDAO, ImageDAO, LikeDAO
from app.database import User, Image, Like
from app.exceptions import UserNotLoggedInException, ImageNotFoundException, UserNotFoundException, \
    NoAccessToImageException, LikeNotFoundException
from app.schemas import RequestPlaceLike


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


async def get_image_by_id(current_user: OptionalCurrentUser, image_id: uuid.UUID | None = None,
                          like_data: RequestPlaceLike | None = None) -> Image:
    image_id = image_id or like_data.to_image_id
    image = await ImageDAO.find_one_or_none_by_id(image_id)
    if not image:
        raise ImageNotFoundException()
    if not image.is_public and (current_user is None or current_user.id != image.author_id):
        raise NoAccessToImageException()
    return image


ImageById = Annotated[Image, Depends(get_image_by_id)]


async def get_user_by_id(user_id: uuid.UUID) -> User:
    user = await UserDAO.find_one_or_none_by_id(user_id)
    if not user:
        raise UserNotFoundException()
    return user


UserById = Annotated[User, Depends(get_user_by_id)]


async def get_like_by_image(image_id: uuid.UUID, current_user: OptionalCurrentUser) -> Like | None:
    if current_user is None:
        return None
    like = await LikeDAO.find_one_or_none(from_user_id=current_user.id, to_image_id=image_id)
    return like


LikeByImage = Annotated[Like | None, Depends(get_like_by_image)]


async def get_like_by_id(like_id: uuid.UUID, current_user: CurrentUser) -> Like:
    like = await LikeDAO.find_one_or_none_by_id(like_id)
    if not like:
        raise LikeNotFoundException()
    return like


LikeById = Annotated[Like, Depends(get_like_by_id)]
