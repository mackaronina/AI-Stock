import inspect
import logging

from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse, RedirectResponse
from fastapi.templating import Jinja2Templates

from app.exceptions import UserNotLoggedInException

templates = Jinja2Templates(directory='templates')


def init_exception_handlers(app: FastAPI) -> None:
    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(request: Request, exc: RequestValidationError):
        error = exc.errors()[0]
        logging.warning(f'Validation error: {error}')
        route_handler = request.scope['route'].endpoint
        sig = inspect.signature(route_handler)
        model = None
        for param in sig.parameters.values():
            if hasattr(param.annotation, 'model_fields'):  # Check if it's a Pydantic model
                model = param.annotation
                break
        field_name = error['loc'][-1]
        field_info = model.model_fields.get(field_name) if model else None
        custom_message = field_info.description if field_info and field_info.description else error['msg']
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content={'detail': custom_message}
        )

    @app.exception_handler(UserNotLoggedInException)
    async def not_logged_exception_handler(request: Request, exc: UserNotLoggedInException) -> RedirectResponse:
        return RedirectResponse(request.url_for('login_user_page'))
