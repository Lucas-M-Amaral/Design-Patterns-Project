from typing import List
from fastapi import APIRouter, Depends, HTTPException, status

from app.models.users import User, fastapi_users
from app.patterns.business_objects.works_bo import WorkBO
from app.schemas.work_schemas import (
    WorkCreate, WorkRead, WorkAnswerCreate, WorkAnswerRead,
    WorkWithNotifications, WorkAnswerWithNotifications
)

works_router = APIRouter(prefix="/works", tags=["works"])


@works_router.post("/", response_model=WorkWithNotifications)
async def create_work(
    work_data: WorkCreate,
    bo: WorkBO = Depends(WorkBO.from_depends),
    current_user: User = Depends(fastapi_users.current_user()),
):
    """Instructor creates a new work for a course (with student notifications)."""
    if not current_user.is_instructor:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only instructors can create works."
        )
    try:
        return await bo.create_work(work_data=work_data, instructor_id=current_user.id)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@works_router.delete("/{work_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_work(
    work_id: int,
    bo: WorkBO = Depends(WorkBO.from_depends),
    current_user: User = Depends(fastapi_users.current_user()),
):
    """Instructor deletes a work."""
    if not current_user.is_instructor:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only instructors can delete works."
        )
    try:
        await bo.delete_work(work_id=work_id, instructor_id=current_user.id)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@works_router.get("/course/{course_id}", response_model=List[WorkRead])
async def list_works_by_course(
    course_id: int,
    bo: WorkBO = Depends(WorkBO.from_depends),
    current_user: User = Depends(fastapi_users.current_user()),
):
    """
    Lists all works of a course.
    - Instructors: Can view all works of their own courses.
    - Students: Can view works only if enrolled in the course.
    """
    try:
        # ✅ Instrutores podem ver todos os trabalhos do curso
        if current_user.is_instructor:
            return await bo.list_works_by_course(course_id=course_id)

        # ✅ Estudantes só podem ver se estiverem matriculados
        if current_user.is_student:
            is_enrolled = await bo.check_student_enrollment(
                student_id=current_user.id,
                course_id=course_id
            )
            if not is_enrolled:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="You are not enrolled in this course."
                )
            return await bo.list_works_by_course(course_id=course_id)

        # ✅ Qualquer outro tipo de usuário não tem permissão
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to view works of this course."
        )

    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@works_router.get("/{work_id}/answers", response_model=List[WorkAnswerRead])
async def list_answers_by_work(
    work_id: int,
    bo: WorkBO = Depends(WorkBO.from_depends),
    current_user: User = Depends(fastapi_users.current_user()),
):
    """
    Lists answers for a work:
    - Instructors: Can view all answers of the work.
    - Students: Can view only their own answer (if enrolled in the course).
    """
    try:
        if current_user.is_instructor:
            return await bo.list_answers_by_work(work_id=work_id)

        if current_user.is_student:
            return [await bo.get_my_answer_for_work(
                work_id=work_id,
                student_id=current_user.id
            )]

        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to view answers for this work."
        )

    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))



@works_router.post("/answer", response_model=WorkAnswerWithNotifications)
async def submit_or_update_answer(
    answer_data: WorkAnswerCreate,
    bo: WorkBO = Depends(WorkBO.from_depends),
    current_user: User = Depends(fastapi_users.current_user()),
):
    """Student submits or updates their own answer to a work (with instructor notification)."""
    if not current_user.is_student:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only students can submit or update answers."
        )
    try:
        return await bo.submit_answer(answer_data=answer_data, student_id=current_user.id)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@works_router.get("/{work_id}/my-answer", response_model=WorkAnswerRead)
async def get_my_answer_for_work(
    work_id: int,
    bo: WorkBO = Depends(WorkBO.from_depends),
    current_user: User = Depends(fastapi_users.current_user()),
):
    """Student retrieves their own answer for a specific work."""
    if not current_user.is_student:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only students can view their own answers."
        )
    try:
        return await bo.get_my_answer_for_work(work_id=work_id, student_id=current_user.id)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
