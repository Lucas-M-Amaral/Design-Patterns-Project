from contextlib import asynccontextmanager
from fastapi import FastAPI

from app.db.database import create_db_and_tables

from app.models.users import user_routers
from app.controllers.users_controller import router
from app.schemas.user_schemas import UserCreate, UserRead, UserUpdate

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


# App routers
# ------------------------------------------------------------------------------
@app.get("/", name="root", tags=["root"])
async def root():
    return {"welcome": "Course Platform API"}

app.include_router(
    router=user_routers["auth"],
    prefix="/auth/jwt",
    tags=["auth"],
)

app.include_router(
    router=user_routers["register"](
        UserRead,
        UserCreate,
    ),
    prefix="/auth",
    tags=["auth"],
)

app.include_router(
    router=user_routers["my-data"](
        UserRead,
        UserUpdate,
    ),
    prefix="/my-data",
    tags=["my-data"],
)

app.include_router(
    router=router,
)