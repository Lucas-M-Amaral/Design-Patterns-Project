from typing import List, Dict, Any
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.db.database import get_async_session
from app.models.works import Work, WorkAnswer


class WorkDAO:
    """Data Access Object for Work (assignments)."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_work(self, work_data: Dict[str, Any]) -> Work:
        work = Work(**work_data)
        self.session.add(work)
        await self.session.commit()
        await self.session.refresh(work)
        return work

    async def get_work_by_id(self, work_id: int) -> Work | None:
        result = await self.session.execute(select(Work).where(Work.id == work_id))
        return result.scalars().first()

    async def delete_work(self, work: Work) -> None:
        await self.session.delete(work)
        await self.session.commit()

    async def get_works_by_course(self, course_id: int) -> List[Work]:
        result = await self.session.execute(select(Work).where(Work.course_id == course_id))
        return result.scalars().all()


class WorkAnswerDAO:
    """Data Access Object for Work answers (students' submissions)."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def submit_or_update_answer(self, answer_data: Dict[str, Any]) -> WorkAnswer:
        """Insert a new answer or update existing one for the same student/work."""
        stmt = select(WorkAnswer).where(
            WorkAnswer.student_id == answer_data["student_id"],
            WorkAnswer.work_id == answer_data["work_id"]
        )
        result = await self.session.execute(stmt)
        existing = result.scalars().first()

        if existing:
            existing.answers = answer_data["answers"]
            await self.session.commit()
            await self.session.refresh(existing)
            return existing

        answer = WorkAnswer(**answer_data)
        self.session.add(answer)
        await self.session.commit()
        await self.session.refresh(answer)
        return answer

    async def get_answers_by_work(self, work_id: int) -> List[WorkAnswer]:
        result = await self.session.execute(select(WorkAnswer).where(WorkAnswer.work_id == work_id))
        return result.scalars().all()
    
    async def get_answer_by_student_and_work(self, work_id: int, student_id: int) -> WorkAnswer | None:
        """
        Retrieve a specific student's answer for a given work.
        Returns None if no answer is found.
        """
        stmt = select(WorkAnswer).where(
            WorkAnswer.work_id == work_id,
            WorkAnswer.student_id == student_id
        )
        result = await self.session.execute(stmt)
        return result.scalars().first()



async def get_work_dao(session: AsyncSession = Depends(get_async_session)):
    """Dependency to get the WorkDAO."""
    yield WorkDAO(session)


async def get_work_answer_dao(session: AsyncSession = Depends(get_async_session)):
    """Dependency to get the WorkAnswerDAO."""
    yield WorkAnswerDAO(session)
