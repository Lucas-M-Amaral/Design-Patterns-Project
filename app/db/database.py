import os
import datetime
import dotenv
from collections.abc import AsyncGenerator

from fastapi import Depends
from fastapi_users.db import SQLAlchemyUserDatabase

from sqlalchemy import Column, DateTime, Column
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.ext.asyncio import (
    create_async_engine,
    AsyncSession,
    async_sessionmaker,
)

from app.models.users import User

# Load environment variables from .env file
dotenv.load_dotenv()

# Database Configs
# ------------------------------------------------------------------------------
DATABASE_URL = os.getenv("DATABASE_URL")
"""str: Database URL for the application, loaded from environment variables."""

engine = create_async_engine(DATABASE_URL)
"""sqlalchemy.ext.asyncio.AsyncEngine: SQLAlchemy async engine instance."""

async_session_maker = async_sessionmaker(engine, expire_on_commit=False)
"""sqlalchemy.ext.asyncio.async_sessionmaker: Async session maker for database operations."""

# Database Operations
# ------------------------------------------------------------------------------

async def create_db_and_tables():
    """Create the database and tables if they do not exist."""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def get_async_session() -> AsyncGenerator[AsyncSession, None]:
    """Get an async session for database operations."""
    async with async_session_maker() as session:
        yield session


async def get_user_db(session: AsyncSession = Depends(get_async_session)):
    """Get the user database instance."""
    yield SQLAlchemyUserDatabase(session, User)


# Base Model - implements common fields for all models
# ------------------------------------------------------------------------------
class Base(DeclarativeBase):
    """Base class for all models in the application."""
    created_at = Column(DateTime, default=datetime.datetime.now)
    updated_at = Column(DateTime, default=datetime.datetime.now, onupdate=datetime.datetime.now)
