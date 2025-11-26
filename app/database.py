import uuid
from collections.abc import Callable
from datetime import datetime
from typing import Any

from sqlalchemy import func, ForeignKey, JSON, UniqueConstraint
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncAttrs
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship

engine = create_async_engine('sqlite+aiosqlite:///db.sqlite3')

async_session = async_sessionmaker(engine, expire_on_commit=False)


class Base(AsyncAttrs, DeclarativeBase):
    __abstract__ = True
    type_annotation_map = {
        list[str]: JSON
    }
    id: Mapped[uuid.UUID] = mapped_column(insert_default=uuid.uuid4, primary_key=True)
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(server_default=func.now(), onupdate=func.now())


class User(Base):
    __tablename__ = 'users'
    username: Mapped[str] = mapped_column(unique=True)
    email: Mapped[str] = mapped_column(unique=True)
    hashed_password: Mapped[str]
    images: Mapped[list['Image']] = relationship(back_populates='author', cascade='all, delete-orphan', lazy='subquery')
    likes: Mapped[list['Like']] = relationship(back_populates='from_user', cascade='all, delete-orphan',
                                               lazy='subquery')


class Image(Base):
    __tablename__ = 'images'
    url: Mapped[str]
    prompt: Mapped[str]
    tags: Mapped[list[str]]
    is_public: Mapped[bool] = mapped_column(default=False)
    author_id: Mapped[uuid.UUID] = mapped_column(ForeignKey('users.id'))
    author: Mapped['User'] = relationship(back_populates='images', lazy='subquery')
    likes: Mapped[list['Like']] = relationship(back_populates='to_image', cascade='all, delete-orphan', lazy='subquery')


class Like(Base):
    __tablename__ = 'likes'
    from_user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey('users.id'))
    to_image_id: Mapped[uuid.UUID] = mapped_column(ForeignKey('images.id'))
    from_user: Mapped['User'] = relationship(back_populates='likes', lazy='subquery')
    to_image: Mapped['Image'] = relationship(back_populates='likes', lazy='subquery')
    __table_args__ = (
        UniqueConstraint('from_user_id', 'to_image_id', name='uq_like'),
    )


async def create_tables() -> None:
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


def connection(method: Callable) -> Callable:
    async def wrapper(*args, **kwargs) -> Any:
        async with async_session() as session:
            try:
                result = await method(*args, session=session, **kwargs)
                await session.commit()
                return result
            except Exception as e:
                await session.rollback()
                raise e

    return wrapper
