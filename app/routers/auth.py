import logging

from fastapi import Response, APIRouter

from app.dao.dao import UserDAO
from app.dependencies import CurrentUser, CurrentUserRefresh
from app.exceptions import UsernameTakenException, EmailTakenException
from app.schemas import RequestLogin, RequestRegister
from app.utils.auth import authenticate_user, get_password_hash, set_access_token, \
    set_refresh_token, delete_access_token, delete_refresh_token

router = APIRouter(prefix='/api/auth')


@router.post('/login')
async def login_user(login_data: RequestLogin, response: Response) -> dict:
    user = await authenticate_user(login_data.username, login_data.password)
    set_access_token(user, response)
    set_refresh_token(user, response)
    logging.info(f'Logged in user with id {user.id}')
    return {'message': 'successfully logged in'}


@router.post('/logout')
async def logout_user(response: Response) -> dict:
    delete_access_token(response)
    delete_refresh_token(response)
    return {'message': 'successfully logged out'}


@router.post('/register')
async def register_user(register_data: RequestRegister) -> dict:
    if await UserDAO.find_one_or_none(username=register_data.username):
        raise UsernameTakenException()
    if await UserDAO.find_one_or_none(email=register_data.email):
        raise EmailTakenException()
    user = await UserDAO.add(username=register_data.username, email=register_data.email,
                             hashed_password=get_password_hash(register_data.password))
    logging.info(f'Registered user with id {user.id}')
    return {'message': 'successfully registered new user'}


@router.delete('/delete')
async def delete_user(current_user: CurrentUser) -> dict:
    await UserDAO.delete_one_by_id(current_user.id)
    logging.info(f'Deleted user with id {current_user.id}')
    return {'message': 'successfully deleted user'}


@router.post('/refresh')
async def refresh_tokens(response: Response, current_user: CurrentUserRefresh) -> dict:
    set_access_token(current_user, response)
    set_refresh_token(current_user, response)
    logging.info(f'Updated tokens for user with id {current_user.id}')
    return {'message': 'successfully logged out'}
