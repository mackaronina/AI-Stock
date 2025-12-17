import asyncio
import logging

import uvicorn
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from app.config import SETTINGS, BASE_DIR
from app.database import create_tables
from app.exception_handlers import init_exception_handlers
from app.routers import pages, images, auth, likes


async def main() -> None:
    app = FastAPI()

    app.mount('/static', StaticFiles(directory=f'{BASE_DIR}/app/static'), name='static')

    app.include_router(pages.router)
    app.include_router(images.router)
    app.include_router(auth.router)
    app.include_router(likes.router)

    init_exception_handlers(app)

    logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s %(message)s')
    logging.info('Starting server')

    await create_tables()

    await uvicorn.Server(uvicorn.Config(app, host=SETTINGS.HOST, port=SETTINGS.PORT)).serve()


if __name__ == '__main__':
    asyncio.run(main())
