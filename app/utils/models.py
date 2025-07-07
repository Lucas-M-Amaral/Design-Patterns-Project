import datetime
from sqlalchemy import DateTime
from sqlalchemy.orm import DeclarativeBase, mapped_column, Mapped


class Base(DeclarativeBase):
    """Base class for all models in the application."""

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    created_at = mapped_column(DateTime, default=datetime.datetime.now)
    updated_at = mapped_column(
        DateTime,
        default=datetime.datetime.now,
        onupdate=datetime.datetime.now
    )
