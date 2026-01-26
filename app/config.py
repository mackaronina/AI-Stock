from pathlib import Path

from pydantic import SecretStr, Field
from pydantic_settings import BaseSettings, SettingsConfigDict

BASE_DIR = Path(__file__).resolve().parent.parent


class ConfigBase(BaseSettings):
    model_config = SettingsConfigDict(env_file=f'{BASE_DIR}/.env', env_file_encoding='utf-8', extra='ignore',
                                      case_sensitive=False)


class PostgresSettings(ConfigBase):
    model_config = SettingsConfigDict(env_prefix='POSTGRES_')
    USER: str
    PASSWORD: SecretStr
    HOST: str
    PORT: int
    NAME: str

    def get_url(self) -> str:
        return (f'postgresql+asyncpg://{self.USER}:{self.PASSWORD.get_secret_value()}'
                f'@{self.HOST}:{self.PORT}/{self.NAME}')


class ImgbbSettings(ConfigBase):
    model_config = SettingsConfigDict(env_prefix='IMGBB_')
    API_KEY: SecretStr
    REQUEST_TIMEOUT_SECONDS: int = 60


class CloudflareSettings(ConfigBase):
    model_config = SettingsConfigDict(env_prefix='CLOUDFLARE_')
    API_KEY: SecretStr
    ACCOUNT_ID: str
    IMAGES_MODEL_NAME: str = '@cf/leonardo/lucid-origin'
    TAGS_MODEL_NAME: str = '@cf/meta/llama-4-scout-17b-16e-instruct'
    IMAGE_HEIGHT: int = 1024
    IMAGE_WIDTH: int = 768
    REQUEST_TIMEOUT_SECONDS: int = 60


class AuthSettings(ConfigBase):
    model_config = SettingsConfigDict(env_prefix='AUTH_')
    SECRET_KEY: SecretStr
    ACCESS_TOKEN_COOKIE_NAME: str = 'user_access_token'
    REFRESH_TOKEN_COOKIE_NAME: str = 'user_refresh_token'
    ALGORITHM: str = 'HS256'
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7


class Settings(ConfigBase):
    POSTGRES: PostgresSettings = Field(default_factory=PostgresSettings)
    IMGBB: ImgbbSettings = Field(default_factory=ImgbbSettings)
    CLOUDFLARE: CloudflareSettings = Field(default_factory=CloudflareSettings)
    AUTH: AuthSettings = Field(default_factory=AuthSettings)
    GENERATIONS_PER_DAY: int = 5
    TIME_ZONE: str = 'UTC'
    USE_SQLITE: bool = False
    SQLITE_URL: str = 'sqlite+aiosqlite:///db.sqlite3'
    HOST: str = '0.0.0.0'
    PORT: int = 8000


SETTINGS = Settings()
