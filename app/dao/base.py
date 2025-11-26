import uuid
from typing import TypeVar, Generic, Sequence

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import connection, Base

T = TypeVar('T', bound=Base)


# DAO - Data Access Object
class BaseDAO(Generic[T]):
    model: type[T]

    @classmethod
    @connection
    async def add(cls, session: AsyncSession, **values) -> T:
        new_instance = cls.model(**values)
        session.add(new_instance)
        return new_instance

    @classmethod
    @connection
    async def find_one_or_none_by_id(cls, data_id: uuid.UUID, session: AsyncSession) -> T | None:
        record = await session.get(cls.model, data_id)
        return record

    @classmethod
    @connection
    async def find_one_or_none(cls, session: AsyncSession, **filter_by) -> T | None:
        query = select(cls.model).filter_by(**filter_by)
        result = await session.execute(query)
        record = result.scalar_one_or_none()
        return record

    @classmethod
    @connection
    async def find_all(cls, session: AsyncSession, **filter_by) -> Sequence[T]:
        query = select(cls.model).filter_by(**filter_by)
        result = await session.execute(query)
        records = result.scalars().all()
        return records

    @classmethod
    @connection
    async def delete_one_by_id(cls, data_id: uuid.UUID, session: AsyncSession) -> None:
        data = await session.get(cls.model, data_id)
        if data:
            await session.delete(data)
