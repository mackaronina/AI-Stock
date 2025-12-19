import base64
import logging

from aiohttp import ClientSession, FormData, ClientTimeout

from app.config import SETTINGS


async def upload_image_to_imgbb(img_data: str) -> str:
    logging.info('Uploading image to imgbb')
    link = f'https://api.imgbb.com/1/upload?key={SETTINGS.IMGBB.API_KEY.get_secret_value()}'
    data = FormData()
    data.add_field(
        name='image',
        content_type='image/jpeg',
        filename='image.jpeg',
        value=base64.decodebytes(bytes(img_data, 'utf-8'))
    )
    async with ClientSession() as session:
        resp = await session.post(link, data=data,
                                  timeout=ClientTimeout(total=SETTINGS.CLOUDFLARE.REQUEST_TIMEOUT_SECONDS))
        json = await resp.json()
        image_url = json['data']['url']
        return image_url
