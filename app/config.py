from pydantic import SecretStr, Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class ConfigBase(BaseSettings):
    model_config = SettingsConfigDict(env_file='.env', env_file_encoding='utf-8', extra='ignore',
                                      case_sensitive=False)


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
    COOKIE_NAME: str = 'Authorization'
    ALGORITHM: str = 'HS256'
    TOKEN_EXPIRE_MINUTES: int = 60


class Settings(ConfigBase):
    IMGBB: ImgbbSettings = Field(default_factory=ImgbbSettings)
    CLOUDFLARE: CloudflareSettings = Field(default_factory=CloudflareSettings)
    AUTH: AuthSettings = Field(default_factory=AuthSettings)
    HOST: str = '127.0.0.1'
    PORT: int = 8000


SETTINGS = Settings()
