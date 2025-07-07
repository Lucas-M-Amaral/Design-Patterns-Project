from typing import Generic, TypeVar, List
from pydantic import BaseModel, Field

T = TypeVar('T')


class PaginatedResponse(BaseModel, Generic[T]):
    """Generic schema for paginated responses."""
    page: int = Field(..., ge=1, description="Current page number")
    per_page: int = Field(..., ge=1, description="Number of items per page")
    total: int | None = Field(None, description="Total number of items")
    items: List[T] = Field(..., description="List of items on the current page")
