from typing import List, Optional
from enum import Enum
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import (
    String,
    ForeignKey,
    Boolean,
    Numeric,
    Text,
    JSON,
    Enum as SQLEnum,
)

from app.utils.models import Base
from app.patterns.composite import LessonComponent, LessonLeaf, CourseComposite


class LessonTypeEnum(str, Enum):
    MODULE = "M"
    QUIZ = "Q"
    VIDEO = "V"
    TEXT = "T"

    @classmethod
    def get_choices(cls):
        return [(choice.value, choice.name) for choice in cls]


class Course(Base):
    """Represents a course in the system, which can contain multiple lessons."""
    __tablename__ = "courses"

    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    price: Mapped[float] = mapped_column(Numeric(10, 2), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    instructor_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )

    instructor = relationship("User", back_populates="courses_teaching")
    lessons: Mapped[List["Lesson"]] = relationship(
        "Lesson",
        back_populates="course",
        cascade="all, delete-orphan",
        order_by="Lesson.order",
        lazy="selectin"
    )

    def render(self):
        """Render the course and its lessons using the Composite Pattern."""
        composite = CourseComposite(self.title)
        for lesson in self.lessons:
            composite.lessons.append(lesson.to_composite())
        return composite.render()


class Lesson(Base):
    """Represents a lesson in a course, which can be a module, quiz, video, or text."""
    __tablename__ = "lessons"

    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    lesson_type: Mapped[LessonTypeEnum] = mapped_column(
        SQLEnum(LessonTypeEnum, values_callable=lambda x: [e.value for e in x]),
        nullable=False,
        default=LessonTypeEnum.VIDEO
    )
    order: Mapped[int] = mapped_column(nullable=False)
    file_path: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    quiz_data: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)

    parent_id: Mapped[Optional[int]] = mapped_column(ForeignKey("lessons.id"))
    prerequisite_id: Mapped[Optional[int]] = mapped_column(ForeignKey("lessons.id"))
    course_id: Mapped[int] = mapped_column(ForeignKey("courses.id", ondelete="CASCADE"))

    # Composite Pattern: self-referential relationship for hierarchical structure
    parent: Mapped[Optional["Lesson"]] = relationship(
        "Lesson",
        back_populates="children",
        foreign_keys=[parent_id],
        remote_side="[Lesson.id]",
        lazy="selectin"
    )
    children: Mapped[List["Lesson"]] = relationship(
        "Lesson",
        back_populates="parent",
        foreign_keys=[parent_id],
        order_by="Lesson.order",
        lazy="selectin"
    )

    # Chain of Responsibility: prerequisite relationship
    prerequisite: Mapped[Optional["Lesson"]] = relationship(
        "Lesson",
        foreign_keys=[prerequisite_id],
        remote_side="[Lesson.id]",
        lazy="selectin"
    )
    course: Mapped["Course"] = relationship(
        "Course",
        back_populates="lessons",
        lazy="selectin"
    )

    def to_composite(self) -> LessonComponent:
        """Convert the lesson to a composite component."""
        if self.children:
            composite = CourseComposite(self.title)
            for child in self.children:
                composite.lessons.append(child.to_composite())
            return composite
        else:
            return LessonLeaf(
                title=self.title,
                content_type=self.lesson_type.value,
                content_path=self.file_path
            )
