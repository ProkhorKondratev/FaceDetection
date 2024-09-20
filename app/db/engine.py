from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy import exc
from sqlalchemy.orm import DeclarativeBase

from app.settings import settings


engine = create_async_engine(settings.DB_URL)
new_session = async_sessionmaker(engine, expire_on_commit=False)


async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    async with new_session() as session:
        try:
            yield session
            await session.commit()
        except exc.SQLAlchemyError:
            await session.rollback()
            raise


class Base(DeclarativeBase):
    pass


async def create_tables():
    print("Создание таблиц")

    print(settings.DB_URL)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def drop_tables():
    print("Удаление таблиц")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
