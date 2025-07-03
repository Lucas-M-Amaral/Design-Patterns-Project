from fastapi_users import schemas

from app.models.users import UserTypeEnum


class UserCreate(schemas.BaseUserCreate):
    """
    Schema for creating a new user. This schema includes
    fields for first name, last name, and user type.
    """
    password: str
    first_name: str
    last_name: str
    user_type: UserTypeEnum = UserTypeEnum.STUDENT
    is_verified: bool = False
    is_active: bool = True
    is_superuser: bool = False


class UserUpdate(schemas.BaseUserUpdate):
    """
    Schema for updating an existing user. This schema includes
    fields for first name and last name.
    """
    first_name: str | None = None
    last_name: str | None = None


class UserRead(schemas.BaseUser[int]):
    """
    Schema for reading user information. This schema includes
    fields for user ID, email, first name, last name, and user type.
    """
    id: int
    email: str
    first_name: str
    last_name: str
    user_type: str
