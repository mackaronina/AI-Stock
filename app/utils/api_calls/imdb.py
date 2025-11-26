import base64
import logging

from curl_cffi import CurlMime
from curl_cffi.requests import AsyncSession

from app.config import SETTINGS


async def upload_image_to_imdb(img_data: str) -> str:
    logging.info('Uploading image to imdb')
    link = f'https://api.imgbb.com/1/upload?key={SETTINGS.IMDB.API_KEY.get_secret_value()}'
    multipart = CurlMime()
    multipart.addpart(
        name='image',
        content_type='image/jpeg',
        filename='image.jpeg',
        data=base64.decodebytes(bytes(img_data, 'utf-8'))
    )
    async with AsyncSession() as session:
        resp = await session.post(link, multipart=multipart, impersonate='chrome110',
                                  timeout=SETTINGS.IMDB.REQUEST_TIMEOUT_SECONDS)
        image_url = resp.json()['data']['url']
        return image_url
