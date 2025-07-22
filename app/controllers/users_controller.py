from fastapi import APIRouter, Depends, Query, HTTPException, status

from app.models.users import User, UserManager, get_user_manager, fastapi_users
from app.schemas.response_schemas import PaginatedResponse
from app.schemas.user_schemas import UserRead
from app.schemas.course_schemas import CourseReadPartial, LessonProgressionRead
from app.patterns.business_objects.students_bo import StudentBO

users_router = APIRouter(prefix="/users", tags=["users"])
"""APIRouter: Router for user-related endpoints."""


# Users Controller
@users_router.get("/", response_model=PaginatedResponse[UserRead])
async def list_all_users(
        page: int = Query(1, ge=1),
        per_page: int = Query(10, le=100),
        user_type: str = Query(None),
        user_manager: UserManager = Depends(get_user_manager),
        current_user: User = Depends(fastapi_users.current_user()),
):
    """List all users with pagination and optional user type filter."""
    offset = (page - 1) * per_page

    if not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to access this resource."
        )

    users = await user_manager.get_all(
        offset=offset,
        limit=per_page,
        user_type=user_type
    )
    return PaginatedResponse(
        items=users,
        total=len(users),
        page=page,
        per_page=per_page
    )


@users_router.get("/my-courses", response_model=PaginatedResponse[CourseReadPartial])
async def get_my_courses(
        current_user: User = Depends(fastapi_users.current_user()),
        student_bo: StudentBO = Depends(StudentBO.from_depends),
        page: int = Query(1, ge=1),
        per_page: int = Query(10, le=100),
):
    """Get all courses for the current user with pagination."""
    if not current_user.is_student:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to access this resource."
        )

    offset = (page - 1) * per_page
    courses = await student_bo. get_student_courses(
        student_id=current_user.id,
        offset=offset,
        limit=per_page
    )
    return PaginatedResponse(
        items=courses,
        total=len(courses),
        page=page,
        per_page=per_page
    )


@users_router.get("/my-course-progression/{course_id}", response_model=PaginatedResponse[LessonProgressionRead])
async def get_course_progression(
        course_id: int,
        current_user: User = Depends(fastapi_users.current_user()),
        student_bo: StudentBO = Depends(StudentBO.from_depends),
        page: int = Query(1, ge=1),
        per_page: int = Query(10, le=100),
):
    """Get the progression of lessons in a course for the current user."""
    if not current_user.is_student:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to access this resource."
        )

    offset = (page - 1) * per_page
    lesson_progressions = await student_bo.get_student_lesson_progressions(
        student_id=current_user.id,
        course_id=course_id,
        offset=offset,
        limit=per_page
    )

    return PaginatedResponse(
        items=lesson_progressions,
        total=len(lesson_progressions),
        page=page,
        per_page=per_page
    )


@users_router.patch("/my-course-progression/{course_id}/{lesson_id}/", response_model=LessonProgressionRead)
async def mark_lesson_completed(
    course_id: int,
    lesson_id: int,
    bo: StudentBO = Depends(StudentBO.from_depends),
    current_user: User = Depends(fastapi_users.current_user()),
):
    """Mark a lesson as completed for the current student."""
    if not current_user.is_student:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to access this resource."
        )
    return await bo.mark_lesson_completed(
        student_id=current_user.id,
        lesson_id=lesson_id,
        course_id=course_id,
    )
