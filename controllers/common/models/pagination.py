from pydantic import BaseModel
from typing import TypeVar, Generic

T = TypeVar('T')

class PaginatedResponse(BaseModel, Generic[T]):
    total: int
    current_page: int
    page_size: int
    results: list[T]