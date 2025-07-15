from typing import List
from fastapi import APIRouter, Depends, status
from fastapi.exceptions import HTTPException

from app.schemas.message_schemas import MessageCreate, MessageRead
from app.patterns.business_objects.messages_bo import MessageBO

messages_router = APIRouter(prefix="/messages", tags=["Messages"])


@messages_router.post("/", response_model=MessageRead, status_code=status.HTTP_201_CREATED)
async def send_message(
    message_data: MessageCreate,
    user_id: int,  # Substitua por Depends(get_current_user) se necessário
    message_bo: MessageBO = Depends(MessageBO.from_depends),
):
    """Envia uma mensagem no chat do curso (se o usuário estiver autorizado)."""
    try:
        return await message_bo.send_message(message_data, sender_id=user_id)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@messages_router.get("/course/{course_id}", response_model=List[MessageRead])
async def get_messages(
    course_id: int,
    user_id: int,  # Substitua por Depends(get_current_user) se necessário
    message_bo: MessageBO = Depends(MessageBO.from_depends),
):
    """Retorna todas as mensagens do curso (se o usuário for participante)."""
    try:
        return await message_bo.get_messages(course_id, user_id)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))
