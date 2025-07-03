from typing import Generic, TypeVar, List
from pydantic import BaseModel

T = TypeVar('T')


class PaginatedResponse(BaseModel, Generic[T]):
    """Generic schema for paginated responses."""
    page: int
    per_page: int
    total: int | None = None
    items: List[T]