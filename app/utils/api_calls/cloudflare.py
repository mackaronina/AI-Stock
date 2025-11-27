import logging

from curl_cffi.requests import AsyncSession

from app.config import SETTINGS


async def generate_image_from_prompt(prompt: str) -> str:
    logging.info(f'Generating image with prompt: {prompt}')
    link = f'https://api.cloudflare.com/client/v4/accounts/{SETTINGS.CLOUDFLARE.ACCOUNT_ID}/ai/run/{SETTINGS.CLOUDFLARE.IMAGES_MODEL_NAME}'
    headers = {
        'Authorization': f'Bearer {SETTINGS.CLOUDFLARE.API_KEY.get_secret_value()}'
    }
    data = {
        'prompt': prompt,
        'height': SETTINGS.CLOUDFLARE.IMAGE_HEIGHT,
        'width': SETTINGS.CLOUDFLARE.IMAGE_WIDTH,
    }
    async with AsyncSession() as session:
        resp = await session.post(link, json=data, headers=headers, impersonate='chrome110',
                                  timeout=SETTINGS.CLOUDFLARE.REQUEST_TIMEOUT_SECONDS)
        img_data = resp.json()['result']['image']
        return img_data


async def generate_tags_for_image(img_data: str) -> list[str]:
    logging.info('Generating tags for image')
    link = f'https://api.cloudflare.com/client/v4/accounts/{SETTINGS.CLOUDFLARE.ACCOUNT_ID}/ai/run/{SETTINGS.CLOUDFLARE.TAGS_MODEL_NAME}'
    headers = {
        'Authorization': f'Bearer {SETTINGS.CLOUDFLARE.API_KEY.get_secret_value()}'
    }
    data = {
        'messages': [
            {
                'role': 'system',
                'content': 'Generate a list of tags for the image. The list must contain 1 to 10 tags. Each tag must begin with #'
            },
            {
                'role': 'user',
                'content': [
                    {
                        'type': 'image_url',
                        'image_url': {
                            'url': f'data:image/jpeg;base64,{img_data}'
                        }
                    }
                ]
            }
        ],
        'response_format': {
            'type': 'json_schema',
            'json_schema': {
                'type': 'object',
                'properties': {
                    'tags': {
                        'type': 'array',
                        'items': {
                            'type': 'string'
                        }
                    }
                },
                'required': [
                    'tags'
                ]
            }
        }
    }
    async with AsyncSession() as session:
        resp = await session.post(link, json=data, headers=headers, impersonate='chrome110',
                                  timeout=SETTINGS.CLOUDFLARE.REQUEST_TIMEOUT_SECONDS)
        tags = resp.json()['result']['response']['tags']
        tags = [tag.lower().replace(' ', '_').replace('-', '_') for tag in tags]
        return tags
