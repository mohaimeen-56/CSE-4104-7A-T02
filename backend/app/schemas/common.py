from typing import Generic, TypeVar, Optional, Any, List
from pydantic import BaseModel

T = TypeVar("T")


class APIResponse(BaseModel, Generic[T]):
    success: bool = True
    message: str = "Operation successful"
    data: Optional[T] = None


class PaginationMeta(BaseModel):
    page: int
    page_size: int
    total: int
    total_pages: int


class PaginatedResponse(BaseModel, Generic[T]):
    success: bool = True
    message: str = "Data retrieved successfully"
    data: List[T]
    pagination: PaginationMeta


class ErrorDetail(BaseModel):
    code: str
    message: str
    details: Optional[Any] = None


class APIErrorResponse(BaseModel):
    success: bool = False
    error: ErrorDetail
