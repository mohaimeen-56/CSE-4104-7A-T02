from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field, ConfigDict


class RegionBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    country: str = Field(default="Bangladesh", max_length=100)


class RegionCreate(RegionBase):
    pass


class RegionUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    country: Optional[str] = Field(None, max_length=100)


class RegionResponse(RegionBase):
    id: int
    created_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)
