import uuid
import enum

from fastapi import Depends
from fastapi_users import BaseUserManager, UUIDIDMixin
from fastapi_users.db import SQLAlchemyBaseUserTableUUID, SQLAlchemyUserDatabase
from fastapi_users.password import PasswordHelper

from sqlalchemy import Column, String, Enum
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.database import get_async_session
from app.utils.models import Base


class UserTypeEnum(enum.Enum):
    """Enumeration for user types."""
    INSTRUCTOR = "I"
    STUDENT = "S"

    @classmethod
    def get_choices(cls):
        return [(choice.value, choice.name) for choice in cls]


class User(SQLAlchemyBaseUserTableUUID, Base):
    """Default custom user model for the application."""
    __tablename__ = "users"

    first_name = Column(String(length=100), nullable=False)
    last_name = Column(String(length=100), nullable=False)
    user_type = Column(
        Enum(UserTypeEnum, native_enum=False, values_callable= lambda x: [e.value for e in x]),
        default=UserTypeEnum.INSTRUCTOR.value,
        nullable=False,
    )

    def __str__(self):
        return f"{self.email} ({self.user_type.name}) - {self.full_name}"

    @property
    def full_name(self) -> str:
        """Return the full name of the user."""
        return f"{self.first_name} {self.last_name}"


class UserManager(UUIDIDMixin, BaseUserManager[User, uuid.UUID], PasswordHelper):
    """Custom user manager for handling user operations."""
    pass


async def get_user_db(session: AsyncSession = Depends(get_async_session)):
    """Dependency to get the user database."""
    yield SQLAlchemyUserDatabase(session, User)


async def get_user_manager(user_db: SQLAlchemyUserDatabase = Depends(get_user_db)):
    """Dependency to get the user manager."""
    yield UserManager(user_db)
