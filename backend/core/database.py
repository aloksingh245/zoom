from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from .base import Base

DATABASE_URL = "sqlite+aiosqlite:///./sql_app.db"

engine = create_async_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False}, # Needed for SQLite
)

async_session_factory = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    
    expire_on_commit=False,
)

async def get_db():
    async with async_session_factory() as session:
        yield session
