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
from sqlalchemy.orm import selectinload

from app.utils.models import Base
from app.models.payments import Payment
from app.models.courses import Course, LessonProgression

# Load environment variables from .env file
dotenv.load_dotenv()

# Database Configs
# ------------------------------------------------------------------------------
DATABASE_URL = os.getenv("DATABASE_URL")
"""str: Database URL for the application, loaded from environment variables."""

engine = create_async_engine(DATABASE_URL)
"""AsyncEngine: SQLAlchemy async engine instance."""

async_session_maker = async_sessionmaker(engine, expire_on_commit=False)
"""async_sessionmaker: Async session maker for database operations."""


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

    async def get_my_courses(self, user_id: int, offset: int = 0, limit: int = 100):
        """Get all courses for a user with pagination."""
        stmt = select(Payment).where(Payment.user_id == user_id).offset(offset).limit(limit)
        stmt = stmt.options(
            selectinload(Payment.course)
        )
        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def get_lesson_progressions(
            self, user_id: int, course_id: int | None = None, offset: int = 0, limit: int = 100
    ):
        """Get all lesson progressions for a user with optional course filtering."""
        stmt = select(LessonProgression).where(LessonProgression.user_id == user_id)
        if course_id is not None:
            stmt = stmt.where(Course.id == course_id)
        stmt = stmt.offset(offset).limit(limit).options(
            selectinload(LessonProgression.lesson)
        )
        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def get_lesson_progress(self, user_id: int, lesson_id: int) -> LessonProgression | None:
        """Get the lesson progression for a user."""
        stmt = select(LessonProgression).where(
            LessonProgression.user_id == user_id,
            LessonProgression.lesson_id == lesson_id
        )
        result = await self.session.execute(stmt)
        return result.scalars().first()

    async def mark_lesson_completed(self, lesson_progression: LessonProgression):
        """Mark a lesson as completed for the user."""
        lesson_progression.completed = True
        self.session.add(lesson_progression)
        await self.session.commit()
        await self.session.refresh(lesson_progression)


async def create_db_and_tables():
    """Create the database and tables if they do not exist."""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def get_async_session() -> AsyncGenerator[AsyncSession, None]:
    """Get an async session for database operations."""
    async with async_session_maker() as session:
        yield session
