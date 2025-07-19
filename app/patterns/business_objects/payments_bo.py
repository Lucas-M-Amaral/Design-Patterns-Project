from typing import List, Optional, Any
from decimal import Decimal
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
from app.utils.exceptions import NotFoundError, ValidationError


class PaymentBO:
    """Business Object for Payment operations."""

    def __init__(self, payment_dao: PaymentDAO, course_dao: CourseDAO):
        self.payment_dao = payment_dao
        self.course_dao = course_dao

    @classmethod
    async def from_depends(cls,
            payment_dao: PaymentDAO = Depends(get_payment_dao),
            course_dao: CourseDAO = Depends(get_course_dao)
    ):
        """Dependency injection factory method to create a BO instance with DAO dependencies."""
        return cls(payment_dao, course_dao)

    @staticmethod
    async def apply_payment_strategy(amount: Decimal, payment_type) -> dict[str, Any]:
        """Apply the appropriate payment strategy based on the payment type."""
        match payment_type:
            case PaymentTypeEnum.CREDIT_CARD:
                strategy = CreditCardPaymentStrategy()
            case PaymentTypeEnum.BILLET:
                strategy = BilletPaymentStrategy()
            case PaymentTypeEnum.PIX:
                strategy = PixPaymentStrategy()
            case _:
                raise ValidationError(f"Unsupported payment type: {payment_type}")

        context = PaymentContext(strategy)
        return context.process_payment(
            amount=float(amount),
            payment_type=payment_type
        )

    async def create_payment(
            self, payment_data: PaymentCreate, user_id: int, course_id: int
    ) -> PaymentRead[CourseReadPartial]:
        course = await self.course_dao.get_course_by_id(course_id=course_id)
        if not course:
            raise NotFoundError("Course not found")

        if payment_data.amount != course.price:
            raise ValidationError("Payment amount does not match course price")

        already_paid = await self.payment_dao.get_payment_get_by_course_id(
            course_id=course_id,
            user_id=user_id
        )
        if already_paid:
            raise ValidationError("Payment for this course has already been made")

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

        payment = await self.payment_dao.create_payment(payment_data=payment_data_dict)

        payment_dict = payment.__dict__.copy()
        payment_dict.update(
            course=CourseReadPartial(
                id=course.id,
                title=course.title,
                description=course.description,
                price=course.price,
                is_active=course.is_active,
                instructor_id=course.instructor_id,
                instructor_name=course.instructor.full_name
            )
        )
        return PaymentRead[CourseReadPartial](**payment_dict)

    async def get_payment_by_id(self, payment_id: int, user_id: int) -> Optional[PaymentRead[CourseReadPartial]]:
        """Get a payment by its ID."""
        payment = await self.payment_dao.get_payment_by_id(
            payment_id=payment_id,
            user_id=user_id
        )
        if not payment:
            raise NotFoundError("Payment not found")

        payment_dict = payment.__dict__.copy()
        payment_dict.update(
            course=CourseReadPartial(
                id=payment.course.id,
                title=payment.course.title,
                description=payment.course.description,
                price=payment.course.price,
                is_active=payment.course.is_active,
                instructor_id=payment.course.instructor_id,
                instructor_name=payment.course.instructor.full_name
            )
        )
        return PaymentRead[CourseReadPartial](
            **payment_dict
        )

    async def get_all_payments(
            self, user_id: int, offset: int = 0, limit: int = 100
    ) -> List[PaymentRead[CourseReadPartial]]:
        """Get a paginated list of all payments."""
        payments = await self.payment_dao.get_all_payments(
            user_id=user_id,
            offset=offset,
            limit=limit
        )

        results = []
        for payment in payments:
            payment_dict = payment.__dict__.copy()
            payment_dict.update(
                course=CourseReadPartial(
                    id=payment.course.id,
                    title=payment.course.title,
                    description=payment.course.description,
                    price=payment.course.price,
                    is_active=payment.course.is_active,
                    instructor_id=payment.course.instructor_id,
                    instructor_name=payment.course.instructor.full_name
                )
            )
            results.append(PaymentRead[CourseReadPartial](**payment_dict))
        return results
