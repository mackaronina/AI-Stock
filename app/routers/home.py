from fastapi import Request, APIRouter
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from app.dependencies import OptionalCurrentUser

router = APIRouter()
templates = Jinja2Templates(directory='templates')


@router.get('/')
async def home_page(current_user: OptionalCurrentUser, request: Request) -> HTMLResponse:
    return templates.TemplateResponse(request=request, name='home.html', context={'current_user': current_user})
