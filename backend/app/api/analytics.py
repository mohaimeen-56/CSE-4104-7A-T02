from datetime import date
from decimal import Decimal
from typing import Optional, List
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.schemas.analytics import (
    SummaryKPI,
    RevenueTrendItem,
    ProductSalesItem,
    CategorySalesItem,
    RegionSalesItem,
    TopProductItem,
    MonthlyComparisonItem,
    DashboardOverviewResponse,
    HourlySalesItem,
    DayOfWeekSalesItem,
    TimeOfDayBucketItem,
    PeakHourItem,
    DataQualityReport,
    DecisionSignalsResponse,
    ExecutiveSummaryResponse,
    DataExplorerResult,
)
from app.services.decision_signals_service import generate_decision_signals, generate_executive_summary
from app.schemas.common import APIResponse
from app.services.analytics_service import AnalyticsService
from app.services.data_quality_service import DataQualityService
from app.core.timeutil import resolve_date_range_preset
from app.core.deps import get_current_user
from app.models.user import User

router = APIRouter(prefix="/analytics", tags=["Analytics"])


def _resolve_dates(
    preset: Optional[str],
    start_date: Optional[date],
    end_date: Optional[date],
) -> tuple[Optional[date], Optional[date]]:
    """Named preset takes priority unless it's 'custom'; explicit start/end always override."""
    if preset and preset != "custom":
        p_start, p_end = resolve_date_range_preset(preset)
        if p_start:
            return p_start, p_end
    return start_date, end_date


# Shared filter dependency parameters, repeated across endpoints for cross-filtering support.
def common_filters(
    preset: Optional[str] = Query(None, description="today|yesterday|this_week|last_7_days|this_month|last_month|custom"),
    start_date: Optional[date] = Query(None),
    end_date: Optional[date] = Query(None),
    region_id: Optional[int] = Query(None),
    category: Optional[str] = Query(None),
    product_id: Optional[int] = Query(None),
    min_price: Optional[Decimal] = Query(None),
    max_price: Optional[Decimal] = Query(None),
):
    resolved_start, resolved_end = _resolve_dates(preset, start_date, end_date)
    return {
        "start_date": resolved_start,
        "end_date": resolved_end,
        "region_id": region_id,
        "category": category,
        "product_id": product_id,
        "min_price": min_price,
        "max_price": max_price,
    }


@router.get("/overview", response_model=APIResponse[DashboardOverviewResponse])
def get_dashboard_overview(
    filters: dict = Depends(common_filters),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    overview = AnalyticsService.get_dashboard_overview(db, **filters)
    return APIResponse(success=True, message="Dashboard analytics overview retrieved", data=overview)


@router.get("/summary", response_model=APIResponse[SummaryKPI])
def get_summary_kpis(
    filters: dict = Depends(common_filters),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    kpis = AnalyticsService.get_summary_kpis(db, **filters)
    return APIResponse(success=True, message="Summary KPIs calculated", data=kpis)


@router.get("/revenue-trend", response_model=APIResponse[List[RevenueTrendItem]])
def get_revenue_trend(
    interval: str = Query("month", description="hour|day|week|month|quarter|year"),
    filters: dict = Depends(common_filters),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    start_date = filters.pop("start_date")
    end_date = filters.pop("end_date")
    trend = AnalyticsService.get_revenue_trend(db, start_date=start_date, end_date=end_date, interval=interval, **filters)
    return APIResponse(success=True, message="Revenue trend retrieved", data=trend)


@router.get("/by-product", response_model=APIResponse[List[ProductSalesItem]])
def get_sales_by_product(
    limit: int = Query(10, ge=1, le=50),
    filters: dict = Depends(common_filters),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    prods = AnalyticsService.get_sales_by_product(db, limit=limit, **filters)
    return APIResponse(success=True, message="Sales by product retrieved", data=prods)


@router.get("/by-category", response_model=APIResponse[List[CategorySalesItem]])
def get_sales_by_category(
    filters: dict = Depends(common_filters),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    cats = AnalyticsService.get_sales_by_category(db, **filters)
    return APIResponse(success=True, message="Sales by category retrieved", data=cats)


@router.get("/by-region", response_model=APIResponse[List[RegionSalesItem]])
def get_sales_by_region(
    filters: dict = Depends(common_filters),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    regs = AnalyticsService.get_sales_by_region(db, **filters)
    return APIResponse(success=True, message="Sales by region retrieved", data=regs)


@router.get("/top-products", response_model=APIResponse[List[TopProductItem]])
def get_top_products(
    limit: int = Query(5, ge=1, le=20),
    filters: dict = Depends(common_filters),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    top_p = AnalyticsService.get_top_products(db, limit=limit, **filters)
    return APIResponse(success=True, message="Top performing products retrieved", data=top_p)


@router.get("/monthly-comparison", response_model=APIResponse[List[MonthlyComparisonItem]])
def get_monthly_comparison(
    months_count: int = Query(6, ge=2, le=24),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    comp = AnalyticsService.get_monthly_comparison(db, months_count=months_count)
    return APIResponse(success=True, message="Monthly comparison retrieved", data=comp)


@router.get("/hourly", response_model=APIResponse[List[HourlySalesItem]])
def get_hourly_sales(
    filters: dict = Depends(common_filters),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    data = AnalyticsService.get_hourly_sales(db, **filters)
    return APIResponse(success=True, message="Hourly sales distribution retrieved", data=data)


@router.get("/peak-hours", response_model=APIResponse[List[PeakHourItem]])
def get_peak_hours(
    limit: int = Query(5, ge=1, le=24),
    filters: dict = Depends(common_filters),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    data = AnalyticsService.get_peak_hours(db, limit=limit, **filters)
    return APIResponse(success=True, message="Peak sales hours retrieved", data=data)


@router.get("/by-day-of-week", response_model=APIResponse[List[DayOfWeekSalesItem]])
def get_sales_by_day_of_week(
    filters: dict = Depends(common_filters),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    data = AnalyticsService.get_sales_by_day_of_week(db, **filters)
    return APIResponse(success=True, message="Sales by day of week retrieved", data=data)


@router.get("/time-of-day", response_model=APIResponse[List[TimeOfDayBucketItem]])
def get_time_of_day_comparison(
    filters: dict = Depends(common_filters),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    data = AnalyticsService.get_time_of_day_comparison(db, **filters)
    return APIResponse(success=True, message="Morning/afternoon/evening/night comparison retrieved", data=data)


@router.get("/data-quality", response_model=APIResponse[DataQualityReport])
def get_data_quality_report(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    report = DataQualityService.get_report(db)
    return APIResponse(success=True, message="Data quality report generated", data=report)


@router.get("/decision-signals", response_model=APIResponse[DecisionSignalsResponse])
def get_decision_signals(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Returns structured business intelligence signals: opportunities, risks, anomalies, trends.
    All computed deterministically from real sales data — no hallucination."""
    signals = generate_decision_signals(db)
    return APIResponse(success=True, message="Decision signals generated", data=signals)


@router.get("/executive-summary")
def get_executive_summary(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Returns a short executive summary computed from real analytics data."""
    summary = generate_executive_summary(db)
    return APIResponse(success=True, message="Executive summary generated", data=summary)


@router.get("/data-explorer")
def data_explorer(
    dimension: str = Query("product", description="product|category|region|day|month|week"),
    metric: str = Query("revenue", description="revenue|orders|quantity|aov"),
    limit: int = Query(20, ge=1, le=100),
    filters: dict = Depends(common_filters),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Flexible dimension × metric query for the Data Explorer page."""
    from decimal import Decimal as D

    start_date = filters.get("start_date")
    end_date = filters.get("end_date")
    region_id = filters.get("region_id")
    category = filters.get("category")
    product_id = filters.get("product_id")

    if dimension in ("product",):
        rows_raw = AnalyticsService.get_sales_by_product(
            db, start_date=start_date, end_date=end_date,
            region_id=region_id, category=category, product_id=product_id, limit=limit
        )
        total_rev = sum(r.revenue for r in rows_raw)
        total_ord = sum(r.units_sold for r in rows_raw)
        rows = [
            {
                "label": r.product_name,
                "category": r.category,
                "revenue": round(r.revenue, 2),
                "orders": r.units_sold,
                "aov": round(r.revenue / r.units_sold, 2) if r.units_sold else 0,
                "contribution_pct": round(r.revenue / total_rev * 100, 1) if total_rev else 0,
            }
            for r in rows_raw
        ]
    elif dimension == "category":
        rows_raw = AnalyticsService.get_sales_by_category(
            db, start_date=start_date, end_date=end_date,
            region_id=region_id, category=category, product_id=product_id
        )
        total_rev = sum(r.revenue for r in rows_raw)
        total_ord = sum(r.units_sold for r in rows_raw)
        rows = [
            {
                "label": r.category,
                "revenue": round(r.revenue, 2),
                "orders": r.units_sold,
                "aov": round(r.revenue / r.units_sold, 2) if r.units_sold else 0,
                "contribution_pct": round(r.percentage, 1),
            }
            for r in rows_raw
        ]
    elif dimension == "region":
        rows_raw = AnalyticsService.get_sales_by_region(
            db, start_date=start_date, end_date=end_date,
            region_id=region_id, category=category, product_id=product_id
        )
        total_rev = sum(r.revenue for r in rows_raw)
        total_ord = sum(r.units_sold for r in rows_raw)
        rows = [
            {
                "label": r.region_name,
                "revenue": round(r.revenue, 2),
                "orders": r.units_sold,
                "aov": round(r.revenue / r.units_sold, 2) if r.units_sold else 0,
                "contribution_pct": round(r.percentage, 1),
            }
            for r in rows_raw
        ]
    elif dimension in ("month", "week", "day"):
        trend_raw = AnalyticsService.get_revenue_trend(
            db, start_date=start_date, end_date=end_date, interval=dimension,
            region_id=region_id, category=category, product_id=product_id
        )
        total_rev = sum(r.revenue for r in trend_raw)
        total_ord = sum(r.orders for r in trend_raw)
        rows = [
            {
                "label": r.date,
                "revenue": round(r.revenue, 2),
                "orders": r.orders,
                "aov": round(r.revenue / r.orders, 2) if r.orders else 0,
                "contribution_pct": round(r.revenue / total_rev * 100, 1) if total_rev else 0,
            }
            for r in trend_raw
        ]
    else:
        rows = []
        total_rev = 0.0
        total_ord = 0

    period_parts = []
    if start_date:
        period_parts.append(f"from {start_date}")
    if end_date:
        period_parts.append(f"to {end_date}")
    period_label = " ".join(period_parts) if period_parts else "All time"

    return APIResponse(
        success=True,
        message="Data explorer query executed",
        data={
            "rows": rows,
            "total_revenue": round(float(total_rev), 2),
            "total_orders": int(total_ord),
            "dimension": dimension,
            "metric": metric,
            "period_label": period_label,
        }
    )
