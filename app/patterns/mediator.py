import logging
from abc import ABC, abstractmethod
from typing import List

from app.schemas.message_schemas import MessageCreate
from app.models.messages import Message
from app.models.users import UserManager
from app.patterns.data_access_objects.messages_dao import MessageDAO
from app.patterns.data_access_objects.courses_dao import CourseDAO
from app.utils.exceptions import NotFoundError, PermissionDeniedError


# Mediator for Course Chat between students and instructors
class ChatMediator(ABC):
    """Abstract Mediator for course chat communication."""

    @abstractmethod
    async def send_message(self, message_data: MessageCreate, sender_id: int) -> Message:
        """Send a message to the course chat."""
        raise NotImplementedError("This method should be overridden in subclasses")

    @abstractmethod
    async def get_messages(self, course_id: int, user_id: int) -> List[Message]:
        """Retrieve all messages from a course chat."""
        raise NotImplementedError("This method should be overridden in subclasses")


class CourseChatMediator(ChatMediator):
    """Concrete Mediator coordinating communication in a course chat."""

    def __init__(self, message_dao: MessageDAO, user_manager: UserManager, course_dao: CourseDAO):
        self.message_dao = message_dao
        self.user_manager = user_manager
        self.course_dao = course_dao

    async def send_message(self, message_data: MessageCreate, sender_id: int) -> Message:
        """Coordinate the sending of a message to the course chat."""
        course = await self.course_dao.get_course_by_id(course_id=message_data.course_id)
        if not course:
            raise NotFoundError("Course not found")

        if course.instructor_id != sender_id:
            my_courses = await self.user_manager.get_my_courses(user_id=sender_id)
            logging.info(f"User {sender_id} my_courses: {my_courses}")
            course_ids = [p.course.id for p in my_courses if p.course]
            if course.id not in course_ids:
                raise PermissionDeniedError("You do not have access to this course")

        message_dict = message_data.model_dump()
        message_dict.update({"sender_id": sender_id})
        return await self.message_dao.create_message(message_dict)

    async def get_messages(self, course_id: int, user_id: int) -> List[Message]:
        """Coordinate retrieving all messages from a course chat."""
        course = await self.course_dao.get_course_by_id(course_id=course_id)
        if not course:
            raise NotFoundError("Course not found")

        if course.instructor_id != user_id:
            my_courses = await self.user_manager.get_my_courses(user_id=user_id)
            logging.debug(f"User {user_id} my_courses: {my_courses}")
            course_ids = [p.course.id for p in my_courses if p.course]
            if course.id not in course_ids:
                raise PermissionDeniedError("You do not have access to this course")

        messages = await self.message_dao.get_messages_by_course(course_id)
        return list(messages) if not isinstance(messages, list) else messages
