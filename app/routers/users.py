from fastapi import Response, APIRouter, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates

from app.config import SETTINGS
from app.dao.dao import UserDAO
from app.dependencies import CurrentUser, OptionalCurrentUser, UserById
from app.exceptions import UsernameTakenException, EmailTakenException
from app.schemas import RequestLogin, RequestRegister
from app.utils.auth import authenticate_user, create_access_token, get_password_hash

router = APIRouter(prefix='/users')
templates = Jinja2Templates(directory='templates')


@router.post('/login')
async def login_user(login_data: RequestLogin, response: Response) -> dict:
    user = await authenticate_user(login_data.username, login_data.password)
    access_token = create_access_token(user)
    response.set_cookie(key=SETTINGS.AUTH.COOKIE_NAME, value=access_token)
    return {'message': 'successfully logged in'}


@router.get('/login')
async def login_user_page(current_user: OptionalCurrentUser, request: Request) -> HTMLResponse:
    return templates.TemplateResponse(request=request, name='login_user.html', context={'current_user': current_user})


@router.post('/logout')
async def logout_user(response: Response) -> dict:
    response.delete_cookie(key=SETTINGS.AUTH.COOKIE_NAME)
    return {'message': 'successfully logged out'}


@router.post('/register')
async def register_user(register_data: RequestRegister) -> dict:
    if await UserDAO.find_one_or_none(username=register_data.username):
        raise UsernameTakenException()
    if await UserDAO.find_one_or_none(email=register_data.email):
        raise EmailTakenException()
    await UserDAO.add(username=register_data.username, email=register_data.email,
                      hashed_password=get_password_hash(register_data.password))
    return {'message': 'successfully registered new user'}


@router.get('/register')
async def register_user_page(current_user: OptionalCurrentUser, request: Request) -> HTMLResponse:
    return templates.TemplateResponse(request=request, name='register_user.html',
                                      context={'current_user': current_user})


@router.delete('/delete')
async def delete_user(current_user: CurrentUser) -> dict:
    await UserDAO.delete_one_by_id(current_user.id)
    return {'message': 'successfully deleted user'}


@router.get('/me')
async def get_me_page(current_user: CurrentUser, request: Request) -> HTMLResponse:
    return templates.TemplateResponse(request=request, name='get_me.html', context={'current_user': current_user})


@router.get('/{user_id}')
async def get_user_page(user: UserById, current_user: OptionalCurrentUser, request: Request) -> HTMLResponse:
    if current_user is not None and user.id == current_user.id:
        return RedirectResponse(request.url_for('get_me_page'))
    return templates.TemplateResponse(request=request, name='get_user.html',
                                      context={'current_user': current_user, 'user': user})
