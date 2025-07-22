from typing import List, Optional
from fastapi import Depends

from app.models.users import UserManager, get_user_manager
from app.schemas.course_schemas import CourseReadPartial, LessonProgressionRead
from app.patterns.chain_of_responsability import ConcreteLessonProgressHandler
from app.patterns.data_access_objects.courses_dao import LessonDAO, get_lesson_dao
from app.patterns.data_access_objects.payments_dao import PaymentDAO, get_payment_dao
from app.utils.exceptions import PermissionDeniedError, NotFoundError


class StudentBO:
    """Business Object for Student operations."""

    def __init__(self, user_manager: UserManager, lesson_dao: LessonDAO, payment_dao: PaymentDAO):
        """Initialize the StudentBO with DAO dependencies."""
        self.user_manager = user_manager
        self.lesson_dao = lesson_dao
        self.payment_dao = payment_dao

    @classmethod
    async def from_depends(cls,
            user_manager: UserManager = Depends(get_user_manager),
            lesson_dao: LessonDAO = Depends(get_lesson_dao),
            payment_dao: PaymentDAO = Depends(get_payment_dao)
    ):
        """Dependency injection factory method to create a BO instance with DAO dependencies."""
        return cls(user_manager, lesson_dao, payment_dao)

    async def get_student_courses(
            self, student_id: int, offset: int = 0, limit: int = 100
    ) -> Optional[List[CourseReadPartial]]:
        """Get all courses for a student with pagination."""
        my_payments = await self.user_manager.get_my_courses(
            user_id=student_id,
            offset=offset,
            limit=limit
        )
        if not my_payments:
            return []

        course_list = []

        for payment in my_payments:
            course = payment.course
            if not course:
                continue

            payments, students_enrolled = await self.payment_dao.get_all_payments_by_course(
                course_id=course.id
            )
            course_list.append(
                CourseReadPartial(
                    id=course.id,
                    title=course.title,
                    description=course.description,
                    is_active=True,
                    price=course.price,
                    instructor_id=course.instructor_id,
                    instructor_name=course.instructor.full_name,
                    students_enrolled=students_enrolled
                )
            )
        return course_list

    async def get_student_lesson_progressions(
            self, student_id: int, course_id: int, offset: int = 0, limit: int = 100
    ) -> List[LessonProgressionRead]:
        """Get all lesson progressions for a student in a specific course."""
        lesson_progressions = await self.user_manager.get_my_lesson_progressions(
            user_id=student_id,
            course_id=course_id,
            offset=offset,
            limit=limit
        )

        if not lesson_progressions:
            raise PermissionDeniedError("You did not enroll in this course")
        return [
            LessonProgressionRead(
                id=lp.id,
                user_id=student_id,
                lesson_id=lp.lesson_id,
                lesson_title=lp.lesson.title,
                lesson_type=lp.lesson.lesson_type,
                lesson_prerequisite_id=lp.lesson.prerequisite_id,
                completed=lp.completed,
            )
            for lp in lesson_progressions
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

        return handler.handle(user_id=student_id, user_progress=progress_dict)

    async def mark_lesson_completed(
            self, student_id: int, lesson_id: int, course_id: int
    ) -> LessonProgressionRead:
        """Mark a lesson as completed for a student."""
        if not await self.can_access_lesson(student_id, lesson_id, course_id):
            raise PermissionDeniedError("You do not have permission to change lesson progression")

        lesson_progression = await self.user_manager.mark_lesson_completed(
            user_id=student_id, lesson_id=lesson_id
        )
        return LessonProgressionRead(
            id=lesson_progression.id,
            user_id=lesson_progression.user_id,
            lesson_id=lesson_progression.lesson_id,
            lesson_title=lesson_progression.lesson.title,
            lesson_type=lesson_progression.lesson.lesson_type,
            lesson_prerequisite_id=lesson_progression.lesson.prerequisite_id,
            completed=lesson_progression.completed
        )
