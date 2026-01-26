import uuid
from typing import Literal, Sequence

from sqlalchemy import select, desc, asc, func, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import SETTINGS
from app.dao.base import BaseDAO
from app.database import User, Image, Like, connection, Tag


class UserDAO(BaseDAO[User]):
    model = User

    @classmethod
    @connection
    async def update_daily_generations(cls, session: AsyncSession) -> None:
        await session.execute(update(User).values(generations_left=SETTINGS.GENERATIONS_PER_DAY))

    @classmethod
    @connection
    async def decrease_generations_by_id(cls, user_id: uuid.UUID, session: AsyncSession) -> int | None:
        user = await cls.find_one_or_none_by_id(user_id, session=session)
        if user is None:
            return None
        user.generations_left -= 1
        return int(user.generations_left)


class ImageDAO(BaseDAO[Image]):
    model = Image

    @classmethod
    @connection
    async def find_all_with_filters(cls, session: AsyncSession, sort_by: Literal['date', 'likes'] = 'likes',
                                    order_by: Literal['asc', 'desc'] = 'desc', term: str = None, page: int = 1,
                                    page_size: int = 9, **filter_by) -> tuple[Sequence[Image], int]:
        query = select(Image).filter_by(**filter_by)
        order_function = desc if order_by == 'desc' else asc
        if term is not None:
            if term.startswith('#'):
                query = query.join(Image.tags).where(Tag.name == term)
            else:
                query = query.where(Image.prompt.contains(term))
        if sort_by == 'date':
            query = query.order_by(order_function(Image.created_at))
        elif sort_by == 'likes':
            query = query.outerjoin(Like).group_by(Image.id).order_by(order_function(func.count(Like.id)))
        count_query = select(func.count()).select_from(query.subquery())
        total_results = await session.scalar(count_query)
        total_pages = (total_results + page_size - 1) // page_size
        offset = (page - 1) * page_size
        paginated_query = query.offset(offset).limit(page_size)
        result = await session.execute(paginated_query)
        records = result.scalars().unique().all()
        return records, total_pages

    @classmethod
    @connection
    async def change_visibility_by_id(cls, image_id: uuid.UUID, session: AsyncSession) -> bool | None:
        image = await cls.find_one_or_none_by_id(image_id, session=session)
        if image is None:
            return None
        image.is_public = not image.is_public
        return bool(image.is_public)

    @classmethod
    @connection
    async def create_tags_for_image_by_id(cls, image_id: uuid.UUID, tag_names: list[str],
                                          session: AsyncSession) -> None:
        image = await cls.find_one_or_none_by_id(image_id, session=session)
        if image is None:
            return
        for tag_name in tag_names:
            tag = await TagDAO.find_one_or_none(name=tag_name, session=session)
            if tag is None:
                tag = await TagDAO.add(name=tag_name, session=session)
            image.tags.append(tag)


class TagDAO(BaseDAO[Tag]):
    model = Tag


class LikeDAO(BaseDAO[Like]):
    model = Like
