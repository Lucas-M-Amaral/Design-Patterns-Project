from enum import Enum

from fastapi import Depends
from fastapi_users import BaseUserManager, FastAPIUsers
from fastapi_users.db import SQLAlchemyBaseUserTable

from sqlalchemy import String, Enum as SQLEnum
from sqlalchemy.orm import mapped_column, Mapped, relationship
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.database import get_async_session, UserDatabase
from app.utils.token import auth_backend
from app.utils.models import Base


class UserTypeEnum(str, Enum):
    """Enumeration for user types."""
    INSTRUCTOR = "I"
    STUDENT = "S"

    @classmethod
    def get_choices(cls):
        return [(choice.value, choice.name) for choice in cls]


class User(SQLAlchemyBaseUserTable[int], Base):
    """Default custom user model for the application."""
    __tablename__ = "users"

    first_name: Mapped[str] = mapped_column(String(length=100), nullable=False)
    last_name: Mapped[str] = mapped_column(String(length=100), nullable=False)
    user_type: Mapped[UserTypeEnum] = mapped_column(
        SQLEnum(UserTypeEnum, values_callable=lambda x: [e.value for e in x]),
        default=UserTypeEnum.STUDENT,
        nullable=False
    )

    # Relationships
    courses_teaching = relationship(
        "Course",
        back_populates="instructor",
        cascade="all, delete-orphan",
        lazy="selectin",
    )
    payments = relationship(
        "Payment",
        back_populates="user",
        cascade="all, delete-orphan",
        lazy="selectin",
    )
    lesson_progressions = relationship(
        "LessonProgression",
        back_populates="user",
        cascade="all, delete-orphan",
        lazy="selectin",
    )

    messages_sent = relationship(
        "Message",
        back_populates="sender",
        cascade="all, delete-orphan",
        lazy="selectin",
    )


    @property
    def full_name(self) -> str:
        """Return the full name of the user."""
        return f"{self.first_name} {self.last_name}"

    @property
    def is_instructor(self) -> bool:
        """Check if the user is an instructor."""
        return self.user_type == UserTypeEnum.INSTRUCTOR

    @property
    def is_student(self) -> bool:
        """Check if the user is a student."""
        return self.user_type == UserTypeEnum.STUDENT


async def get_user_db(session: AsyncSession = Depends(get_async_session)):
    """Dependency to get the user database."""
    yield UserDatabase(session, User)


class UserManager(BaseUserManager[User, int]):
    """
    Custom user manager for the application."""

    def __init__(self, user_db: UserDatabase = Depends(get_user_db)):
        super().__init__(user_db=user_db)

    def parse_id(self, value: str) -> int:
        """Parse a string ID into the correct type (int in this case)."""
        try:
            return int(value)
        except ValueError as e:
            raise ValueError("Invalid ID format") from e

    async def get_all(self, offset: int = 0, limit: int = 100, user_type: str | None = None):
        """Get all users with optional filters."""
        return await self.user_db.get_all(offset=offset, limit=limit, user_type=user_type) # noqa

    async def get_my_courses(self, user_id: int, offset: int = 0, limit: int = 100):
        """Get all courses for a user with pagination."""
        return await self.user_db.get_my_courses(user_id=user_id, offset=offset, limit=limit) # noqa

    async def get_my_lesson_progressions(
            self, user_id: int, course_id: int | None = None, offset: int = 0, limit: int = 100
    ):
        """Get all lesson progressions for a user with optional course filtering."""
        return await self.user_db.get_lesson_progressions(  # noqa
            user_id=user_id, course_id=course_id, offset=offset, limit=limit
        )

    async def mark_lesson_completed(self, user_id: int, lesson_id: int):
        """Mark a lesson as completed for the user."""
        lesson_progression = await self.user_db.get_lesson_progress(user_id=user_id, lesson_id=lesson_id) # noqa
        lesson_progression.completed = True
        await self.user_db.mark_lesson_completed(lesson_progression=lesson_progression) # noqa

async def get_user_manager(user_db: UserDatabase = Depends(get_user_db)):
    """Dependency to get the user manager."""
    yield UserManager(user_db)


# FastAPIUsers Configs and Routers
# ------------------------------------------------------------------------------
fastapi_users = FastAPIUsers[User, int](
    get_user_manager,
    [auth_backend],
)
"""FastAPIUsers: Instance for managing user authentication and authorization."""

user_routers = {
    "auth": fastapi_users.get_auth_router(auth_backend),
    "register": fastapi_users.get_register_router,
    "my-data": fastapi_users.get_users_router,
}
"""
dict: Dictionary containing user-related routes for registration, authentication, and user data management.
"""