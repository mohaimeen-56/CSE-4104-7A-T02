import uuid
from datetime import datetime
from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from app.db.session import Base


class AdminInviteCode(Base):
    __tablename__ = "admin_invite_codes"

    id = Column(Integer, primary_key=True, index=True)
    code = Column(String(64), unique=True, nullable=False, index=True, default=lambda: uuid.uuid4().hex)
    created_by_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    used = Column(Boolean, default=False, nullable=False)
    used_by_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    expires_at = Column(DateTime, nullable=False)

    created_by = relationship("User", foreign_keys=[created_by_id])
    used_by = relationship("User", foreign_keys=[used_by_id])
