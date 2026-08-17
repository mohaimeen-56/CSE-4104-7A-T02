from typing import List
from fastapi import APIRouter, Depends, Query, HTTPException, status
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.schemas.notification import NotificationResponse, NotificationUnreadCount
from app.schemas.common import APIResponse
from app.services.notification_service import NotificationService
from app.core.deps import get_current_user
from app.models.user import User

router = APIRouter(prefix="/notifications", tags=["Notifications"])


@router.get("", response_model=APIResponse[List[NotificationResponse]])
def get_notifications(
    limit: int = Query(20, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    notifs = NotificationService.get_user_notifications(db, user_id=current_user.id, limit=limit)
    return APIResponse(
        success=True,
        message="Notifications retrieved",
        data=[NotificationResponse.model_validate(n) for n in notifs]
    )


@router.get("/unread-count", response_model=APIResponse[NotificationUnreadCount])
def get_unread_count(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    count = NotificationService.get_unread_count(db, user_id=current_user.id)
    return APIResponse(
        success=True,
        message="Unread notification count retrieved",
        data=NotificationUnreadCount(unread_count=count)
    )


@router.put("/{notification_id}/read", response_model=APIResponse[NotificationResponse])
def mark_notification_as_read(
    notification_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    notif = NotificationService.mark_as_read(db, notification_id=notification_id, user_id=current_user.id)
    return APIResponse(
        success=True,
        message="Notification marked as read",
        data=NotificationResponse.model_validate(notif)
    )


@router.put("/read-all", response_model=APIResponse[dict])
def mark_all_as_read(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    count = NotificationService.mark_all_as_read(db, user_id=current_user.id)
    return APIResponse(
        success=True,
        message=f"{count} notifications marked as read",
        data={"updated_count": count}
    )
