from typing import List, Optional
from pydantic import BaseModel


class SummaryKPI(BaseModel):
    total_revenue: float
    total_orders: int
    average_order_value: float
    revenue_growth_pct: float
    orders_growth_pct: float
    aov_growth_pct: float


class RevenueTrendItem(BaseModel):
    date: str  # Month or Date string (e.g. '2026-06' or '2026-06-01')
    revenue: float
    orders: int


class ProductSalesItem(BaseModel):
    product_id: int
    product_name: str
    category: str
    units_sold: int
    revenue: float


class CategorySalesItem(BaseModel):
    category: str
    units_sold: int
    revenue: float
    percentage: float


class RegionSalesItem(BaseModel):
    region_id: int
    region_name: str
    units_sold: int
    revenue: float
    percentage: float


class TopProductItem(BaseModel):
    rank: int
    product_id: int
    product_name: str
    category: str
    units_sold: int
    revenue: float


class MonthlyComparisonItem(BaseModel):
    month: str
    revenue: float
    orders: int
    avg_order_value: float


class DashboardOverviewResponse(BaseModel):
    kpis: SummaryKPI
    revenue_trend: List[RevenueTrendItem]
    sales_by_product: List[ProductSalesItem]
    sales_by_category: List[CategorySalesItem]
    sales_by_region: List[RegionSalesItem]
    top_products: List[TopProductItem]


class HourlySalesItem(BaseModel):
    hour: int  # 0-23, local (Asia/Dhaka) hour
    revenue: float
    orders: int


class DayOfWeekSalesItem(BaseModel):
    day_of_week: int  # 0=Monday .. 6=Sunday (ISO-ish, Python weekday())
    day_name: str
    revenue: float
    orders: int


class TimeOfDayBucketItem(BaseModel):
    bucket: str  # 'morning' (06-12) | 'afternoon' (12-17) | 'evening' (17-21) | 'night' (21-06)
    revenue: float
    orders: int
    percentage: float


class PeakHourItem(BaseModel):
    hour: int
    revenue: float
    orders: int


class DataQualityReport(BaseModel):
    total_records: int
    captured_timestamps: int
    estimated_timestamps: int
    timestamp_coverage_pct: float
    null_or_invalid_count: int
    future_dated_count: int
    duplicate_exact_timestamp_count: int
    last_import_at: Optional[str] = None
    anomaly_count: int


class DecisionSignal(BaseModel):
    signal_type: str  # opportunity | risk | anomaly | trend | action
    title: str
    description: str
    severity: str  # high | medium | low
    link_path: Optional[str] = None  # frontend route to navigate to
    metric_value: Optional[float] = None
    metric_label: Optional[str] = None
    confidence: str = "medium"  # high | medium | low


class DecisionSignalsResponse(BaseModel):
    signals: List[DecisionSignal]
    opportunities_count: int
    risks_count: int
    anomalies_count: int
    trends_count: int
    generated_at: str


class SparklinePoint(BaseModel):
    date: str
    value: float


class ExecutiveSummaryResponse(BaseModel):
    headline: str
    body: str
    key_opportunity: Optional[str] = None
    key_risk: Optional[str] = None
    confidence_pct: int
    top_performer: Optional[str] = None
    top_performer_type: Optional[str] = None


class DataExplorerResult(BaseModel):
    rows: List[dict]
    total_revenue: float
    total_orders: int
    dimension: str
    metric: str
    period_label: str
