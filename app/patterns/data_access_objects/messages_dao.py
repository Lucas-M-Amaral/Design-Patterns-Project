from typing import List
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.db.database import get_async_session
from app.models.messages import Message


class MessageDAO:
    """Data Access Object for handling messages."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_message(self, message_data: dict) -> Message:
        """Create a new message."""
        message = Message(**message_data)
        self.session.add(message)
        await self.session.commit()
        await self.session.refresh(message)
        return message

    async def get_messages_by_course(self, course_id: int) -> List[Message]:
        """Get all messages in a course."""
        stmt = select(Message).where(Message.course_id == course_id).order_by(Message.timestamp)
        result = await self.session.execute(stmt)
        return result.scalars().all()


async def get_message_dao(session: AsyncSession = Depends(get_async_session)):
    """Dependency to get the MessageDAO instance."""
    yield MessageDAO(session)
