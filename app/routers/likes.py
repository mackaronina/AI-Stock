import logging

from fastapi import APIRouter

from app.dao.dao import LikeDAO
from app.dependencies import CurrentUser, ImageById, LikeById
from app.exceptions import PlacingLikeException, LikeAlreadyPlacedException, NoAccessToLikeException
from app.schemas import RequestPlaceLike

router = APIRouter(prefix='/api/likes')


@router.post('/place')
async def place_like(image: ImageById, like_data: RequestPlaceLike, current_user: CurrentUser) -> dict:
    if image.author_id == current_user.id:
        raise PlacingLikeException()
    like = await LikeDAO.find_one_or_none(from_user_id=current_user.id, to_image_id=like_data.to_image_id)
    if like is not None:
        raise LikeAlreadyPlacedException()
    like = await LikeDAO.add(from_user_id=current_user.id, to_image_id=like_data.to_image_id)
    logging.info(
        f'Placed like with id {like.id} by user with id {like.from_user_id} on image with id {like.to_image_id}')
    return {'message': 'successfully placed like'}


@router.delete('/delete/{like_id}')
async def delete_like(like: LikeById, current_user: CurrentUser) -> dict:
    if like.from_user_id != current_user.id:
        raise NoAccessToLikeException()
    await LikeDAO.delete_one_by_id(like.id)
    logging.info(
        f'Deleted like with id {like.id} by user with id {like.from_user_id} on image with id {like.to_image_id}')
    return {'message': 'successfully deleted like'}
