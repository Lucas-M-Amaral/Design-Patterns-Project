from enum import Enum
from typing import Any

from fastapi import Depends
from fastapi_users import BaseUserManager, FastAPIUsers, models
from fastapi_users.db import SQLAlchemyBaseUserTable

from sqlalchemy import String, Enum as SQLEnum
from sqlalchemy.orm import mapped_column, Mapped
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

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    first_name: Mapped[str] = mapped_column(String(length=100), nullable=False)
    last_name: Mapped[str] = mapped_column(String(length=100), nullable=False)
    user_type: Mapped[UserTypeEnum] = mapped_column(
        SQLEnum(UserTypeEnum, values_callable=lambda x: [e.value for e in x]),
        default=UserTypeEnum.STUDENT,
        nullable=False
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

    def __str__(self):
        return f"{self.email} ({self.user_type.name}) - {self.full_name}"


async def get_user_db(session: AsyncSession = Depends(get_async_session)):
    """Dependency to get the user database."""
    yield UserDatabase(session, User)


class UserManager(BaseUserManager[User, int]):
    """
    Custom user manager for the application. A manager is a Data Access Object (DAO)
    that provides methods to interact with the user database.
    """

    def __init__(self, user_db: UserDatabase = Depends(get_user_db)):
        super().__init__(user_db=user_db)

    def parse_id(self, value: str) -> int:
        """Parse a string ID into the correct type (int in this case)."""
        try:
            return int(value)
        except ValueError as e:
            raise ValueError("Invalid ID format") from e

    async def get_all(self, offset: int = 0, limit: int = 100, user_type: str | None = None) -> list[User]:
        """Get all users with optional filters."""
        return await self.user_db.get_all(offset=offset, limit=limit, user_type=user_type) # noqa


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
dict: Dictionary containing user-related routes for registration, 
      authentication, and user data management.
"""