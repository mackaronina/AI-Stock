import uuid
from typing import Self, Literal, Annotated

from pydantic import BaseModel, EmailStr, Field, model_validator, ConfigDict, AfterValidator


# Field description is the message that will appear when a validation error occurs
class Base(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)


def validate_search_term(value: str | None) -> str | None:
    if value is None:
        return None
    if value == 'None':
        return None
    if 3 <= len(value) <= 300:
        return value
    return None


class RequestSearchQuery(Base):
    sort_by: Literal['date', 'likes'] = 'likes'
    order_by: Literal['asc', 'desc'] = 'desc'
    term: Annotated[str | None, AfterValidator(validate_search_term)] = None
    page: int = Field(default=1, ge=1)
    page_size: int = Field(default=9, ge=1, le=100)


class RequestGenerateImage(Base):
    prompt: str = Field(min_length=3, max_length=200, description='Prompt must be between 3 and 200 characters long')


class RequestPlaceLike(Base):
    to_image_id: uuid.UUID = Field(description='The id of the image being liked must be valid')


class RequestLogin(Base):
    username: str = Field(min_length=4, max_length=20, description='Username must be between 4 and 20 characters long')
    password: str = Field(min_length=6, max_length=20, description='Password must be between 6 and 20 characters long')


class RequestRegister(Base):
    username: str = Field(min_length=4, max_length=20, description='Username must be between 4 and 20 characters long')
    email: EmailStr = Field(description='Email address must be valid')
    password: str = Field(min_length=6, max_length=20, description='Password must be between 6 and 20 characters long')
    confirm_password: str = Field(min_length=6, max_length=20,
                                  description='Password confirmation must be between 6 and 20 characters long')

    @model_validator(mode='after')
    def check_password(self) -> Self:
        if self.password != self.confirm_password:
            raise ValueError('Passwords do not match')
        return self
