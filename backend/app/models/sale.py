from datetime import datetime
from sqlalchemy import Column, Integer, Numeric, Date, DateTime, Boolean, ForeignKey, Index
from sqlalchemy.orm import relationship
from app.db.session import Base


class Sale(Base):
    __tablename__ = "sales"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True)
    product_id = Column(Integer, ForeignKey("products.id", ondelete="RESTRICT"), nullable=False, index=True)
    region_id = Column(Integer, ForeignKey("regions.id", ondelete="RESTRICT"), nullable=False, index=True)
    quantity = Column(Integer, nullable=False)
    unit_price = Column(Numeric(10, 2), nullable=False)
    total_price = Column(Numeric(12, 2), nullable=False)
    sale_date = Column(Date, nullable=False, index=True)
    # Full date+time of the sale, timezone-aware (stored UTC, app timezone is Asia/Dhaka).
    # Nullable=False but backfilled via migration for pre-existing rows.
    sale_datetime = Column(DateTime(timezone=True), nullable=False, index=True)
    # True when sale_datetime was backfilled/estimated rather than captured at time of entry
    # (e.g. legacy date-only records, or a row whose time was otherwise missing/invalid).
    is_estimated_time = Column(Boolean, nullable=False, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    user = relationship("User", back_populates="sales")
    product = relationship("Product", back_populates="sales")
    region = relationship("Region", back_populates="sales")


# Indexes matching schemas.sql
Index("idx_sales_user_id", Sale.user_id)
Index("idx_sales_product_id", Sale.product_id)
Index("idx_sales_region_id", Sale.region_id)
Index("idx_sales_sale_date", Sale.sale_date)
Index("idx_sales_sale_datetime", Sale.sale_datetime)
