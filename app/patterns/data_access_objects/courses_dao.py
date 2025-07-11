from typing import List, Dict, Any
from fastapi import Depends
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.courses import Course, Lesson
from app.schemas.course_schemas import (
    CourseRead,
    CourseUpdate,
    LessonCreate,
    LessonRead,
    LessonReadPartial,
    CourseReadPartial,
)
from app.patterns.prototype import LessonPrototype
from app.db.database import get_async_session


class CourseDAO:
    """Data Access Object for Course operations."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_course(self, course_data: Dict[str, Any]) -> CourseRead:
        """Create a new course with the provided data."""
        stmt = (select(Course)
                .where(Course.title == course_data["title"])
                .where(Course.instructor_id == course_data["instructor_id"])
                )
        result = await self.session.execute(stmt)
        existing_course = result.scalars().first()
        if existing_course:
            raise ValueError("Course with the same title and instructor already exists")

        course = Course(**course_data)
        self.session.add(course)
        await self.session.commit()
        await self.session.refresh(course)
        return CourseRead.model_validate(course)

    async def get_course_by_id(self, course_id: int) -> CourseRead[LessonReadPartial] | None:
        """Get a course by its ID."""
        stmt = select(Course).where(Course.id == course_id).options(selectinload(Course.lessons))
        result = await self.session.execute(stmt)
        course = result.scalars().first()
        if not course:
            return None
        return CourseRead[LessonReadPartial].model_validate(course)

    async def get_all_courses(self, offset: int = 0, limit: int = 100) -> List[CourseReadPartial]:
        """Get a paginated list of all business_objects."""
        stmt = (
            select(Course)
            .options(selectinload(Course.lessons))
            .offset(offset)
            .limit(limit)
        )
        result = await self.session.execute(stmt)
        courses = result.scalars().all()
        return [CourseReadPartial.model_validate(course) for course in courses]

    async def get_course_model_by_id(self, course_id: int) -> Course:
        from sqlalchemy.orm import selectinload
        stmt = (
            select(Course)
            .where(Course.id == course_id)
            .options(
                selectinload(Course.lessons)
                .selectinload(Lesson.children)
            )
        )
        result = await self.session.execute(stmt)
        course = result.scalars().first()
        if not course:
            raise ValueError("Course not found")
        return course

    async def update_course(self, course_id: int, course_data: CourseUpdate) -> CourseReadPartial:
        """Update a course with the provided data."""
        course = await self.session.get(Course, course_id)
        if not course:
            raise ValueError("Course not found")

        for key, value in course_data.model_dump(exclude_unset=True).items():
            setattr(course, key, value)

        await self.session.commit()
        await self.session.refresh(course)
        return CourseReadPartial.model_validate(course)

    async def delete_course(self, course_id: int) -> None:
        """Delete a course by its ID."""
        course = await self.session.get(Course, course_id)
        if not course:
            raise ValueError("Course not found")
        await self.session.delete(course)
        await self.session.commit()


class LessonDAO:
    """Data Access Object for Lesson operations."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_lesson(self, course_id: int, lesson_data: LessonCreate) -> LessonRead:
        """Create a new lesson with the provided data."""
        lesson = Lesson(**lesson_data.model_dump())

        lesson.course_id = course_id
        pre_requisite_id = lesson_data.prerequisite_id
        parent_id = lesson_data.parent_id

        if pre_requisite_id is not None:
            pre_requisite = await self.session.get(Lesson, lesson_data.prerequisite_id)
            if not pre_requisite:
                raise ValueError("Prerequisite lesson not found")
            if pre_requisite.course_id != course_id:
                raise ValueError("Prerequisite lesson must belong to the same course")

        if parent_id is not None:
            parent = await self.session.get(Lesson, lesson_data.parent_id)
            if not parent:
                raise ValueError("Module lesson not found")
            if not parent.is_module:
                raise ValueError("Parent lesson must be a module")

        if pre_requisite_id is not None and parent_id is not None:
            if pre_requisite_id == parent_id:
                raise ValueError("Prerequisite and parent cannot be the same lesson")

        self.session.add(lesson)
        await self.session.commit()
        await self.session.refresh(lesson)
        return LessonRead.model_validate(lesson)

    async def get_lesson_by_id(self, course_id: int, lesson_id: int) -> LessonRead[LessonReadPartial] | None:
        """Get a lesson by its ID."""
        stmt = (select(Lesson)
                .where(Lesson.course_id == course_id)
                .where(Lesson.id == lesson_id)
                .options(selectinload(Lesson.children))
                )
        result = await self.session.execute(stmt)
        lesson = result.scalars().first()
        if not lesson:
            raise ValueError("Lesson not found for this course")
        return LessonRead.model_validate(lesson)

    async def delete_lesson(self, course_id: id, lesson_id: int) -> None:
        """Delete a lesson by its ID."""
        stmt = (select(Lesson)
                .where(Lesson.course_id == course_id)
                .where(Lesson.id == lesson_id))
        lesson = (await self.session.execute(stmt)).scalars().first()
        if not lesson:
            raise ValueError("Lesson not found for this course")
        await self.session.delete(lesson)
        await self.session.commit()

    async def clone_lesson(
            self,
            course_id: int,
            new_course_id: int,
            lesson_id: int,
            new_prerequisite_id: int | None = None
    ) -> LessonRead:
        """Clone a lesson to a new course."""
        stmt = (
            select(Lesson)
            .where(Lesson.id == lesson_id, Lesson.course_id == course_id)
            .options(selectinload(Lesson.children))
        )

        result = await self.session.execute(stmt)
        lesson: Lesson = result.scalar_one_or_none()

        if not lesson:
            raise ValueError("Lesson not found")

        if not lesson.is_module:
            raise ValueError("Only modules can be cloned")

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
        return LessonRead.model_validate(lesson_clone)


async def get_course_dao(session: AsyncSession = Depends(get_async_session)):
    """Dependency to get the CourseDAO."""
    yield CourseDAO(session)


async def get_lesson_dao(session: AsyncSession = Depends(get_async_session)):
    """Dependency to get the LessonDAO."""
    yield LessonDAO(session)
