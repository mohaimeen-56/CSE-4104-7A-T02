from datetime import datetime
from typing import List
from sqlalchemy.orm import Session
from app.models.system_setting import MaintenanceLog
from app.models.user import User
from app.services.system_setting_service import SystemSettingService
from app.schemas.maintenance import MaintenanceStatus, MaintenanceLogItem

DEFAULT_MESSAGE = "SalesIQ is currently under maintenance. Please check back shortly."

KEY_ENABLED = "maintenance_mode"
KEY_MESSAGE = "maintenance_message"
KEY_REASON = "maintenance_reason"
KEY_ENABLED_BY = "maintenance_enabled_by_name"
KEY_STARTED_AT = "maintenance_started_at"


class MaintenanceService:
    @staticmethod
    def get_status(db: Session) -> MaintenanceStatus:
        enabled = SystemSettingService.get_bool(db, KEY_ENABLED, default=False)
        message = SystemSettingService.get_str(db, KEY_MESSAGE, DEFAULT_MESSAGE)
        if not enabled:
            return MaintenanceStatus(enabled=False, message=message)

        started_raw = SystemSettingService.get_str(db, KEY_STARTED_AT)
        return MaintenanceStatus(
            enabled=True,
            message=message,
            enabled_by_name=SystemSettingService.get_str(db, KEY_ENABLED_BY),
            started_at=datetime.fromisoformat(started_raw) if started_raw else None,
            reason=SystemSettingService.get_str(db, KEY_REASON),
        )

    @staticmethod
    def enable(db: Session, admin: User, reason: str, message: str = None) -> MaintenanceStatus:
        now = datetime.utcnow()
        SystemSettingService.set(db, KEY_ENABLED, "true", updated_by=admin.id)
        SystemSettingService.set(db, KEY_MESSAGE, message or DEFAULT_MESSAGE, updated_by=admin.id)
        SystemSettingService.set(db, KEY_REASON, reason, updated_by=admin.id)
        SystemSettingService.set(db, KEY_ENABLED_BY, admin.name, updated_by=admin.id)
        SystemSettingService.set(db, KEY_STARTED_AT, now.isoformat(), updated_by=admin.id)

        db.add(MaintenanceLog(action="enabled", performed_by=admin.id, reason=reason, created_at=now))
        db.commit()
        return MaintenanceService.get_status(db)

    @staticmethod
    def disable(db: Session, admin: User, reason: str = None) -> MaintenanceStatus:
        now = datetime.utcnow()
        SystemSettingService.set(db, KEY_ENABLED, "false", updated_by=admin.id)

        db.add(MaintenanceLog(action="disabled", performed_by=admin.id, reason=reason, created_at=now))
        db.commit()
        return MaintenanceService.get_status(db)

    @staticmethod
    def get_audit_log(db: Session, limit: int = 50) -> List[MaintenanceLogItem]:
        rows = (
            db.query(MaintenanceLog)
            .order_by(MaintenanceLog.created_at.desc())
            .limit(limit)
            .all()
        )
        return [
            MaintenanceLogItem(
                id=r.id, action=r.action,
                performed_by_name=r.performer.name if r.performer else None,
                reason=r.reason, created_at=r.created_at,
            )
            for r in rows
        ]
