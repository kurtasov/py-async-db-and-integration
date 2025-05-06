from app.main import read_tasks_for_day
from fastapi import Response
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
import pytest
from unittest.mock import patch


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
    mock_url = "https://isdayoff.ru/2025-05-06"
    mock_response_data = "1"

    async def mock_get(*args, **kwargs):
        class MockResponse:
            def __init__(self, text_data, status_code):
                self.text = text_data
                self.status_code = status_code

            def raise_for_status(self):
                if self.status_code >= 400:
                    raise Exception("Request failed")

        return MockResponse(mock_response_data, status_code=200)

    with patch("httpx.AsyncClient.get", new=mock_get):
        coro = read_tasks_for_day(response=Response(), session=get_async_session)
        res = await coro
        assert res[0].get("is_day_off", None) == True
