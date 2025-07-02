import uuid

from fastapi_users import schemas


class UserCreateSchema(schemas.BaseUserCreate[uuid.UUID]):
    """
    Schema for creating a new user. This schema includes
    fields for first name, last name, and user type.

    Attributes:
        first_name (str): The first name of the user.
        last_name (str): The last name of the user.
        user_type (str): The type of user, default is "S" for Student.
    """
    first_name: str
    last_name: str
    user_type: str = "S" # Default to Student


class UserUpdateSchema(schemas.BaseUserUpdate[uuid.UUID]):
    """
    Schema for updating an existing user. This schema includes
    fields for first name and last name.

    Attributes:
        first_name (str): The first name of the user.
        last_name (str): The last name of the user.
    """
    first_name: str
    last_name: str


class UserReadSchema(schemas.BaseUser[uuid.UUID]):
    """
    Schema for reading user information. This schema includes
    fields for user ID, email, first name, last name, and user type.

    Attributes:
        id (uuid.UUID): The unique identifier of the user.
        email (str): The email address of the user.
        first_name (str): The first name of the user.
        last_name (str): The last name of the user.
        user_type (str): The type of user, e.g., "I" for Instructor or "S" for Student.
    """
    id: uuid.UUID
    email: str
    first_name: str
    last_name: str
    user_type: str
