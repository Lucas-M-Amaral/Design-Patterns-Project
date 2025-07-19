from typing import List, Optional
from fastapi import Depends

from app.models.users import UserManager, get_user_manager
from app.schemas.course_schemas import CourseReadPartial
from app.patterns.chain_of_responsability import ConcreteLessonProgressHandler
from app.patterns.data_access_objects.courses_dao import LessonDAO, get_lesson_dao
from app.utils.exceptions import PermissionDeniedError, NotFoundError


class StudentBO:
    """Business Object for Student operations."""

    def __init__(self, user_manager: UserManager, lesson_dao: LessonDAO):
        self.user_manager = user_manager
        self.lesson_dao = lesson_dao

    @classmethod
    async def from_depends(cls,
            user_manager: UserManager = Depends(get_user_manager),
            lesson_dao: LessonDAO = Depends(get_lesson_dao)
    ):
        """Dependency injection factory method to create a BO instance with DAO dependencies."""
        return cls(user_manager, lesson_dao)

    async def get_student_courses(
            self, student_id: int, offset: int = 0, limit: int = 100
    ) -> Optional[List[CourseReadPartial]]:
        """Get all courses for a student with pagination."""
        my_courses = await self.user_manager.get_my_courses(
            user_id=student_id,
            offset=offset,
            limit=limit
        )
        if not my_courses:
            return []
        return [
            CourseReadPartial.model_validate(payment.course)
            for payment in my_courses
            if payment.course is not None
        ]

    async def can_access_lesson(
            self, student_id: int, lesson_id: int, course_id: int
    ) -> bool:
        """Check if a student can access a specific lesson."""
        lesson_progressions = await self.user_manager.get_my_lesson_progressions(
            user_id=student_id
        )
        if not lesson_progressions:
            raise PermissionDeniedError("You did not enroll in this course")
        progress_dict = {lp.lesson_id: lp for lp in lesson_progressions}

        lesson = await self.lesson_dao.get_lesson_by_id(
            lesson_id=lesson_id,
            course_id=course_id
        )
        if not lesson:
            raise NotFoundError(f"Lesson with ID {lesson_id} not found in course {course_id}")

        handler = ConcreteLessonProgressHandler(lesson=lesson)

        can_access = handler.handle(user_id=student_id, user_progress=progress_dict)
        if can_access:
            progression = progress_dict.get(lesson_id)
            if not progression or not progression.completed:
                await self.user_manager.mark_lesson_completed(student_id, lesson_id)
        return can_access
