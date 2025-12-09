import logging
from typing import Annotated

from fastapi import APIRouter, Query
from fastapi import Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from app.dao.dao import ImageDAO
from app.dependencies import CurrentUser, ImageById, OptionalCurrentUser, LikeByImage
from app.exceptions import GeneratingImageException, NoAccessToImageException
from app.schemas import RequestGenerateImage, RequestSearchQuery
from app.utils.api_calls.cloudflare import generate_image_from_prompt, generate_tags_for_image
from app.utils.api_calls.imgbb import upload_image_to_imgbb

router = APIRouter(prefix='/images')
templates = Jinja2Templates(directory='templates')


@router.get('/create')
async def create_image_page(current_user: CurrentUser, request: Request) -> HTMLResponse:
    return templates.TemplateResponse(request=request, name='create_image.html',
                                      context={'current_user': current_user})


@router.post('/create')
async def create_image(current_user: CurrentUser, generate_data: RequestGenerateImage, request: Request) -> dict:
    try:
        img_data = await generate_image_from_prompt(generate_data.prompt)
        tags = await generate_tags_for_image(img_data, generate_data.prompt)
        image_url = await upload_image_to_imgbb(img_data)
        image = await ImageDAO.add(url=image_url, prompt=generate_data.prompt, tags=tags, author_id=current_user.id)
        logging.info(f'Created image with id {image.id}')
        return {'image_url': str(request.url_for('get_image_page', image_id=str(image.id)))}
    except Exception as e:
        logging.error(f'Error while generating image: {e}', exc_info=True)
        raise GeneratingImageException()


@router.get('/')
async def get_all_images_page(current_user: OptionalCurrentUser, search_query: Annotated[RequestSearchQuery, Query()],
                              request: Request) -> HTMLResponse:
    images, total_pages = await ImageDAO.find_all_with_filters(sort_by=search_query.sort_by,
                                                               order_by=search_query.order_by,
                                                               term=search_query.term, page=search_query.page,
                                                               page_size=search_query.page_size, is_public=True)
    return templates.TemplateResponse(request=request, name='get_all_images.html',
                                      context={'current_user': current_user, 'images': images,
                                               'search_query': search_query, 'total_pages': total_pages})


@router.get('/{image_id}')
async def get_image_page(image: ImageById, like: LikeByImage, current_user: OptionalCurrentUser,
                         request: Request) -> HTMLResponse:
    return templates.TemplateResponse(request=request, name='get_image.html',
                                      context={'current_user': current_user, 'image': image, 'like': like})


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
