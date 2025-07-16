import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.db.database import create_db_and_tables

from app.models.users import user_routers
from app.controllers.users_controller import users_router
from app.controllers.courses_controller import courses_router
from app.controllers.payments_controller import payments_router
from app.schemas.user_schemas import UserCreate, UserRead, UserUpdate
from app.controllers.messages_controller import messages_router
from app.controllers.works_controller import works_router

@asynccontextmanager
async def lifespan(app: FastAPI): # noqa
    """Lifespan event handler to create database tables."""
    await create_db_and_tables()
    yield  # This will run when the app starts and stops


# FastAPI Configuration
# ------------------------------------------------------------------------------
app = FastAPI(
    title="Course Platform API",
    description="API for managing business_objects, students, and instructors",
    version="0.1.0",
    lifespan=lifespan,
)
"""FastAPI: application instance for the Course Platform API."""

# Middleware Configuration
# ------------------------------------------------------------------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins, adjust as needed
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods, adjust as needed
    allow_headers=["*"],  # Allows all headers, adjust as needed
)

# Logging Configuration
# ------------------------------------------------------------------------------
file_handler = logging.FileHandler("app.log")
console_handler = logging.StreamHandler()

logging.basicConfig(
    level=logging.INFO,
    format="%(levelname)s: - %(message)s",
    handlers=[
        file_handler,
        console_handler
    ],
)


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

app.include_router(router=users_router)
app.include_router(router=courses_router)
app.include_router(router=payments_router)
app.include_router(router=messages_router)
app.include_router(router=works_router)