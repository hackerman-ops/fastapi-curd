
from sqlmodel import SQLModel
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.orm import sessionmaker

DATABASE_URL = "postgresql+asyncpg://my_user:password123@172.30.167.162:5433/sql_model"

engine = create_async_engine(
    DATABASE_URL,
    echo=True,
    future=True,
    max_overflow=50,
    pool_size=100,
    pool_timeout=30,
    pool_recycle=3600,
    pool_pre_ping=True,
)


async def get_session() -> AsyncSession:
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    async with async_session() as session:
        yield session


async def init_db():
    async with engine.begin() as conn:
        # await conn.run_sync(SQLModel.metadata.drop_all)
        await conn.run_sync(SQLModel.metadata.create_all)
