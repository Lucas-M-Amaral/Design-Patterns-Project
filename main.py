import uuid
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi_users import FastAPIUsers

from app.db.database import create_db_and_tables
from app.models.users import User, get_user_manager
from app.schemas.user_schemas import UserCreate, UserRead, UserUpdate
from app.utils.token import auth_backend

@asynccontextmanager
async def lifespan(app: FastAPI): # noqa
    """Lifespan event handler to create database tables."""
    await create_db_and_tables()
    yield  # This will run when the app starts and stops


# FastAPI Configs
# ------------------------------------------------------------------------------
app = FastAPI(
    title="Course Platform API",
    description="API for managing courses, students, and instructors",
    version="0.1.0",
    lifespan=lifespan,
)
"""FastAPI: application instance for the Course Platform API."""


fastapi_users = FastAPIUsers[User, uuid.UUID](
    get_user_manager,
    [auth_backend],
)
"""FastAPIUsers: Instance for managing user authentication and authorization."""


# App routers
# ------------------------------------------------------------------------------
@app.get("/", name="root", tags=["root"])
async def root():
    return {"welcome": "Course Platform API"}

app.include_router(
    fastapi_users.get_auth_router(auth_backend),
    prefix="/auth/jwt",
    tags=["auth"],
)

app.include_router(
    fastapi_users.get_register_router(
        UserRead,
        UserCreate,
),
    prefix="/auth",
    tags=["auth"],
)

app.include_router(
    fastapi_users.get_users_router(
        UserRead,
        UserUpdate,
    ),
    prefix="/users",
    tags=["users"],
)
