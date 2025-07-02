from contextlib import asynccontextmanager
from fastapi import FastAPI

from app.db.database import create_db_tables


@asynccontextmanager
async def lifespan(app: FastAPI): # noqa
    """Lifespan event handler to create database tables."""
    await create_db_tables()
    yield  # This will run when the app starts and stops

app = FastAPI(
    title="Course Platform API",
    description="API for managing courses, students, and instructors",
    version="0.1.0",
    lifespan=lifespan,
)
"""FastAPI: application instance for the Course Platform API."""


# App routers
@app.get("/")
async def root():
    return {"message": "Course Platform API"}
