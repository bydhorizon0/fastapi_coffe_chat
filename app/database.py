from typing import Annotated, AsyncGenerator

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase

DATABASE_URI = "mysql+aiomysql://root:root123@localhost:3306/myapi?charset=utf8mb4"

async_engine = create_async_engine(
    url=DATABASE_URI, echo=True, pool_size=10, max_overflow=20, pool_recycle=3600
)


class Base(DeclarativeBase):
    pass


AsyncSessionLocal = async_sessionmaker(bind=async_engine, expire_on_commit=False)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()


DbSessionDep = Annotated[AsyncSession, Depends(get_db)]
