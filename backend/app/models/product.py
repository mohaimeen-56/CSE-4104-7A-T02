from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime, Numeric, Boolean
from sqlalchemy.orm import relationship
from app.db.session import Base


class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String(100), nullable=False)
    category = Column(String(50), nullable=True)
    subcategory = Column(String(50), nullable=True)
    brand = Column(String(100), nullable=True)
    sku = Column(String(50), nullable=True, unique=True)
    description = Column(Text, nullable=True)
    price = Column(Numeric(10, 2), nullable=True)  # current list price, distinct from per-sale unit_price
    cost = Column(Numeric(10, 2), nullable=True)
    stock = Column(Integer, default=0)
    # Qualitative production/supply level ('low'/'medium'/'high'). Manually set; when null,
    # reports derive a default bucket from `stock` instead of fabricating a value.
    production_level = Column(String(20), nullable=True)
    is_active = Column(Boolean, nullable=False, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    sales = relationship("Sale", back_populates="product")

    @property
    def effective_production_level(self) -> str:
        """The manually-set production_level if present, otherwise a stock-derived default
        (low < 20, medium < 60, high >= 60) so reports never fabricate a level from nothing."""
        if self.production_level:
            return self.production_level
        stock = self.stock or 0
        if stock < 20:
            return "low"
        if stock < 60:
            return "medium"
        return "high"
