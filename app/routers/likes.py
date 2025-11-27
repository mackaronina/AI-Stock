from fastapi import APIRouter

from app.dao.dao import ImageDAO, LikeDAO
from app.dependencies import CurrentUser
from app.exceptions import PlacingLikeException
from app.schemas import RequestPlaceLike

router = APIRouter(prefix='/likes')


@router.post('/place')
async def place_or_remove_like(like_data: RequestPlaceLike, current_user: CurrentUser) -> dict:
    image = await ImageDAO.find_one_or_none_by_id(like_data.to_image_id)
    if not image or not image.is_public:
        raise PlacingLikeException()
    if image.author_id == current_user.id:
        raise PlacingLikeException()
    like = await LikeDAO.find_one_or_none(from_user_id=current_user.id, to_image_id=like_data.to_image_id)
    if like is not None:
        await LikeDAO.delete_one_by_id(like.id)
    else:
        await LikeDAO.add(from_user_id=current_user.id, to_image_id=like_data.to_image_id)
    new_likes_count = len(await LikeDAO.find_all(to_image_id=like_data.to_image_id))
    return {'new_likes_count': new_likes_count}
