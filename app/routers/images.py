from fastapi import APIRouter
from fastapi import Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from app.dao.dao import ImageDAO
from app.dependencies import CurrentUser, ImageById, OptionalCurrentUser
from app.exceptions import GeneratingImageException, ChangingVisibilityImageException
from app.schemas import RequestGenerateImage
from app.utils.api_calls.cloudflare import generate_image_from_prompt, generate_tags_for_image
from app.utils.api_calls.imdb import upload_image_to_imdb

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
        tags = await generate_tags_for_image(img_data)
        image_url = await upload_image_to_imdb(img_data)
        image = await ImageDAO.add(url=image_url, prompt=generate_data.prompt, tags=tags, author_id=current_user.id)
        return {'image_url': str(request.url_for('get_image_page', image_id=str(image.id)))}
    except:
        raise GeneratingImageException()


@router.get('/')
async def get_all_images_page(current_user: OptionalCurrentUser, request: Request) -> HTMLResponse:
    images = await ImageDAO.find_all()
    return templates.TemplateResponse(request=request, name='get_all_images.html',
                                      context={'current_user': current_user, 'images': images})


@router.get('/{image_id}')
async def get_image_page(image: ImageById, current_user: OptionalCurrentUser, request: Request) -> HTMLResponse:
    return templates.TemplateResponse(request=request, name='get_image.html',
                                      context={'current_user': current_user, 'image': image})


@router.patch('/visibility/{image_id}')
async def change_image_visibility(image: ImageById, current_user: CurrentUser) -> dict:
    if image.author_id != current_user.id:
        raise ChangingVisibilityImageException()
    await ImageDAO.update_one_by_id(image.id, is_public=not image.is_public)
    return {'message': 'successfully changed image visibility'}
