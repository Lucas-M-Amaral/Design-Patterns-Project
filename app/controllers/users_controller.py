from fastapi import APIRouter, Depends, Query, HTTPException, status

from app.models.users import User, UserManager, get_user_manager, fastapi_users
from app.schemas.response_schemas import PaginatedResponse
from app.schemas.user_schemas import UserRead

users_router = APIRouter(prefix="/users", tags=["users"])
"""APIRouter: Router for user-related endpoints."""

# Users Controller
@users_router.get("/", response_model=PaginatedResponse[UserRead])
async def list_all_users(
        page: int = Query(1, ge=1),
        per_page: int = Query(10, le=100),
        user_type: str = Query(None),
        user_manager: UserManager = Depends(get_user_manager),
        current_user: User = Depends(fastapi_users.current_user()), # noqa
):
    """List all users with pagination and optional user type filter."""
    try:
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

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error while listing users: {str(e)}"
        )