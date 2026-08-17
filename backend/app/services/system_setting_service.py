from typing import Optional
from sqlalchemy.orm import Session
from app.models.system_setting import SystemSetting


class SystemSettingService:
    """Thin key/value accessor over the system_settings table, backing global,
    server-side application state (e.g. maintenance mode) that must survive restarts
    and be shared across every client -- unlike React component state."""

    @staticmethod
    def get_str(db: Session, key: str, default: Optional[str] = None) -> Optional[str]:
        row = db.query(SystemSetting).filter(SystemSetting.key == key).first()
        return row.value if row else default

    @staticmethod
    def get_bool(db: Session, key: str, default: bool = False) -> bool:
        raw = SystemSettingService.get_str(db, key, None)
        if raw is None:
            return default
        return raw.strip().lower() == "true"

    @staticmethod
    def set(db: Session, key: str, value: str, updated_by: Optional[int] = None) -> SystemSetting:
        row = db.query(SystemSetting).filter(SystemSetting.key == key).first()
        if row:
            row.value = value
            row.updated_by = updated_by
        else:
            row = SystemSetting(key=key, value=value, updated_by=updated_by)
            db.add(row)
        db.commit()
        db.refresh(row)
        return row
