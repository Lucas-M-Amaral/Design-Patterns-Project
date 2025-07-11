from enum import Enum
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import ForeignKey, Numeric, Integer, Enum as SQLEnum

from app.utils.models import Base


class PaymentTypeEnum(str, Enum):
    """Enumeration for payment types."""
    PIX = "P"
    CREDIT_CARD = "C"
    BILLET = "B"

    @classmethod
    def get_choices(cls):
        return [(choice.value, choice.name) for choice in cls]


class Payment(Base):
    """Represents a payment made by a user for a course."""
    __tablename__ = "payments"

    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    course_id: Mapped[int] = mapped_column(
        ForeignKey("courses.id", ondelete="CASCADE"), nullable=False
    )
    payment_type: Mapped[PaymentTypeEnum] = mapped_column(
        SQLEnum(PaymentTypeEnum, values_callable=lambda x: [e.value for e in x]),
        nullable=False
    )
    amount: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False)
    installments: Mapped[int] = mapped_column(Integer, nullable=False, default=1)

    # Relationships
    user = relationship(
        "User",
        back_populates="payments",
        lazy="selectin"
    )
    course = relationship(
        "Course",
        back_populates="payments",
        lazy="selectin"
    )
