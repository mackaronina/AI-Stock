from typing import Literal, Sequence

from sqlalchemy import select, desc, asc, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.dao.base import BaseDAO
from app.database import User, Image, Like, connection


class UserDAO(BaseDAO[User]):
    model = User


class ImageDAO(BaseDAO[Image]):
    model = Image

    @classmethod
    @connection
    async def find_all_with_filters(cls, session: AsyncSession, sort_by: Literal['date', 'likes'] = 'likes',
                                    order_by: Literal['asc', 'desc'] = 'desc', term: str = None,
                                    **filter_by) -> Sequence[Image]:
        query = select(Image).filter_by(**filter_by)
        if term is not None:
            if term.startswith('#'):
                query = query.where(Image.tags.contains(term))
            else:
                query = query.where(Image.prompt.contains(term))
        if sort_by == 'date':
            if order_by == 'desc':
                query = query.order_by(desc(Image.created_at))
            else:
                query = query.order_by(asc(Image.created_at))
        elif sort_by == 'likes':
            if order_by == 'desc':
                query = query.outerjoin(Like).group_by(Image.id).order_by(
                    desc(func.count(Like.id)))
            else:
                query = query.filter_by(**filter_by).outerjoin(Like).group_by(Image.id).order_by(
                    asc(func.count(Like.id)))
        result = await session.execute(query)
        records = result.scalars().all()
        return records


class LikeDAO(BaseDAO[Like]):
    model = Like
