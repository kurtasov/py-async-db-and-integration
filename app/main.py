from fastapi import FastAPI, status, Depends, Response
import time
from datetime import date
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlmodel import SQLModel, Field as SQLModelField, select
import asyncio
import httpx


ASYNC_DB_URL = (f"postgresql+asyncpg://"
                f"fastapi_taskman:fastapi_taskman"
                f"@127.0.0.1:5432/fastapi_taskman")
async_engine = create_async_engine(ASYNC_DB_URL, echo=True)

async_session = async_sessionmaker(
    async_engine, class_=AsyncSession, expire_on_commit=False
)


async def get_async_session() -> AsyncSession:
    async with async_session() as session:
        yield session


class Task(SQLModel, table=True):
    task_id: int = SQLModelField(default=None, nullable=False, primary_key=True)
    due_date: date
    assignee: int #= SQLModelField(foreign_key="user.user_id")
    project: int #= SQLModelField(default=None, nullable=True, foreign_key="project.project_id")
    lat: float #= SQLModelField(default=None, nullable=True)
    lon: float #= SQLModelField(default=None, nullable=True)


app = FastAPI()

@app.get("/tasks-for-day", status_code=status.HTTP_200_OK)
async def read_tasks_for_day(response: Response,
                             session: AsyncSession = Depends(get_async_session),
                             due_date: date = date.today()):
    start = time.time()
    async def query_db(due_date_param):
        statement = (select(Task)
                     .where(Task.due_date == due_date_param))
        result = await session.execute(statement)
        return result.scalars().all()


    http_client = httpx.AsyncClient(timeout=httpx.Timeout(10.0, read=None))
    res = await asyncio.gather(
        query_db(due_date),
        http_client.get(f"https://isdayoff.ru/{due_date}"),
        #session.execute(text("SELECT pg_sleep(5)")),
        #http_client.get("https://httpbin.org/delay/10"),
    )

    elapsed_seconds = time.time() - start
    output = [{
        "due_date": due_date,
        "is_day_off": True if res[1].text == "1" else False,
        "tasks": res[0]
    }]

    response.headers["X-Completed-In"] = f"{elapsed_seconds:.3f} seconds"
    return output
