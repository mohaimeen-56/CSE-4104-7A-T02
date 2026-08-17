from typing import List, Optional
from datetime import datetime
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from app.models.notification import Notification
from app.models.user import User


class NotificationService:
    @staticmethod
    def get_user_notifications(db: Session, user_id: int, limit: int = 50) -> List[Notification]:
        return (
            db.query(Notification)
            .filter(Notification.user_id == user_id)
            .order_by(Notification.created_at.desc())
            .limit(limit)
            .all()
        )

    @staticmethod
    def get_unread_count(db: Session, user_id: int) -> int:
        return (
            db.query(Notification)
            .filter(Notification.user_id == user_id, Notification.is_read == False)
            .count()
        )

    @staticmethod
    def mark_as_read(db: Session, notification_id: int, user_id: int) -> Notification:
        notif = (
            db.query(Notification)
            .filter(Notification.id == notification_id, Notification.user_id == user_id)
            .first()
        )
        if not notif:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Notification not found")
        notif.is_read = True
        db.add(notif)
        db.commit()
        db.refresh(notif)
        return notif

    @staticmethod
    def mark_all_as_read(db: Session, user_id: int) -> int:
        count = (
            db.query(Notification)
            .filter(Notification.user_id == user_id, Notification.is_read == False)
            .update({"is_read": True})
        )
        db.commit()
        return count

    @staticmethod
    def create_system_notification(db: Session, user_id: int, message: str) -> Notification:
        notif = Notification(
            user_id=user_id,
            message=message,
            is_read=False,
            created_at=datetime.utcnow()
        )
        db.add(notif)
        db.commit()
        db.refresh(notif)
        return notif
