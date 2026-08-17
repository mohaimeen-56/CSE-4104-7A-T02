from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Index
from sqlalchemy.orm import relationship
from app.db.session import Base


class AILog(Base):
    __tablename__ = "ai_logs"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    conversation_id = Column(String(36), nullable=True, index=True)
    query = Column(Text, nullable=True)
    response = Column(Text, nullable=True)
    route = Column(String(20), nullable=True)  # 'conversation' | 'analytics'
    intent = Column(String(50), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="ai_logs")


Index("idx_ai_logs_user_id", AILog.user_id)
Index("idx_ai_logs_conversation_id", AILog.conversation_id)
