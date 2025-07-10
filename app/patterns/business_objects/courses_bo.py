from typing import List, Optional
from fastapi import Depends

from app.patterns.data_access_objects.courses_dao import (
    CourseDAO,
    LessonDAO,
    get_course_dao,
    get_lesson_dao,
)
from app.schemas.course_schemas import (
    CourseCreate,
    CourseRead,
    CourseUpdate,
    LessonCreate,
    LessonRead,
    LessonReadPartial,
    CourseReadPartial,
)


class CourseBO:
    """Business Object for Course operations with Composite and Chain of Responsibility patterns"""

    def __init__(self, course_dao: CourseDAO, lesson_dao: LessonDAO):
        self.course_dao = course_dao
        self.lesson_dao = lesson_dao

    @classmethod
    async def from_depends(
        cls,
        course_dao: CourseDAO = Depends(get_course_dao),
        lesson_dao: LessonDAO = Depends(get_lesson_dao),
    ):
        """Dependency injection factory method to create an BO instance with DAO dependencies."""
        return cls(course_dao, lesson_dao)

    async def create_course(
        self,
        course_data: CourseCreate,
        instructor_id: int,
    ) -> CourseRead:
        """Create a new course with the provided data."""
        if course_data.price < 0:
            raise ValueError("Course price cannot be negative")
        course_data.instructor_id = instructor_id
        return await self.course_dao.create_course(course_data=course_data)

    async def get_course_by_id(self, course_id: int) -> Optional[CourseRead[LessonReadPartial]]:
        """Get the structure of a course by its ID."""
        curse_model = await self.course_dao.get_course_model_by_id(course_id=course_id)
        print(curse_model.display_content())
        return await self.course_dao.get_course_by_id(course_id=course_id)

    async def get_all_courses(self, offset: int = 0, limit: int = 100) -> List[CourseReadPartial]:
        """Get a paginated list of all business_objects."""
        return await self.course_dao.get_all_courses(offset, limit)

    async def update_course(
            self,
            course_id: int,
            instructor_id: int,
            course_data: CourseUpdate
    ) -> CourseReadPartial:
        """Update a course with the given data."""
        if course_data.price is not None and course_data.price < 0:
            raise ValueError("Course price cannot be negative")
        course = await self.course_dao.get_course_by_id(course_id=course_id)
        if not course:
            raise ValueError("Course not found")
        if course.instructor_id != instructor_id:
            raise ValueError("You do not have permission to update this course")
        return await self.course_dao.update_course(
            course_id=course_id,
            course_data=course_data
        )

    async def delete_course(self, course_id: int, instructor_id: int):
        """Delete a course by its ID."""
        course = await self.course_dao.get_course_by_id(course_id=course_id)
        if not course:
            raise ValueError("Course not found")
        if course.instructor_id != instructor_id:
            raise ValueError("You do not have permission to delete this course")
        await self.course_dao.delete_course(course_id)

    async def create_lessons(self, course_id: int, instructor_id: int, lesson_data: LessonCreate) -> LessonRead:
        """Add a new content item to a course."""
        course = await self.course_dao.get_course_by_id(course_id=course_id)
        if not course:
            raise ValueError("Course not found")
        if course.instructor_id != instructor_id:
            raise ValueError("You do not have permission to add lessons to this course")

        content_item = await self.lesson_dao.create_lesson(
            course_id=course_id,
            lesson_data=lesson_data
        )
        return content_item

    async def get_lesson_by_id(self, course_id: int, lesson_id: int) -> Optional[LessonRead[LessonReadPartial]]:
        """Get a lesson by its ID."""
        return await self.lesson_dao.get_lesson_by_id(
            course_id=course_id,
            lesson_id=lesson_id
        )

    async def delete_lessons(self, course_id: int, instructor_id: int, lesson_id: int):
        """Delete a lesson from a course."""
        course = await self.course_dao.get_course_by_id(course_id=course_id)
        if not course:
            raise ValueError("Course not found")
        if course.instructor_id != instructor_id:
            raise ValueError("You do not have permission to delete lessons from this course")
        await self.lesson_dao.delete_lesson(course_id=course_id, lesson_id=lesson_id)

    async def clone_lesson(
        self, course_id: int, lesson_id: int, new_course_id: int, new_prerequisite_id: int,  instructor_id: int
    ) -> LessonRead:
        """Clone a lesson within a course."""
        course = await self.course_dao.get_course_by_id(course_id=course_id)
        if not course:
            raise ValueError("Course not found")
        if course.instructor_id != instructor_id:
            raise ValueError("You do not have permission to clone lessons in this course")

        cloned_lesson = await self.lesson_dao.clone_lesson(
            course_id=course_id,
            lesson_id=lesson_id,
            new_course_id=new_course_id,
            new_prerequisite_id=new_prerequisite_id
        )
        return cloned_lesson
