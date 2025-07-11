from typing import List, Optional, Any
from fastapi import Depends

from app.models.payments import PaymentTypeEnum
from app.patterns.strategy import (
    PaymentContext,
    CreditCardPaymentStrategy,
    BilletPaymentStrategy,
    PixPaymentStrategy
)
from app.patterns.data_access_objects.courses_dao import CourseDAO, get_course_dao
from app.patterns.data_access_objects.payments_dao import PaymentDAO, get_payment_dao
from app.schemas.payment_schemas import PaymentCreate, PaymentRead, CourseReadPartial


class PaymentBO:
    """Business Object for Payment operations."""

    def __init__(self, payment_dao: PaymentDAO, course_dao: CourseDAO):
        self.payment_dao = payment_dao
        self.course_dao = course_dao

    @classmethod
    async def from_depends(
            cls,
            payment_dao: PaymentDAO = Depends(get_payment_dao),
            course_dao: CourseDAO = Depends(get_course_dao)
    ):
        """Dependency injection factory method to create a BO instance with DAO dependencies."""
        return cls(payment_dao, course_dao)

    @staticmethod
    async def apply_payment_strategy(amount: float, payment_type) -> dict[str, Any]:
        """Apply the appropriate payment strategy based on the payment type."""
        match payment_type:
            case PaymentTypeEnum.CREDIT_CARD:
                strategy = CreditCardPaymentStrategy()
            case PaymentTypeEnum.BILLET:
                strategy = BilletPaymentStrategy()
            case PaymentTypeEnum.PIX:
                strategy = PixPaymentStrategy()
            case _:
                raise ValueError(f"Unsupported payment type: {payment_type}")

        context = PaymentContext(strategy)
        return context.process_payment(
            amount=amount,
            payment_type=payment_type
        )

    async def create_payment(
            self, payment_data: PaymentCreate, user_id: int, course_id: int
    ) -> PaymentRead:
        """Create a new payment with the provided data."""
        if payment_data.amount < 0:
            raise ValueError("Payment amount cannot be negative")

        course = await self.course_dao.get_course_by_id(course_id=course_id)
        if not course:
            raise ValueError("Course not found")

        if course.price != payment_data.amount:
            raise ValueError("Payment amount does not match course price")

        already_paid = await self.payment_dao.get_payment_get_by_course_id(
            course_id=course_id,
            user_id=user_id
        )
        if already_paid:
            raise ValueError("Payment for this course has already been made")

        strategy = await self.apply_payment_strategy(
            amount=payment_data.amount,
            payment_type=payment_data.payment_type
        )

        payment_data_dict = payment_data.model_dump()
        payment_data_dict.update({
            "user_id": user_id,
            "course_id": course_id,
            "amount": strategy["amount"],
            "installments": strategy["installments"],
        })

        return await self.payment_dao.create_payment(payment_data=payment_data_dict)

    async def get_payment_by_id(self, payment_id: int, user_id: int) -> Optional[PaymentRead[CourseReadPartial]]:
        """Get a payment by its ID."""
        return await self.payment_dao.get_payment_by_id(
            payment_id=payment_id,
            user_id=user_id
        )

    async def get_all_payments(
            self, user_id: int, offset: int = 0, limit: int = 100
    ) -> List[PaymentRead[CourseReadPartial]]:
        """Get a paginated list of all payments."""
        return await self.payment_dao.get_all_payments(
            user_id=user_id,
            offset=offset,
            limit=limit
        )
