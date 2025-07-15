from typing import List
from fastapi import Depends

from app.models.users import UserManager, get_user_manager
from app.patterns.data_access_objects.messages_dao import MessageDAO, get_message_dao
from app.patterns.data_access_objects.courses_dao import CourseDAO, get_course_dao
from app.schemas.message_schemas import MessageCreate, MessageRead


class MessageBO:
    """Business Object (Mediator) to manage message exchange between course participants."""

    def __init__(self, message_dao: MessageDAO, user_manager: UserManager, course_dao: CourseDAO):
        self.message_dao = message_dao
        self.user_manager = user_manager
        self.course_dao = course_dao

    @classmethod
    async def from_depends(
        cls,
        message_dao: MessageDAO = Depends(get_message_dao),
        user_manager: UserManager = Depends(get_user_manager),
        course_dao: CourseDAO = Depends(get_course_dao)
    ):
        return cls(message_dao, user_manager, course_dao)

    async def send_message(self, message_data: MessageCreate, sender_id: int) -> MessageRead:
        """Send a message to the course chat if the user is allowed."""

        # Validates if the message data is valid
        course = await self.course_dao.get_course_by_id(course_id=message_data.course_id)
        if not course:
            raise ValueError("Course not found")

        # Verifies if the user is a participant in the course (either a paying student or the instructor)
        if course.instructor_id == sender_id:
            pass  # The user is the instructor, so they can send messages
        else:
            my_courses = await self.user_manager.get_my_courses(user_id=sender_id)
            course_ids = [p.course.id for p in my_courses if p.course]
            if course.id not in course_ids:
                raise ValueError("You do not have access to this course")

        message_dict = message_data.model_dump()
        message_dict.update({"sender_id": sender_id})

        message = await self.message_dao.create_message(message_dict)
        return MessageRead.model_validate(message)

    async def get_messages(self, course_id: int, user_id: int) -> List[MessageRead]:
        """Retrieve all messages from a course, if the user is a participant."""

        # Verifies if the course exists
        course = await self.course_dao.get_course_by_id(course_id=course_id)
        if not course:
            raise ValueError("Course not found")

        # Verifies if the user is a participant in the course (either a paying student or the instructor)
        if course.instructor_id == user_id:
            pass
        else:
            my_courses = await self.user_manager.get_my_courses(user_id=user_id)
            course_ids = [p.course.id for p in my_courses if p.course]
            if course.id not in course_ids:
                raise ValueError("You do not have access to this course")

        messages = await self.message_dao.get_messages_by_course(course_id)
        return [MessageRead.model_validate(m) for m in messages]
