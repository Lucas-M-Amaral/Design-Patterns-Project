from fastapi import Depends
from typing import List

from app.models.users import UserManager, get_user_manager
from app.patterns.data_access_objects.messages_dao import MessageDAO, get_message_dao
from app.patterns.data_access_objects.courses_dao import CourseDAO, get_course_dao
from app.schemas.message_schemas import MessageCreate, MessageRead
from app.patterns.mediator import CourseChatMediator


class MessageBO:
    """Business Object that delegates to the Mediator for message exchange."""

    def __init__(self, mediator: CourseChatMediator):
        self.mediator = mediator

    @classmethod
    async def from_depends(
        cls,
        message_dao: MessageDAO = Depends(get_message_dao),
        user_manager: UserManager = Depends(get_user_manager),
        course_dao: CourseDAO = Depends(get_course_dao),
    ):
        """Dependency injection factory method to create a BO instance with DAO dependencies."""
        mediator = CourseChatMediator(
            message_dao=message_dao,
            user_manager=user_manager,
            course_dao=course_dao
        )
        return cls(mediator)

    async def send_message(self, message_data: MessageCreate, sender_id: int) -> MessageRead:
        """Sends a message to the course chat."""
        message = await self.mediator.send_message(message_data, sender_id)
        return MessageRead.model_validate(message)

    async def get_messages(self, course_id: int, user_id: int) -> List[MessageRead]:
        """Retrieves all messages from a course chat."""
        messages = await self.mediator.get_messages(course_id, user_id)
        return [MessageRead.model_validate(m) for m in messages]
