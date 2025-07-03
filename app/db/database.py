import os
import dotenv
from collections.abc import AsyncGenerator
from fastapi_users.db import SQLAlchemyUserDatabase

from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import (
    create_async_engine,
    AsyncSession,
    async_sessionmaker,
)

from app.utils.models import Base

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


# Database Classes and Functions
# ------------------------------------------------------------------------------
class UserDatabase(SQLAlchemyUserDatabase):
    """Custom user database for the application."""

    async def get_all(self, offset: int = 0, limit: int = 100, user_type: str | None = None):
        """Get all users with pagination."""
        stmt = select(self.user_table).offset(offset).limit(limit)
        if user_type:
            stmt = stmt.where(self.user_table.user_type == user_type) # type: ignore
        result = await self.session.execute(stmt)
        return result.scalars().all()


async def create_db_and_tables():
    """Create the database and tables if they do not exist."""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def get_async_session() -> AsyncGenerator[AsyncSession, None]:
    """Get an async session for database operations."""
    async with async_session_maker() as session:
        yield session
