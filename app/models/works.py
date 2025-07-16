from datetime import datetime
from typing import List
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import ForeignKey, String, JSON, DateTime

from app.utils.models import Base


class Work(Base):
    """Represents an assignment (work) posted by an instructor in a course."""
    __tablename__ = "works"

    title: Mapped[str] = mapped_column(String(255), nullable=False)
    questions: Mapped[list] = mapped_column(JSON, nullable=False)  # Stored as JSON directly
    course_id: Mapped[int] = mapped_column(ForeignKey("courses.id", ondelete="CASCADE"), nullable=False)

    course = relationship("Course", back_populates="works", lazy="selectin")
    answers = relationship(
        "WorkAnswer",
        back_populates="work",
        cascade="all, delete-orphan",
        lazy="selectin"
    )


class WorkAnswer(Base):
    """Represents a student's submission to a work."""
    __tablename__ = "work_answers"

    answers: Mapped[list] = mapped_column(JSON, nullable=False)
    student_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    work_id: Mapped[int] = mapped_column(ForeignKey("works.id", ondelete="CASCADE"), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    work = relationship("Work", back_populates="answers", lazy="selectin")
