from datetime import datetime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import ForeignKey, Text, DateTime

from app.utils.models import Base


class Message(Base):
    """Represents a message exchanged in the course (student ↔ professor)."""
    __tablename__ = "messages"

    content: Mapped[str] = mapped_column(Text, nullable=False)
    timestamp: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)

    sender_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    course_id: Mapped[int] = mapped_column(ForeignKey("courses.id"), nullable=False)

    sender = relationship("User", back_populates="messages_sent", lazy="selectin")
    course = relationship("Course", back_populates="messages", lazy="selectin")