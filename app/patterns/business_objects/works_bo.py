from fastapi import Depends
from typing import List

from app.models.users import UserManager, get_user_manager
from app.schemas.work_schemas import (
    WorkCreate, WorkRead, WorkAnswerCreate, WorkAnswerRead,
    WorkWithNotifications, WorkAnswerWithNotifications, NotificationRead
)
from app.patterns.data_access_objects.works_dao import (
    WorkDAO, WorkAnswerDAO, get_work_dao, get_work_answer_dao
)
from app.patterns.data_access_objects.courses_dao import CourseDAO, get_course_dao
from app.patterns.data_access_objects.payments_dao import PaymentDAO, get_payment_dao
from app.patterns.observer import (
    NotificationCenter, StudentObserver, InstructorObserver
)


class WorkBO:
    """Business Object for handling works and answers with Observer notifications."""

    def __init__(
        self,
        work_dao: WorkDAO,
        work_answer_dao: WorkAnswerDAO,
        course_dao: CourseDAO,
        payment_dao: PaymentDAO,
        user_manager: UserManager
    ):
        self.work_dao = work_dao
        self.work_answer_dao = work_answer_dao
        self.course_dao = course_dao
        self.payment_dao = payment_dao
        self.user_manager = user_manager

    @classmethod
    async def from_depends(
        cls,
        work_dao: WorkDAO = Depends(get_work_dao),
        work_answer_dao: WorkAnswerDAO = Depends(get_work_answer_dao),
        course_dao: CourseDAO = Depends(get_course_dao),
        payment_dao: PaymentDAO = Depends(get_payment_dao),
        user_manager: UserManager = Depends(get_user_manager),
    ):
        """Dependency injection factory method to create a WorkBO instance with DAO dependencies."""
        return cls(work_dao, work_answer_dao, course_dao, payment_dao, user_manager)

    async def create_work(self, work_data: WorkCreate, instructor_id: int) -> WorkWithNotifications:
        """Instructor posts a new work and students are notified."""
        course = await self.course_dao.get_course_by_id(work_data.course_id)
        if not course:
            raise ValueError("Course not found")
        if course.instructor_id != instructor_id:
            raise ValueError("You do not have permission to post works in this course")

        work_dict = work_data.model_dump()
        work = await self.work_dao.create_work(work_dict)

        payments = await self.payment_dao.get_all_payments_by_course(course.id)
        notification_center = NotificationCenter()
        for payment in payments:
            notification_center.attach(StudentObserver(payment.user_id))

        messages = await notification_center.notify(
            f"New work posted in course '{course.title}': {work.title}"
        )

        return WorkWithNotifications(
            work=WorkRead(
                id=work.id,
                title=work.title,
                questions=work.questions,
                course_id=work.course_id
            ),
            notifications=[NotificationRead(**msg) for msg in messages]
        )

    async def delete_work(self, work_id: int, instructor_id: int):
        """Instructor deletes a work."""
        work = await self.work_dao.get_work_by_id(work_id)
        if not work:
            raise ValueError("Work not found")
        course = await self.course_dao.get_course_by_id(work.course_id)
        if course.instructor_id != instructor_id:
            raise ValueError("You do not have permission to delete this work")
        await self.work_dao.delete_work(work)

    async def submit_answer(self, answer_data: WorkAnswerCreate, student_id: int) -> WorkAnswerWithNotifications:
        """Student submits or updates their answer and instructor is notified."""
        work = await self.work_dao.get_work_by_id(answer_data.work_id)
        if not work:
            raise ValueError("Work not found")

        # Verifies if the student is enrolled in the course
        is_enrolled = await self.check_student_enrollment(
            student_id=student_id,
            course_id=work.course_id
        )
        if not is_enrolled:
            raise ValueError("You are not enrolled in this course and cannot answer this work.")

        answer_dict = {
            "work_id": answer_data.work_id,
            "student_id": student_id,
            "answers": answer_data.answers
        }

        answer = await self.work_answer_dao.submit_or_update_answer(answer_dict)

        # Notify the instructor about the new or updated answer
        course = await self.course_dao.get_course_by_id(work.course_id)
        notification_center = NotificationCenter()
        notification_center.attach(InstructorObserver(course.instructor_id)) # noqa

        messages = await notification_center.notify(
            f"Student {student_id} submitted/updated an answer to work '{work.title}'."
        )

        return WorkAnswerWithNotifications(
            answer=WorkAnswerRead(
                id=answer.id,
                work_id=answer.work_id,
                student_id=answer.student_id,
                answers=answer.answers,
                updated_at=answer.updated_at
            ),
            notifications=[NotificationRead(**msg) for msg in messages]
        )

    async def list_works_by_course(self, course_id: int) -> List[WorkRead]:
        """List all works for a specific course."""
        works = await self.work_dao.get_works_by_course(course_id)
        return [
            WorkRead(
                id=w.id,
                title=w.title,
                questions=w.questions,
                course_id=w.course_id
            )
            for w in works
        ]

    async def list_answers_by_work(self, work_id: int) -> List[WorkAnswerRead]:
        """Retrieve all answers submitted for a specific work."""
        answers = await self.work_answer_dao.get_answers_by_work(work_id)
        return [
            WorkAnswerRead(
                id=a.id,
                work_id=a.work_id,
                student_id=a.student_id,
                answers=a.answers,
                updated_at=a.updated_at
            )
            for a in answers
        ]
    
    async def get_my_answer_for_work(self, work_id: int, student_id: int) -> WorkAnswerRead:
        """
        Retrieve the student's own answer for a specific work.
        Raises ValueError if no answer is found or if the student is not enrolled in the course.
        """
        work = await self.work_dao.get_work_by_id(work_id)
        if not work:
            raise ValueError("Work not found")

        is_enrolled = await self.check_student_enrollment(student_id=student_id, course_id=work.course_id)
        if not is_enrolled:
            raise ValueError("You are not enrolled in this course.")

        answer = await self.work_answer_dao.get_answer_by_student_and_work(
            work_id=work_id,
            student_id=student_id
        )
        if not answer:
            raise ValueError("No answer found for this work by the current student.")

        return WorkAnswerRead(
            id=answer.id,
            work_id=answer.work_id,
            student_id=answer.student_id,
            answers=answer.answers,
            updated_at=answer.updated_at
        )

    async def check_student_enrollment(self, student_id: int, course_id: int) -> bool:
        """
        Check if a student is enrolled in a specific course.
        Uses the PaymentDAO to verify the enrollment.
        """
        payment = await self.payment_dao.get_payment_get_by_course_id(
            course_id=course_id,
            user_id=student_id
        )
        return payment is not None
