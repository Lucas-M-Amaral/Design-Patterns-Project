from typing import List, Dict, Any
from fastapi import Depends
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.courses import Course, Lesson
from app.patterns.prototype import LessonPrototype
from app.db.database import get_async_session


class CourseDAO:
    """Data Access Object for Course operations."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_course(self, course_data: Dict[str, Any]) -> Course:
        """Create a new course with the provided data."""
        course = Course(**course_data)
        self.session.add(course)
        await self.session.commit()
        await self.session.refresh(course)
        return course

    async def get_course_by_id(self, course_id: int) -> Course | None:
        """Get a course by its ID, including nested lesson relationships."""
        stmt = (select(Course).where(Course.id == course_id).options(
            selectinload(Course.lessons).options(
                selectinload(Lesson.children),
                selectinload(Lesson.prerequisite),
                selectinload(Lesson.parent),
            )
        )
        )
        result = await self.session.execute(stmt)
        course = result.scalars().first()
        if not course:
            return None

        # Ensure all relationships are loaded
        for lesson in course.lessons:
            _ = lesson.children
            _ = lesson.prerequisite
            _ = lesson.parent
        return course

    async def get_all_courses(self, offset: int = 0, limit: int = 100) -> List[Course]:
        """Get a paginated list of all business_objects."""
        stmt = (
            select(Course)
            .options(selectinload(Course.lessons))
            .offset(offset)
            .limit(limit)
        )
        result = await self.session.execute(stmt)
        courses = result.scalars().all()
        return list[Course](courses)

    async def update_course(self, course: Course, course_data: Dict[str, Any]) -> Course:
        """Update a course with the provided data."""
        for key, value in course_data.items():
            if hasattr(course, key) and value is not None:
                setattr(course, key, value)
        await self.session.commit()
        await self.session.refresh(course)
        return course

    async def delete_course(self, course: Course) -> None:
        """Delete a course by its ID."""
        await self.session.delete(course)
        await self.session.commit()


class LessonDAO:
    """Data Access Object for Lesson operations."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_lesson(self, lesson_data: Dict[str, Any]) -> Lesson:
        """Create a new lesson with the provided data."""
        lesson = Lesson(**lesson_data)
        self.session.add(lesson)
        await self.session.commit()
        await self.session.refresh(lesson)
        return lesson

    async def get_lesson_by_id(self, course_id: int, lesson_id: int) -> Lesson | None:
        """Get a lesson by its ID."""
        stmt = (select(Lesson)
                .where(Lesson.course_id == course_id)
                .where(Lesson.id == lesson_id)
                .options(selectinload(Lesson.children))
                )
        result = await self.session.execute(stmt)
        lesson = result.scalars().first()
        if not lesson:
            return None
        return lesson

    async def get_prerequisite_lesson(self, course_id: int, pre_requisite_id: int) -> Lesson | None:
        """Get a prerequisite lesson by its ID."""
        stmt = (
            select(Lesson)
            .where(Lesson.course_id == course_id)
            .where(Lesson.id == pre_requisite_id)
        )
        result = await self.session.execute(stmt)
        pre_requisite = result.scalars().first()
        if not pre_requisite:
            return None
        return pre_requisite

    async def get_parent_lesson(self, course_id: int, parent_id: int) -> Lesson | None:
        """Get a parent lesson by its ID."""
        stmt = (
            select(Lesson)
            .where(Lesson.course_id == course_id)
            .where(Lesson.id == parent_id)
        )
        result = await self.session.execute(stmt)
        parent = result.scalars().first()
        if not parent:
            return None
        return parent

    async def has_dependants(self, lesson_id: int) -> bool:
        """Check if a lesson has any dependants."""
        stmt = (
            select(Lesson)
            .where(Lesson.prerequisite_id == lesson_id)
        )
        result = await self.session.execute(stmt)
        return result.scalars().first() is not None

    async def delete_lesson(self, lesson: Lesson) -> None:
        """Delete a lesson by its ID."""
        await self.session.delete(lesson)
        await self.session.commit()

    async def clone_lesson(
            self,
            course_id: int,
            new_course_id: int,
            lesson_id: int,
            new_prerequisite_id: int | None = None
    ) -> Lesson:
        """Clone a lesson to a new course."""
        stmt = (
            select(Lesson)
            .where(Lesson.id == lesson_id, Lesson.course_id == course_id)
            .options(selectinload(Lesson.children))
        )

        result = await self.session.execute(stmt)
        lesson = result.scalar_one_or_none()

        lesson_clone = LessonPrototype(
            lesson=lesson,
            new_course_id=new_course_id,
            new_prerequisite_id=new_prerequisite_id
        ).clone()

        self.session.add(lesson_clone)
        await self.session.flush()

        for child in lesson_clone.children:
            child.parent_id = lesson_clone.id

        await self.session.commit()
        await self.session.refresh(lesson_clone)
        return lesson_clone


async def get_course_dao(session: AsyncSession = Depends(get_async_session)):
    """Dependency to get the CourseDAO."""
    yield CourseDAO(session)


async def get_lesson_dao(session: AsyncSession = Depends(get_async_session)):
    """Dependency to get the LessonDAO."""
    yield LessonDAO(session)
