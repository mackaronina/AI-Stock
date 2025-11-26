from app.dao.base import BaseDAO
from app.database import User, Image, Like


class UserDAO(BaseDAO[User]):
    model = User


class ImageDAO(BaseDAO[Image]):
    model = Image


class LikeDAO(BaseDAO[Like]):
    model = Like
