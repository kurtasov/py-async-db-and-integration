from app.main import read_tasks_for_day
from fastapi import Response
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
import pytest


ASYNC_DB_URL = (f"postgresql+asyncpg://"
                f"fastapi_taskman:fastapi_taskman"
                f"@127.0.0.1:5432/fastapi_taskman")
async_engine = create_async_engine(ASYNC_DB_URL, echo=True)

async_session = async_sessionmaker(
    async_engine, class_=AsyncSession, expire_on_commit=False
)

@pytest.fixture()
async def get_async_session() -> AsyncSession:
    async with async_session() as session:
        yield session




@pytest.mark.asyncio
async def test_main(get_async_session):
    o = read_tasks_for_day(response=Response(), session=get_async_session)
    assert await o is not None
