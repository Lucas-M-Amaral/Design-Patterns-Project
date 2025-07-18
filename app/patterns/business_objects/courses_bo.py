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

        course_data_dict = course_data.model_dump()
        course_data_dict.update({"instructor_id": instructor_id})

        course = await self.course_dao.create_course(course_data=course_data_dict)
        return CourseRead(
            id=course.id,
            title=course.title,
            description=course.description,
            price=course.price,
            is_active=course.is_active,
            instructor_id=course.instructor_id,
            instructor_name=course.instructor.full_name,
        )

    async def get_course_by_id(self, course_id: int) -> Optional[CourseRead[LessonReadPartial]]:
        """Get the structure of a course by its ID."""
        import logging

        course = await self.course_dao.get_course_by_id(course_id=course_id)
        if not course:
            raise ValueError("Course not found")
        logging.info(course.display_content())
        lessons_list = [LessonReadPartial.model_validate(lesson) for lesson in course.lessons]
        return CourseRead[LessonReadPartial](
            id=course.id,
            title=course.title,
            description=course.description,
            price=course.price,
            is_active=course.is_active,
            instructor_id=course.instructor_id,
            instructor_name=course.instructor.full_name,
            lessons=lessons_list
        )

    async def get_all_courses(self, offset: int = 0, limit: int = 100) -> List[CourseReadPartial]:
        """Get a paginated list of all business_objects."""
        courses =  await self.course_dao.get_all_courses(offset, limit)
        return [
            CourseReadPartial(
                id=course.id,
                title=course.title,
                description=course.description,
                price=course.price,
                is_active=course.is_active,
                instructor_id=course.instructor_id,
                instructor_name=course.instructor.full_name
            )
            for course in courses
        ]

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

        updated_course =  await self.course_dao.update_course(
            course=course,
            course_data=course_data.model_dump()
        )
        return CourseReadPartial.model_validate(updated_course)

    async def delete_course(self, course_id: int, instructor_id: int):
        """Delete a course by its ID."""
        course = await self.course_dao.get_course_by_id(course_id=course_id)
        if not course:
            raise ValueError("Course not found")
        if course.instructor_id != instructor_id:
            raise ValueError("You do not have permission to delete this course")
        await self.course_dao.delete_course(course=course)

    async def create_lessons(self, course_id: int, instructor_id: int, lesson_data: LessonCreate) -> LessonRead:
        """Add a new content item to a course."""
        course = await self.course_dao.get_course_by_id(course_id=course_id)
        if not course:
            raise ValueError("Course not found")
        if course.instructor_id != instructor_id:
            raise ValueError("You do not have permission to add lessons to this course")

        pre_requisite_id = lesson_data.prerequisite_id
        parent_id = lesson_data.parent_id

        lesson_data = lesson_data.model_dump()
        lesson_data.update({"course_id": course_id})

        if pre_requisite_id is not None:
            pre_requisite = await self.lesson_dao.get_prerequisite_lesson(
                course_id=course_id,
                pre_requisite_id=pre_requisite_id,
            )
            if not pre_requisite:
                raise ValueError("Prerequisite lesson not found")
            if pre_requisite.course_id != course_id:
                raise ValueError("Prerequisite lesson must belong to the same course")

        if parent_id is not None:
            parent = await self.lesson_dao.get_parent_lesson(
                course_id=course_id,
                parent_id=parent_id,
            )
            if not parent:
                raise ValueError("Module lesson not found")
            if not parent.is_module:
                raise ValueError("Parent lesson must be a module")

        if pre_requisite_id is not None and parent_id is not None:
            if pre_requisite_id == parent_id:
                raise ValueError("Prerequisite and parent cannot be the same lesson")

        lesson = await self.lesson_dao.create_lesson(
            lesson_data=lesson_data,
        )
        return LessonRead.model_validate(lesson)

    async def get_lesson_by_id(self, course_id: int, lesson_id: int) -> Optional[LessonRead[LessonReadPartial]]:
        """Get a lesson by its ID."""
        lesson =  await self.lesson_dao.get_lesson_by_id(
            course_id=course_id,
            lesson_id=lesson_id
        )
        if not lesson:
            raise ValueError("Lesson not found for this course")
        return LessonRead[LessonReadPartial].model_validate(lesson)

    async def delete_lessons(self, course_id: int, instructor_id: int, lesson_id: int):
        """Delete a lesson from a course."""
        lesson = await self.lesson_dao.get_lesson_by_id(
            course_id=course_id,
            lesson_id=lesson_id
        )
        if not lesson:
            raise ValueError("Lesson not found for this course")

        has_dependants = await self.lesson_dao.has_dependants(lesson_id=lesson.id)
        if has_dependants:
            raise ValueError("Cannot delete a lesson that has prerequisites")

        course = await self.course_dao.get_course_by_id(course_id=course_id)
        if course.instructor_id != instructor_id:
            raise ValueError("You do not have permission to delete lessons from this course")
        await self.lesson_dao.delete_lesson(lesson=lesson)

    async def clone_lesson(
        self, course_id: int, lesson_id: int, new_course_id: int, new_prerequisite_id: int,  instructor_id: int
    ) -> LessonRead:
        """Clone a lesson within a course."""
        course = await self.course_dao.get_course_by_id(course_id=course_id)
        lesson = await self.lesson_dao.get_lesson_by_id(
            course_id=course_id,
            lesson_id=lesson_id
        )
        if not course:
            raise ValueError("Course not found")
        if not lesson:
            raise ValueError("Lesson not found for this course")
        if not lesson.is_module:
            raise ValueError("Only module lessons can be cloned")
        if course.instructor_id != instructor_id:
            raise ValueError("You do not have permission to clone lessons in this course")

        cloned_lesson = await self.lesson_dao.clone_lesson(
            course_id=course_id,
            lesson_id=lesson_id,
            new_course_id=new_course_id,
            new_prerequisite_id=new_prerequisite_id
        )
        return LessonRead.model_validate(cloned_lesson)
