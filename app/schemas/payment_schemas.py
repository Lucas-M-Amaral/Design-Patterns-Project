from typing import Generic, TypeVar
from decimal import Decimal
from pydantic import BaseModel, ConfigDict, Field

from app.models.payments import PaymentTypeEnum
from app.schemas.course_schemas import CourseReadPartial

T = TypeVar('T')


class PaymentCreate(BaseModel):
    """Schema for creating a payment."""
    payment_type: PaymentTypeEnum = Field(..., description="Type of payment method used")
    amount: Decimal = Field(..., ge=0, description="Total amount to be paid")


class PaymentRead(BaseModel, Generic[T]):
    """Schema for reading a payment."""
    id: int = Field(..., description="Unique identifier for the payment")
    amount: Decimal = Field(..., ge=0, description="Total amount paid")
    payment_type: PaymentTypeEnum = Field(..., description="Type of payment method used")
    installments: int = Field(..., ge=1, description="Number of installments for the payment")
    user_id: int = Field(..., description="ID of the user who made the payment")
    course_id: int = Field(..., description="ID of the course paid for")
    course: CourseReadPartial = Field(..., description="Details of the course associated with the payment")

    model_config = ConfigDict(from_attributes=True)
