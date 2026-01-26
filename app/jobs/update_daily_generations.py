import logging

from app.dao.dao import UserDAO


async def job_update_daily_generations() -> None:
    await UserDAO.update_daily_generations()
    logging.info('Daily generations updated for all users')
