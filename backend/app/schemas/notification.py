from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict


class NotificationBase(BaseModel):
    message: str
    is_read: bool = False


class NotificationCreate(NotificationBase):
    user_id: int


class NotificationResponse(NotificationBase):
    id: int
    user_id: int
    created_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


class NotificationUnreadCount(BaseModel):
    unread_count: int
