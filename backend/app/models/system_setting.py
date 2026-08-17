from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from app.db.session import Base


class SystemSetting(Base):
    """Persistent server-side key/value store for global application state
    (e.g. maintenance mode) so it survives restarts and is shared across all clients,
    unlike React component state."""

    __tablename__ = "system_settings"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    key = Column(String(100), unique=True, nullable=False, index=True)
    value = Column(Text, nullable=False)
    updated_by = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    updater = relationship("User")


class MaintenanceLog(Base):
    """Audit trail of maintenance-mode enable/disable events for administrative accountability."""

    __tablename__ = "maintenance_logs"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    action = Column(String(20), nullable=False)  # 'enabled' | 'disabled'
    performed_by = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    reason = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, index=True)

    performer = relationship("User")
