import uuid
from typing import Optional

from fastapi import Depends, Request
from fastapi_users import FastAPIUsers, BaseUserManager, UUIDIDMixin
from fastapi_users.db import SQLAlchemyUserDatabase

from app.db.database import get_user_db
from app.models.users import User
from app.schemas.user_schemas import UserCreateSchema, UserUpdateSchema


class UserManager(UUIDIDMixin, BaseUserManager[User, uuid.UUID]):
    """User manager for handling user-related operations."""

    async def create(
            self, user_create: UserCreateSchema, safe: bool = False, request: Optional[Request] = None
    ) -> User:
        """Creates a new user with the provided user_create schema."""
        pass

    async def update(
            self, user_update: UserUpdateSchema, user: User, safe: bool = False, request: Optional[Request] = None
    ) -> User:
        """Updates an existing user with the provided user_update schema."""
        pass

    async def get_by_email(self, email: str, request: Optional[Request] = None) -> Optional[User]:
        """Retrieves a user by their email address."""
        return await self.get_by_email(email, request=request)

    async def get_by_id(self, id: uuid.UUID, request: Optional[Request] = None) -> Optional[User]:
        """Retrieves a user by their unique identifier."""
        return await self.get_by_id(id, request=request)


async def get_user_manager(user_db: SQLAlchemyUserDatabase = Depends(get_user_db)):
    yield UserManager(user_db)


fastapi_users = FastAPIUsers[User, uuid.UUID](
    get_user_manager,
    [],
)