import uuid
import enum
from typing import Optional

from fastapi import Depends, Request
from fastapi_users import FastAPIUsers, BaseUserManager, UUIDIDMixin
from fastapi_users.db import SQLAlchemyBaseUserTableUUID
from sqlalchemy import Column, String, Enum

from app.db.database import get_user_db, Base
from app.schemas.user_schemas import UserCreateSchema, UserUpdateSchema


class UserTypeEnum(enum.Enum):
    """Enumeration for user types."""
    INSTRUCTOR = "I"
    STUDENT = "S"

    @classmethod
    def get_choices(cls):
        return [(choice.value, choice.name) for choice in cls]


class User(SQLAlchemyBaseUserTableUUID, Base):
    """Default custom user model for the application."""
    __table__ = "users"

    first_name = Column(String(length=100), nullable=False)
    last_name = Column(String(length=100), nullable=False)
    user_type = Column(
        Enum(UserTypeEnum, native_enum=False),
        default=UserTypeEnum.INSTRUCTOR.value,
        nullable=False,
    )

    def __str__(self):
        return f"{self.email} ({self.user_type.name}) - {self.full_name}"

    @property
    def full_name(self) -> str:
        """Return the full name of the user."""
        return f"{self.first_name} {self.last_name}"
