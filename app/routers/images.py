import logging

from fastapi import APIRouter
from fastapi import Request

from app.dao.dao import ImageDAO
from app.dependencies import CurrentUser, ImageById
from app.exceptions import GeneratingImageException, NoAccessToImageException
from app.schemas import RequestGenerateImage
from app.utils.api_calls.cloudflare import generate_image_from_prompt, generate_tags_for_image
from app.utils.api_calls.imgbb import upload_image_to_imgbb

router = APIRouter(prefix='/api/images')


@router.post('/create')
async def create_image(current_user: CurrentUser, generate_data: RequestGenerateImage, request: Request) -> dict:
    try:
        img_data = await generate_image_from_prompt(generate_data.prompt)
        tag_names = await generate_tags_for_image(img_data, generate_data.prompt)
        image_url = await upload_image_to_imgbb(img_data)
        image = await ImageDAO.add(url=image_url, prompt=generate_data.prompt, author_id=current_user.id)
        logging.info(f'Created image with id {image.id}')
        await ImageDAO.create_tags_for_image_by_id(image.id, tag_names)
        logging.info(f'Created tags for image with id {image.id}')
        return {'image_url': str(request.url_for('get_image_page', image_id=str(image.id)))}
    except Exception as e:
        logging.error(f'Error while generating image: {e}', exc_info=True)
        raise GeneratingImageException()


@router.delete('/delete/{image_id}')
async def delete_image(image: ImageById, current_user: CurrentUser) -> dict:
    if image.author_id != current_user.id:
        raise NoAccessToImageException()
    await ImageDAO.delete_one_by_id(image.id)
    logging.info(f'Deleted image with id {image.id}')
    return {'message': 'successfully deleted image'}


@router.patch('/visibility/{image_id}')
async def change_image_visibility(image: ImageById, current_user: CurrentUser) -> dict:
    if image.author_id != current_user.id:
        raise NoAccessToImageException()
    is_public = await ImageDAO.change_visibility_by_id(image.id)
    logging.info(f'Changed visibility of image with id {image.id}. is_public = {is_public}')
    return {'message': 'successfully changed image visibility'}
