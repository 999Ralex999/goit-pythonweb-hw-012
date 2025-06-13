# app/db/session.py

import contextlib
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.exc import SQLAlchemyError

from app.core.config import settings


engine = create_async_engine(
    settings.DB_URL,
    echo=False,     
    future=True,    
)

SessionLocal = async_sessionmaker(
    bind=engine,
    expire_on_commit=False,
    autoflush=False,
    class_=AsyncSession,
)


@contextlib.asynccontextmanager
async def get_db() -> AsyncSession:

    async with SessionLocal() as session:
        try:
            yield session
            await session.commit()
        except SQLAlchemyError:
            await session.rollback()
            raise


