from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.orm import relationship
from app.db.session import Base


class Region(Base):
    __tablename__ = "regions"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String(100), nullable=False)
    country = Column(String(100), default="Bangladesh")
    created_at = Column(DateTime, default=datetime.utcnow)

    sales = relationship("Sale", back_populates="region")
