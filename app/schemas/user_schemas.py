from typing import List
from fastapi_users import schemas
from pydantic import Field, ConfigDict

from app.models.users import UserTypeEnum
from app.schemas.course_schemas import CoursesTeaching


class UserCreate(schemas.BaseUserCreate):
    """
    Schema for creating a new user. This schema includes
    fields for first name, last name, and user type.
    """
    password: str = Field(..., min_length=8, max_length=64, description="Password of the user")
    first_name: str = Field(..., max_length=50, description="First name of the user")
    last_name: str = Field(..., max_length=50, description="Last name of the user")
    user_type: UserTypeEnum = Field(
        UserTypeEnum.STUDENT,
        examples=[UserTypeEnum.STUDENT, UserTypeEnum.INSTRUCTOR],
        description="The type of user: S for Student, I for Instructor"
    )
    is_verified: bool = Field(False, description="Whether the user's email has been verified")
    is_active: bool = Field(True, description="Whether the user account is active")
    is_superuser: bool = Field(False, description="Whether the user has superuser privileges")


class UserUpdate(schemas.BaseUserUpdate):
    """
    Schema for updating an existing user. This schema includes
    fields for first name and last name.
    """
    first_name: str | None = Field(..., max_length=50, description="First name of the user")
    last_name: str | None = Field(..., max_length=50, description="Last name of the user")


class UserRead(schemas.BaseUser[int]):
    """
    Schema for reading user information. This schema includes
    fields for user ID, email, first name, last name, user type,
    and a list of courses the instructor is teaching if the user type is INSTRUCTOR.
    """
    id: int = Field(..., description="Unique identifier for the user")
    email: str = Field(..., description="Email address of the user")
    first_name: str = Field(..., description="First name of the user")
    last_name: str = Field(..., description="Last name of the user")
    user_type: str = Field(
        ...,
        description="The type of user: S or I.",
        examples=[UserTypeEnum.STUDENT, UserTypeEnum.INSTRUCTOR],
    )
    courses_teaching: List[CoursesTeaching] = Field(
        default_factory=list,
        description="List of courses the instructor is teaching, if applicable."
    )

    model_config = ConfigDict(from_attributes=True)
