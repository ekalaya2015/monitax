from sqlalchemy.ext.asyncio import create_async_engine

from sqlalchemy.orm import sessionmaker
from sqlmodel.ext.asyncio.session import AsyncSession

from app.core import config as app_config

DB_POOL_SIZE = 83
WEB_CONCURRENCY = 10
POOL_SIZE = max(DB_POOL_SIZE // WEB_CONCURRENCY, 8)
SIZE_POOL_AIOHTTP = 100

engine = create_async_engine(
    app_config.settings.DEFAULT_SQLALCHEMY_DATABASE_URI,
    echo=True,
    future=True,
    pool_size=POOL_SIZE,
    max_overflow=64,
)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
)
