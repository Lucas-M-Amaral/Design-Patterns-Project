from fastapi import Query, Depends, APIRouter, HTTPException, status

from app.models.users import User, fastapi_users
from app.patterns.business_objects.courses_bo import CourseBO
from app.schemas.response_schemas import PaginatedResponse
from app.schemas.course_schemas import (
    CourseCreate,
    CourseRead,
    CourseReadPartial,
    CourseUpdate,
    LessonCreate,
    LessonRead,
    LessonReadPartial
)

courses_router = APIRouter(prefix="/courses", tags=["courses"])
"""APIRouter: Router for course-related endpoints."""


@courses_router.post("/", response_model=CourseRead)
async def create_course(
    course_data: CourseCreate,
    bo: CourseBO = Depends(CourseBO.from_depends),
    current_user: User = Depends(fastapi_users.current_user()),
):
    """Create a new course with the provided data."""
    if not current_user.is_instructor:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to create a course."
        )
    try:
        return await bo.create_course(
            course_data=course_data,
            instructor_id=current_user.id,
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@courses_router.get("/", response_model=PaginatedResponse[CourseReadPartial])
async def get_all_courses(
    bo: CourseBO = Depends(CourseBO.from_depends),
    current_user: User = Depends(fastapi_users.current_user()), # noqa
    page: int = Query(1, ge=1),
    per_page: int = Query(10, le=100),
):
    """Get a paginated list of all business_objects."""
    offset = (page - 1) * per_page
    try:
        items = await bo.get_all_courses(
            offset=offset,
            limit=per_page
        )
        return PaginatedResponse[CourseRead](
            page=page,
            per_page=per_page,
            total=len(items),
            items=items
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@courses_router.get("/{course_id}", response_model=CourseRead[LessonReadPartial])
async def get_course_by_id(
    course_id: int,
    bo: CourseBO = Depends(CourseBO.from_depends),
    current_user: User = Depends(fastapi_users.current_user()),  # noqa
):
    """Get the structure of a course by its ID."""
    try:
        return await bo.get_course_by_id(course_id=course_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@courses_router.patch("/{course_id}", response_model=CourseReadPartial)
async def update_course(
    course_id: int,
    course_data: CourseUpdate,
    bo: CourseBO = Depends(CourseBO.from_depends),
    current_user: User = Depends(fastapi_users.current_user()),
):
    """Update a course with the given data."""
    if not current_user.is_instructor:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to update this course."
        )
    try:
        return await bo.update_course(
            course_id=course_id,
            instructor_id=current_user.id,
            course_data=course_data
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@courses_router.delete("/{course_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_course(
    course_id: int,
    bo: CourseBO = Depends(CourseBO.from_depends),
    current_user: User = Depends(fastapi_users.current_user()),
):
    """Delete a course by its ID."""
    try:
        if not current_user.is_instructor:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You do not have permission to delete this course."
            )
        await bo.delete_course(course_id=course_id, instructor_id=current_user.id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@courses_router.post("/{course_id}/lessons", response_model=LessonRead[LessonReadPartial])
async def create_lesson(
    course_id: int,
    lesson_data: LessonCreate,
    bo: CourseBO = Depends(CourseBO.from_depends),
    current_user: User = Depends(fastapi_users.current_user()),
):
    """Add a new lesson to a course."""
    if not current_user.is_instructor:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to add lessons to this course."
        )
    try:
        return await bo.create_lessons(
            course_id=course_id,
            instructor_id=current_user.id,
            lesson_data=lesson_data
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@courses_router.get("/{course_id}/lessons/{lesson_id}", response_model=LessonRead)
async def get_lesson_by_id(
    course_id: int,
    lesson_id: int,
    bo: CourseBO = Depends(CourseBO.from_depends),
    current_user: User = Depends(fastapi_users.current_user()), # noqa
):
    """Get a lesson by its ID."""
    try:
        return await bo.get_lesson_by_id(
            course_id=course_id,
            lesson_id=lesson_id
        )
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@courses_router.delete("/{course_id}/lessons/{lesson_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_lesson(
    course_id: int,
    lesson_id: int,
    bo: CourseBO = Depends(CourseBO.from_depends),
    current_user: User = Depends(fastapi_users.current_user()),
):
    """Delete a lesson from a course."""
    try:
        if not current_user.is_instructor:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You do not have permission to delete lessons from this course."
            )
        await bo.delete_lessons(
            course_id=course_id,
            instructor_id=current_user.id,
            lesson_id=lesson_id
        )
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
