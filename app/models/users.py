from typing import Required
from fastapi_users.db import BeanieBaseUser, BeanieUserDatabase
from beanie import Document


class User(BeanieBaseUser, Document):
    """User model for FastAPI Users with Beanie ORM."""
    pass


    class Settings:
        """Settings for the User model."""
        collection = "users"
