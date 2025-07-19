from fastapi import Query, Depends, APIRouter, HTTPException, status

from app.models.users import User, fastapi_users
from app.patterns.business_objects.payments_bo import PaymentBO
from app.schemas.response_schemas import PaginatedResponse
from app.schemas.course_schemas import CourseReadPartial
from app.schemas.payment_schemas import PaymentCreate, PaymentRead


payments_router = APIRouter(prefix="/payments", tags=["payments"])
"""APIRouter: Router for payment-related endpoints."""


@payments_router.post("/course/{course_id}", response_model=PaymentRead)
async def create_payment(
    course_id: int,
    payment_data: PaymentCreate,
    current_user: User = Depends(fastapi_users.current_user()),
    bo: PaymentBO = Depends(PaymentBO.from_depends)
):
    """Create a new payment with the provided data."""
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to make a payment."
        )
    return await bo.create_payment(
        payment_data=payment_data,
        user_id=current_user.id,
        course_id=course_id,
    )


@payments_router.get("/", response_model=PaginatedResponse[PaymentRead[CourseReadPartial]])
async def get_all_payments(
    bo: PaymentBO = Depends(PaymentBO.from_depends),
    current_user: User = Depends(fastapi_users.current_user()),
    page: int = Query(1, ge=1),
    per_page: int = Query(10, le=100),
):
    """Get a paginated list of all payments."""
    offset = (page - 1) * per_page
    items = await bo.get_all_payments(
        user_id=current_user.id,
        offset=offset,
        limit=per_page
    )
    return PaginatedResponse[PaymentRead](
        page=page,
        per_page=per_page,
        total=len(items),
        items=items
    )


@payments_router.get("/{payment_id}", response_model=PaymentRead[CourseReadPartial])
async def get_payment_by_id(
    payment_id: int,
    bo: PaymentBO = Depends(PaymentBO.from_depends),
    current_user: User = Depends(fastapi_users.current_user()),
):
    """Get a payment by its ID."""
    return await bo.get_payment_by_id(
        payment_id=payment_id,
        user_id=current_user.id
    )
