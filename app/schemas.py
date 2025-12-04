import uuid
from typing import Self, Literal

from pydantic import BaseModel, EmailStr, Field, model_validator


# Field description is the message that will appear when a validation error occurs
class RequestSearchQuery(BaseModel):
    sort_by: Literal['date', 'likes'] = 'likes'
    order_by: Literal['asc', 'desc'] = 'desc'


class RequestGenerateImage(BaseModel):
    prompt: str = Field(min_length=3, max_length=200, description='Prompt must be between 3 and 200 characters long')


class RequestPlaceLike(BaseModel):
    to_image_id: uuid.UUID = Field(description='The id of the image being liked must be valid')


class RequestLogin(BaseModel):
    username: str = Field(min_length=4, max_length=20, description='Username must be between 4 and 20 characters long')
    password: str = Field(min_length=6, max_length=20, description='Password must be between 6 and 20 characters long')


class RequestRegister(BaseModel):
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
