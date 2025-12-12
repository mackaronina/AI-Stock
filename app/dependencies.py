import uuid
from typing import Annotated

from fastapi import Depends, HTTPException, Request
from jwt import InvalidTokenError

from app.dao.dao import UserDAO, ImageDAO, LikeDAO
from app.database import User, Image, Like
from app.exceptions import UserNotLoggedInException, ImageNotFoundException, UserNotFoundException, \
    NoAccessToImageException, LikeNotFoundException
from app.schemas import RequestPlaceLike
from app.utils.auth import get_access_token, get_refresh_token, get_user_by_token


async def get_current_user_by_refresh_token(request: Request) -> User:
    try:
        refresh_token = get_refresh_token(request)
        user = await get_user_by_token(refresh_token, 'refresh')
        return user
    except (InvalidTokenError, UserNotFoundException, ValueError, KeyError):
        raise UserNotLoggedInException()


# Used only for token refreshes
CurrentUserRefresh = Annotated[User, Depends(get_current_user_by_refresh_token)]


async def get_current_user(request: Request) -> User:
    try:
        access_token = get_access_token(request)
        user = await get_user_by_token(access_token, 'access')
        return user
    except (InvalidTokenError, UserNotFoundException, ValueError, KeyError):
        raise UserNotLoggedInException()


# Used for endpoints that require authorization
CurrentUser = Annotated[User, Depends(get_current_user)]


async def get_current_user_or_none(request: Request) -> User | None:
    try:
        return await get_current_user(request)
    except HTTPException:
        return None


# Used for endpoints with optional authorization
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
