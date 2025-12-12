from fastapi import Request, APIRouter
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates

from app.config import BASE_DIR
from app.dao.dao import ImageDAO
from app.dependencies import OptionalCurrentUser, CurrentUser, UserById, ImageById, LikeByImage
from app.schemas import SearchQuery

router = APIRouter()
templates = Jinja2Templates(directory=f'{BASE_DIR}/app/templates')


@router.get('/')
async def home_page(current_user: OptionalCurrentUser, request: Request) -> HTMLResponse:
    return templates.TemplateResponse(request=request, name='home.html', context={'current_user': current_user})


@router.get('/users/me')
async def get_me_page(current_user: CurrentUser, request: Request) -> HTMLResponse:
    return templates.TemplateResponse(request=request, name='get_me.html', context={'current_user': current_user})


@router.get('/users/login')
async def login_user_page(current_user: OptionalCurrentUser, request: Request) -> HTMLResponse:
    return templates.TemplateResponse(request=request, name='login_user.html', context={'current_user': current_user})


@router.get('/users/register')
async def register_user_page(current_user: OptionalCurrentUser, request: Request) -> HTMLResponse:
    return templates.TemplateResponse(request=request, name='register_user.html',
                                      context={'current_user': current_user})


@router.get('/users/{user_id}')
async def get_user_page(user: UserById, current_user: OptionalCurrentUser, request: Request) -> HTMLResponse:
    if current_user is not None and user.id == current_user.id:
        return RedirectResponse(request.url_for('get_me_page'))
    return templates.TemplateResponse(request=request, name='get_user.html',
                                      context={'current_user': current_user, 'user': user})


@router.get('/images/create')
async def create_image_page(current_user: CurrentUser, request: Request) -> HTMLResponse:
    return templates.TemplateResponse(request=request, name='create_image.html',
                                      context={'current_user': current_user})


@router.get('/images')
async def get_all_images_page(current_user: OptionalCurrentUser, search_query: SearchQuery,
                              request: Request) -> HTMLResponse:
    images, total_pages = await ImageDAO.find_all_with_filters(sort_by=search_query.sort_by,
                                                               order_by=search_query.order_by,
                                                               term=search_query.term, page=search_query.page,
                                                               page_size=search_query.page_size, is_public=True)
    return templates.TemplateResponse(request=request, name='get_all_images.html',
                                      context={'current_user': current_user, 'images': images,
                                               'search_query': search_query, 'total_pages': total_pages})


@router.get('/images/{image_id}')
async def get_image_page(image: ImageById, like: LikeByImage, current_user: OptionalCurrentUser,
                         request: Request) -> HTMLResponse:
    return templates.TemplateResponse(request=request, name='get_image.html',
                                      context={'current_user': current_user, 'image': image, 'like': like})
