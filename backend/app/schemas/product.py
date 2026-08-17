from datetime import datetime
from decimal import Decimal
from typing import Optional, Literal
from pydantic import BaseModel, Field, ConfigDict

ProductionLevel = Literal["low", "medium", "high"]


class ProductBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    category: Optional[str] = Field(None, max_length=50)
    subcategory: Optional[str] = Field(None, max_length=50)
    brand: Optional[str] = Field(None, max_length=100)
    sku: Optional[str] = Field(None, max_length=50)
    description: Optional[str] = None
    price: Optional[Decimal] = Field(None, ge=0)
    cost: Optional[Decimal] = Field(None, ge=0)
    stock: int = Field(default=0, ge=0)
    production_level: Optional[ProductionLevel] = None
    is_active: bool = True


class ProductCreate(ProductBase):
    pass


class ProductUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    category: Optional[str] = Field(None, max_length=50)
    subcategory: Optional[str] = Field(None, max_length=50)
    brand: Optional[str] = Field(None, max_length=100)
    sku: Optional[str] = Field(None, max_length=50)
    description: Optional[str] = None
    price: Optional[Decimal] = Field(None, ge=0)
    cost: Optional[Decimal] = Field(None, ge=0)
    stock: Optional[int] = Field(None, ge=0)
    production_level: Optional[ProductionLevel] = None
    is_active: Optional[bool] = None


class ProductResponse(ProductBase):
    id: int
    created_at: Optional[datetime] = None
    effective_production_level: Optional[ProductionLevel] = None

    model_config = ConfigDict(from_attributes=True)
