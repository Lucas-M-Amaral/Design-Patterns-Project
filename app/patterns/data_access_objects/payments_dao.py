from typing import List, Dict, Any

from fastapi import Depends
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.payments import Payment
from app.models.courses import LessonProgression
from app.db.database import get_async_session


class PaymentDAO:
    """Data Access Object for Payment operations."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_payment(self, payment_data: Dict[str, Any]) -> Payment:
        """Create a new payment with the provided data."""
        payment = Payment(**payment_data)
        self.session.add(payment)
        await self.session.commit()
        await self.session.refresh(payment)

        course_lessons = payment.course.lessons
        if course_lessons:
            # Initialize lesson progression for the user
            for lesson in course_lessons:
                progression = LessonProgression(
                    user_id=payment.user_id,
                    lesson_id=lesson.id,
                    completed=False
                )
                self.session.add(progression)

            await self.session.commit()
        return payment

    async def get_payment_by_id(self, payment_id: int, user_id: int) -> Payment | None:
        """Get a payment by its ID."""
        stmt = (select(Payment)
                .where(Payment.id == payment_id)
                .where(Payment.user_id == user_id)
                .options(selectinload(Payment.course))
        )
        result = await self.session.execute(stmt)
        payment = result.scalars().first()
        if not payment:
            return None
        return payment

    async def get_payment_get_by_course_id(
            self, course_id: int, user_id: int
    ) -> Payment | None:
        """Get a payment by course ID."""
        stmt = (select(Payment)
                .where(Payment.course_id == course_id)
                .where(Payment.user_id == user_id)
                .options(selectinload(Payment.course))
        )
        result = await self.session.execute(stmt)
        payment = result.scalars().first()
        if not payment:
            return None
        return payment

    async def get_all_payments(
            self, user_id: int,  offset: int = 0, limit: int = 100
    ) -> List[Payment]:
        """Get a paginated list of all payments."""
        stmt = (
            select(Payment)
            .where(Payment.user_id == user_id)
            .options(selectinload(Payment.course))
            .offset(offset)
            .limit(limit)
        )
        result = await self.session.execute(stmt)
        payments = result.scalars().all()
        return list[Payment](payments)
    
    async def get_all_payments_by_course(self, course_id: int) -> List[Payment]:
        """Get all payments for a specific course (all enrolled students)."""
        stmt = (
            select(Payment)
            .where(Payment.course_id == course_id)
            .options(selectinload(Payment.user))  # Para acessar o user_id
        )
        result = await self.session.execute(stmt)
        return result.scalars().all()


async def get_payment_dao(session: AsyncSession = Depends(get_async_session)):
    """Dependency to get the PaymentDAO instance."""
    yield PaymentDAO(session)
