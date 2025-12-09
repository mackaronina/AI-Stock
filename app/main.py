import asyncio
import logging

import uvicorn
from fastapi import FastAPI

from app.config import SETTINGS
from app.database import create_tables
from app.exception_handlers import init_exception_handlers
from app.routers import home, images, users, likes


async def main() -> None:
    app = FastAPI()

    app.include_router(home.router)
    app.include_router(images.router)
    app.include_router(users.router)
    app.include_router(likes.router)

    init_exception_handlers(app)

    logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s %(message)s')
    logging.info('Starting server')

    await create_tables()

    await uvicorn.Server(uvicorn.Config(app, host=SETTINGS.HOST, port=SETTINGS.PORT)).serve()


if __name__ == '__main__':
    asyncio.run(main())
