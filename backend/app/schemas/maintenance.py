from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field


class MaintenanceStatus(BaseModel):
    enabled: bool
    message: str
    enabled_by_name: Optional[str] = None
    started_at: Optional[datetime] = None
    reason: Optional[str] = None


class MaintenanceEnableRequest(BaseModel):
    reason: str = Field(..., min_length=1, max_length=500)
    message: Optional[str] = Field(None, max_length=500)


class MaintenanceDisableRequest(BaseModel):
    reason: Optional[str] = Field(None, max_length=500)


class MaintenanceLogItem(BaseModel):
    id: int
    action: str
    performed_by_name: Optional[str] = None
    reason: Optional[str] = None
    created_at: datetime
