from typing import List
from fastapi import APIRouter, Depends, status
from fastapi.exceptions import HTTPException

from app.models.users import User, fastapi_users
from app.schemas.message_schemas import MessageCreate, MessageRead
from app.patterns.business_objects.messages_bo import MessageBO

messages_router = APIRouter(prefix="/messages", tags=["Messages"])


@messages_router.post("/", response_model=MessageRead, status_code=status.HTTP_201_CREATED)
async def send_message(
    message_data: MessageCreate,
    current_user: User = Depends(fastapi_users.current_user()),
    message_bo: MessageBO = Depends(MessageBO.from_depends),
):
    """Sends a message to the course chat."""
    try:
        return await message_bo.send_message(
            message_data=message_data,
            sender_id=current_user.id
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@messages_router.get("/course/{course_id}", response_model=List[MessageRead])
async def get_messages(
    course_id: int,
    current_user: User = Depends(fastapi_users.current_user()),
    message_bo: MessageBO = Depends(MessageBO.from_depends),
):
    """Retrieves all messages from a course chat."""
    try:
        return await message_bo.get_messages(
            course_id=course_id,
            user_id=current_user.id
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
