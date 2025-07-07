from typing import List
from fastapi import Depends
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.courses import Course, Lesson
from app.schemas.course_schemas import (
    CourseCreate,
    CourseRead,
    CourseUpdate,
    LessonCreate,
    LessonRead,
)
from app.db.database import get_async_session


class CourseDAO:
    """Data Access Object for Course operations."""
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_course(
            self,
            course_data: CourseCreate[LessonCreate],
            instructor_id: int
    ) -> CourseRead[LessonRead]:
        """Create a new course with the provided data."""
        stmt = select(Course).where(Course.title == course_data.title)
        result = await self.session.execute(stmt)
        existing_course = result.scalars().first()
        if existing_course:
            raise ValueError("Course with this title already exists")

        course_dict = course_data.model_dump(exclude={"lessons"})
        lessons = [Lesson(**item.model_dump()) for item in course_data.lessons]

        course = Course(**course_dict)
        course.instructor_id = instructor_id
        course.lessons = lessons
        self.session.add(course)
        await self.session.commit()
        await self.session.refresh(course)
        return CourseRead[LessonRead].model_validate(course)

    async def get_course_by_id(self, course_id: int) -> CourseRead[LessonRead] | None:
        """Get a course by its ID."""
        stmt = select(Course).where(Course.id == course_id).options(selectinload(Course.lessons))
        result = await self.session.execute(stmt)
        course = result.scalars().first()
        if not course:
            return None
        return CourseRead[LessonRead].model_validate(course)

    async def get_all_courses(self, offset: int = 0, limit: int = 100) -> List[CourseRead[LessonRead]]:
        """Get a paginated list of all business_objects."""
        stmt = (
            select(Course)
            .options(selectinload(Course.lessons))
            .offset(offset)
            .limit(limit)
        )
        result = await self.session.execute(stmt)
        courses = result.scalars().all()
        return [CourseRead[LessonRead].model_validate(course) for course in courses]

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

    async def update_course(
            self,
            course_id: int,
            course_data: CourseUpdate
    ) -> CourseRead:
        """Update a course with the provided data."""
        course = await self.session.get(Course, course_id)
        if not course:
            raise ValueError("Course not found")

        for key, value in course_data.model_dump(exclude_unset=True).items():
            setattr(course, key, value)

        await self.session.commit()
        await self.session.refresh(course)
        return CourseRead[LessonRead].model_validate(course)

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
        self.session.add(lesson)
        await self.session.commit()
        await self.session.refresh(lesson)
        return LessonRead.model_validate(lesson)

    async def get_lesson_by_id(self, lesson_id: int) -> LessonRead | None:
        """Get a lesson by its ID."""
        stmt = select(Lesson).where(Lesson.id == lesson_id)
        result = await self.session.execute(stmt)
        lesson = result.scalars().first()
        if not lesson:
            return None
        return LessonRead.model_validate(lesson)

    async def delete_lesson(self, lesson_id: int) -> None:
        """Delete a lesson by its ID."""
        lesson = await self.session.get(Lesson, lesson_id)
        if not lesson:
            raise ValueError("Lesson not found")
        await self.session.delete(lesson)
        await self.session.commit()


async def get_course_dao(session: AsyncSession = Depends(get_async_session)):
    """Dependency to get the CourseDAO."""
    yield CourseDAO(session)


async def get_lesson_dao(session: AsyncSession = Depends(get_async_session)):
    """Dependency to get the LessonDAO."""
    yield LessonDAO(session)