from datetime import date, datetime
from typing import Optional, List
from decimal import Decimal
from pydantic import BaseModel, Field, ConfigDict
from app.schemas.product import ProductResponse
from app.schemas.region import RegionResponse
from app.schemas.user import UserResponse


class SaleBase(BaseModel):
    product_id: int
    region_id: int
    quantity: int = Field(..., gt=0)
    unit_price: Decimal = Field(..., ge=0)
    sale_date: date
    sale_time: Optional[str] = Field(
        None, description="Time of day as HH:MM or HH:MM:SS. Omit to let the server use its current time-of-day."
    )


class SaleCreate(SaleBase):
    pass


class SaleUpdate(BaseModel):
    product_id: Optional[int] = None
    region_id: Optional[int] = None
    quantity: Optional[int] = Field(None, gt=0)
    unit_price: Optional[Decimal] = Field(None, ge=0)
    sale_date: Optional[date] = None
    sale_time: Optional[str] = None


class SaleResponse(BaseModel):
    id: int
    user_id: Optional[int] = None
    product_id: int
    region_id: int
    quantity: int
    unit_price: float
    total_price: float
    sale_date: date
    sale_datetime: datetime
    is_estimated_time: bool
    created_at: Optional[datetime] = None

    # Nested info for rich display
    product: Optional[ProductResponse] = None
    region: Optional[RegionResponse] = None
    user: Optional[UserResponse] = None

    model_config = ConfigDict(from_attributes=True)


class CsvRowError(BaseModel):
    row: int
    message: str
    data: Optional[dict] = None


class CsvUploadResponse(BaseModel):
    total_rows: int
    imported_rows: int
    failed_rows: int
    errors: List[CsvRowError] = []
