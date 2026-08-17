from typing import List, Optional, Dict, Any
from datetime import date, datetime, timedelta
from decimal import Decimal
from sqlalchemy.orm import Session, Query
from sqlalchemy import func, extract, desc, asc
from app.models.sale import Sale
from app.models.product import Product
from app.models.region import Region
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
)
from app.core.timeutil import APP_TIMEZONE

DAY_NAMES = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]


def _time_of_day_bucket(hour: int) -> str:
    if 6 <= hour < 12:
        return "morning"
    if 12 <= hour < 17:
        return "afternoon"
    if 17 <= hour < 21:
        return "evening"
    return "night"


class AnalyticsService:
    @staticmethod
    def build_filtered_query(
        db: Session,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
        region_id: Optional[int] = None,
        category: Optional[str] = None,
        product_id: Optional[int] = None,
        min_price: Optional[Decimal] = None,
        max_price: Optional[Decimal] = None,
    ) -> Query:
        """Shared filter builder for every analytics/report aggregation. Always joins
        Product + Region so callers can filter/group on either without an extra join."""
        query = (
            db.query(Sale)
            .join(Product, Sale.product_id == Product.id)
            .join(Region, Sale.region_id == Region.id)
        )
        if start_date:
            query = query.filter(Sale.sale_date >= start_date)
        if end_date:
            query = query.filter(Sale.sale_date <= end_date)
        if region_id:
            query = query.filter(Sale.region_id == region_id)
        if category:
            query = query.filter(Product.category == category)
        if product_id:
            query = query.filter(Sale.product_id == product_id)
        if min_price is not None:
            query = query.filter(Sale.unit_price >= min_price)
        if max_price is not None:
            query = query.filter(Sale.unit_price <= max_price)
        return query

    @staticmethod
    def get_summary_kpis(
        db: Session,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
        region_id: Optional[int] = None,
        category: Optional[str] = None,
        product_id: Optional[int] = None,
        min_price: Optional[Decimal] = None,
        max_price: Optional[Decimal] = None,
    ) -> SummaryKPI:
        filters = dict(region_id=region_id, category=category, product_id=product_id,
                        min_price=min_price, max_price=max_price)

        query = AnalyticsService.build_filtered_query(db, start_date, end_date, **filters).with_entities(
            func.coalesce(func.sum(Sale.total_price), 0),
            func.count(Sale.id),
        )
        curr_rev, curr_orders = query.first() or (0, 0)
        curr_rev = float(curr_rev)
        curr_orders = int(curr_orders)
        curr_aov = round(curr_rev / curr_orders, 2) if curr_orders > 0 else 0.0

        # Calculate previous period for comparison
        prev_rev = 0.0
        prev_orders = 0
        prev_aov = 0.0

        if start_date and end_date:
            duration = (end_date - start_date).days + 1
            prev_end = start_date - timedelta(days=1)
            prev_start = prev_end - timedelta(days=duration - 1)

            prev_q = AnalyticsService.build_filtered_query(db, prev_start, prev_end, **filters).with_entities(
                func.coalesce(func.sum(Sale.total_price), 0),
                func.count(Sale.id),
            )
            p_rev, p_ord = prev_q.first() or (0, 0)
            prev_rev = float(p_rev)
            prev_orders = int(p_ord)
            prev_aov = round(prev_rev / prev_orders, 2) if prev_orders > 0 else 0.0
        else:
            # Default comparison against previous month based on latest sale date
            latest_sale = db.query(func.max(Sale.sale_date)).scalar()
            if latest_sale:
                curr_m, curr_y = latest_sale.month, latest_sale.year
                if curr_m == 1:
                    prev_m, prev_y = 12, curr_y - 1
                else:
                    prev_m, prev_y = curr_m - 1, curr_y

                prev_month_start = date(prev_y, prev_m, 1)
                prev_month_end = date(curr_y, curr_m, 1) - timedelta(days=1) if curr_m != 1 else date(prev_y, 12, 31)
                p_rev_q = AnalyticsService.build_filtered_query(
                    db, prev_month_start, prev_month_end, **filters
                ).with_entities(
                    func.coalesce(func.sum(Sale.total_price), 0),
                    func.count(Sale.id),
                ).first()
                if p_rev_q:
                    prev_rev = float(p_rev_q[0])
                    prev_orders = int(p_rev_q[1])
                    prev_aov = round(prev_rev / prev_orders, 2) if prev_orders > 0 else 0.0

        def calc_pct(current: float, previous: float) -> float:
            if previous <= 0:
                return 100.0 if current > 0 else 0.0
            return round(((current - previous) / previous) * 100.0, 1)

        return SummaryKPI(
            total_revenue=round(curr_rev, 2),
            total_orders=curr_orders,
            average_order_value=curr_aov,
            revenue_growth_pct=calc_pct(curr_rev, prev_rev),
            orders_growth_pct=calc_pct(curr_orders, prev_orders),
            aov_growth_pct=calc_pct(curr_aov, prev_aov),
        )

    @staticmethod
    def get_revenue_trend(
        db: Session,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
        interval: str = "month",  # "hour" | "day" | "week" | "month" | "quarter" | "year"
        **filters: Any,
    ) -> List[RevenueTrendItem]:
        all_sales = AnalyticsService.build_filtered_query(db, start_date, end_date, **filters).order_by(
            Sale.sale_date.asc()
        ).all()

        # Group in python for cross-engine date aggregation stability and local-tz hour grouping
        trend_dict: Dict[str, Dict[str, Any]] = {}
        for s in all_sales:
            if interval == "hour":
                local_dt = s.sale_datetime.astimezone(APP_TIMEZONE)
                key = local_dt.strftime("%Y-%m-%d %H:00")
            elif interval == "day":
                key = s.sale_date.strftime("%Y-%m-%d")
            elif interval == "week":
                iso_year, iso_week, _ = s.sale_date.isocalendar()
                key = f"{iso_year}-W{iso_week:02d}"
            elif interval == "quarter":
                q = (s.sale_date.month - 1) // 3 + 1
                key = f"{s.sale_date.year}-Q{q}"
            elif interval == "year":
                key = str(s.sale_date.year)
            else:
                key = s.sale_date.strftime("%Y-%m")

            if key not in trend_dict:
                trend_dict[key] = {"revenue": 0.0, "orders": 0}
            trend_dict[key]["revenue"] += float(s.total_price)
            trend_dict[key]["orders"] += 1

        return [
            RevenueTrendItem(date=k, revenue=round(v["revenue"], 2), orders=v["orders"])
            for k, v in sorted(trend_dict.items())
        ]

    @staticmethod
    def get_sales_by_product(
        db: Session,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
        limit: int = 10,
        **filters: Any,
    ) -> List[ProductSalesItem]:
        results = (
            AnalyticsService.build_filtered_query(db, start_date, end_date, **filters)
            .with_entities(
                Product.id,
                Product.name,
                Product.category,
                func.coalesce(func.sum(Sale.quantity), 0).label("units_sold"),
                func.coalesce(func.sum(Sale.total_price), 0).label("revenue"),
            )
            .group_by(Product.id, Product.name, Product.category)
            .order_by(desc("revenue"))
            .limit(limit)
            .all()
        )
        return [
            ProductSalesItem(
                product_id=r[0], product_name=r[1], category=r[2] or "Uncategorized",
                units_sold=int(r[3]), revenue=round(float(r[4]), 2),
            )
            for r in results
        ]

    @staticmethod
    def get_sales_by_category(
        db: Session,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
        **filters: Any,
    ) -> List[CategorySalesItem]:
        rows = (
            AnalyticsService.build_filtered_query(db, start_date, end_date, **filters)
            .with_entities(
                func.coalesce(Product.category, "Other").label("cat"),
                func.coalesce(func.sum(Sale.quantity), 0).label("units"),
                func.coalesce(func.sum(Sale.total_price), 0).label("revenue"),
            )
            .group_by("cat")
            .order_by(desc("revenue"))
            .all()
        )
        total_rev = sum(float(r[2]) for r in rows)
        return [
            CategorySalesItem(
                category=r[0], units_sold=int(r[1]), revenue=round(float(r[2]), 2),
                percentage=round((float(r[2]) / total_rev * 100), 1) if total_rev > 0 else 0.0
            )
            for r in rows
        ]

    @staticmethod
    def get_sales_by_region(
        db: Session,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
        **filters: Any,
    ) -> List[RegionSalesItem]:
        rows = (
            AnalyticsService.build_filtered_query(db, start_date, end_date, **filters)
            .with_entities(
                Region.id,
                Region.name,
                func.coalesce(func.sum(Sale.quantity), 0).label("units"),
                func.coalesce(func.sum(Sale.total_price), 0).label("revenue"),
            )
            .group_by(Region.id, Region.name)
            .order_by(desc("revenue"))
            .all()
        )
        total_rev = sum(float(r[3]) for r in rows)
        return [
            RegionSalesItem(
                region_id=r[0], region_name=r[1], units_sold=int(r[2]), revenue=round(float(r[3]), 2),
                percentage=round((float(r[3]) / total_rev * 100), 1) if total_rev > 0 else 0.0
            )
            for r in rows
        ]

    @staticmethod
    def get_top_products(
        db: Session,
        limit: int = 5,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
        **filters: Any,
    ) -> List[TopProductItem]:
        prods = AnalyticsService.get_sales_by_product(db, start_date=start_date, end_date=end_date, limit=limit, **filters)
        return [
            TopProductItem(
                rank=idx + 1, product_id=p.product_id, product_name=p.product_name,
                category=p.category, units_sold=p.units_sold, revenue=p.revenue,
            )
            for idx, p in enumerate(prods)
        ]

    @staticmethod
    def get_monthly_comparison(db: Session, months_count: int = 6, **filters: Any) -> List[MonthlyComparisonItem]:
        trend = AnalyticsService.get_revenue_trend(db, interval="month", **filters)
        recent = trend[-months_count:] if len(trend) > months_count else trend
        return [
            MonthlyComparisonItem(
                month=t.date, revenue=t.revenue, orders=t.orders,
                avg_order_value=round(t.revenue / t.orders, 2) if t.orders > 0 else 0.0
            )
            for t in recent
        ]

    @staticmethod
    def get_hourly_sales(
        db: Session,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
        **filters: Any,
    ) -> List[HourlySalesItem]:
        sales = AnalyticsService.build_filtered_query(db, start_date, end_date, **filters).all()
        buckets: Dict[int, Dict[str, Any]] = {h: {"revenue": 0.0, "orders": 0} for h in range(24)}
        for s in sales:
            hour = s.sale_datetime.astimezone(APP_TIMEZONE).hour
            buckets[hour]["revenue"] += float(s.total_price)
            buckets[hour]["orders"] += 1
        return [
            HourlySalesItem(hour=h, revenue=round(v["revenue"], 2), orders=v["orders"])
            for h, v in sorted(buckets.items())
        ]

    @staticmethod
    def get_peak_hours(
        db: Session,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
        limit: int = 5,
        **filters: Any,
    ) -> List[PeakHourItem]:
        hourly = AnalyticsService.get_hourly_sales(db, start_date, end_date, **filters)
        top = sorted(hourly, key=lambda h: h.revenue, reverse=True)[:limit]
        return [PeakHourItem(hour=h.hour, revenue=h.revenue, orders=h.orders) for h in top]

    @staticmethod
    def get_sales_by_day_of_week(
        db: Session,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
        **filters: Any,
    ) -> List[DayOfWeekSalesItem]:
        sales = AnalyticsService.build_filtered_query(db, start_date, end_date, **filters).all()
        buckets: Dict[int, Dict[str, Any]] = {d: {"revenue": 0.0, "orders": 0} for d in range(7)}
        for s in sales:
            dow = s.sale_date.weekday()  # 0=Monday
            buckets[dow]["revenue"] += float(s.total_price)
            buckets[dow]["orders"] += 1
        return [
            DayOfWeekSalesItem(day_of_week=d, day_name=DAY_NAMES[d], revenue=round(v["revenue"], 2), orders=v["orders"])
            for d, v in sorted(buckets.items())
        ]

    @staticmethod
    def get_time_of_day_comparison(
        db: Session,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
        **filters: Any,
    ) -> List[TimeOfDayBucketItem]:
        sales = AnalyticsService.build_filtered_query(db, start_date, end_date, **filters).all()
        buckets: Dict[str, Dict[str, Any]] = {b: {"revenue": 0.0, "orders": 0} for b in ("morning", "afternoon", "evening", "night")}
        for s in sales:
            hour = s.sale_datetime.astimezone(APP_TIMEZONE).hour
            b = _time_of_day_bucket(hour)
            buckets[b]["revenue"] += float(s.total_price)
            buckets[b]["orders"] += 1
        total_rev = sum(v["revenue"] for v in buckets.values())
        return [
            TimeOfDayBucketItem(
                bucket=b, revenue=round(v["revenue"], 2), orders=v["orders"],
                percentage=round((v["revenue"] / total_rev * 100), 1) if total_rev > 0 else 0.0
            )
            for b, v in buckets.items()
        ]

    @staticmethod
    def get_dashboard_overview(
        db: Session,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
        **filters: Any,
    ) -> DashboardOverviewResponse:
        kpis = AnalyticsService.get_summary_kpis(db, start_date, end_date, **filters)
        trend = AnalyticsService.get_revenue_trend(db, start_date, end_date, interval="month", **filters)
        by_prod = AnalyticsService.get_sales_by_product(db, start_date, end_date, limit=6, **filters)
        by_cat = AnalyticsService.get_sales_by_category(db, start_date, end_date, **filters)
        by_reg = AnalyticsService.get_sales_by_region(db, start_date, end_date, **filters)
        top_prods = AnalyticsService.get_top_products(db, limit=5, start_date=start_date, end_date=end_date, **filters)

        return DashboardOverviewResponse(
            kpis=kpis,
            revenue_trend=trend,
            sales_by_product=by_prod,
            sales_by_category=by_cat,
            sales_by_region=by_reg,
            top_products=top_prods,
        )
