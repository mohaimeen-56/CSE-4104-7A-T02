from typing import List, Optional, Dict
from pydantic import BaseModel


class ReportFilterSummary(BaseModel):
    date_label: str
    category_label: str
    region_label: str
    product_label: str
    price_label: str
    quantity_label: str
    grouping_label: str
    generated_at: str


class ReportRow(BaseModel):
    group_key: str
    units: int
    revenue: float
    orders: int
    avg_price: float


class PriceRangeRow(BaseModel):
    range_label: str
    units: int
    revenue: float


class ReportTotals(BaseModel):
    units: int
    revenue: float
    orders: int
    avg_order_value: float


class ReportDefinitions(BaseModel):
    quantity_levels: Dict[str, str]
    price_buckets: List[float]


class ReportBuilderResponse(BaseModel):
    rows: List[ReportRow]
    price_range_rows: List[PriceRangeRow]
    totals: ReportTotals
    filter_summary: ReportFilterSummary
    definitions: ReportDefinitions
