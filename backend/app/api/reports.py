from datetime import date
from decimal import Decimal
from typing import Optional, List
from fastapi import APIRouter, Depends, Query, Response
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.services.report_service import ReportService
from app.services.analytics_service import AnalyticsService
from app.services.report_builder_service import ReportBuilderService
from app.ai.grounded_engine import GroundedAIEngine
from app.schemas.common import APIResponse
from app.schemas.report import ReportBuilderResponse
from app.core.timeutil import resolve_date_range_preset, APP_TIMEZONE
from app.core.deps import get_current_user
from app.models.user import User
from app.models.product import Product
from app.models.region import Region
from datetime import datetime

router = APIRouter(prefix="/reports", tags=["Reports"])


def _builder_filters(
    preset: Optional[str] = Query(None),
    start_date: Optional[date] = Query(None),
    end_date: Optional[date] = Query(None),
    region_id: Optional[int] = Query(None),
    category: Optional[str] = Query(None),
    product_id: Optional[int] = Query(None),
    min_price: Optional[Decimal] = Query(None),
    max_price: Optional[Decimal] = Query(None),
    quantity_level: Optional[str] = Query(None, description="low|medium|high|custom|all"),
    min_quantity: Optional[int] = Query(None),
    max_quantity: Optional[int] = Query(None),
    group_by: str = Query("month", description="hour|day|week|month|quarter|year|category|subcategory|brand|product|region"),
    price_buckets: Optional[str] = Query(None, description="Comma-separated BDT boundaries, e.g. 1000,5000,20000,50000"),
    db: Session = Depends(get_db),
):
    resolved_start, resolved_end = start_date, end_date
    date_label = "All time"
    if preset and preset != "custom":
        p_start, p_end = resolve_date_range_preset(preset)
        if p_start:
            resolved_start, resolved_end = p_start, p_end
            date_label = preset.replace("_", " ").title()
    if start_date and end_date:
        date_label = f"{start_date.strftime('%d %b %Y')} - {end_date.strftime('%d %b %Y')}"
    elif resolved_start and resolved_end and date_label == "All time":
        date_label = f"{resolved_start.strftime('%d %b %Y')} - {resolved_end.strftime('%d %b %Y')}"

    region_label = "All regions"
    if region_id:
        region = db.query(Region).filter(Region.id == region_id).first()
        region_label = region.name if region else f"Region #{region_id}"

    product_label = "All products"
    if product_id:
        product = db.query(Product).filter(Product.id == product_id).first()
        product_label = product.name if product else f"Product #{product_id}"

    category_label = category if category else "All categories"

    if min_price is not None and max_price is not None:
        price_label = f"BDT {min_price:,.0f} - {max_price:,.0f}"
    elif min_price is not None:
        price_label = f">= BDT {min_price:,.0f}"
    elif max_price is not None:
        price_label = f"<= BDT {max_price:,.0f}"
    else:
        price_label = "All prices"

    quantity_label_map = {
        "low": "Low (1-2 units)", "medium": "Medium (3-5 units)", "high": "High (6+ units)",
    }
    if quantity_level == "custom":
        quantity_label = f"Custom ({min_quantity or 0}-{max_quantity or '∞'} units)"
    else:
        quantity_label = quantity_label_map.get(quantity_level, "All quantities")

    buckets_list: Optional[List[float]] = None
    if price_buckets:
        try:
            buckets_list = sorted(float(b.strip()) for b in price_buckets.split(",") if b.strip())
        except ValueError:
            buckets_list = None

    return {
        "start_date": resolved_start, "end_date": resolved_end, "date_label": date_label,
        "region_id": region_id, "region_label": region_label,
        "category": category, "category_label": category_label,
        "product_id": product_id, "product_label": product_label,
        "min_price": min_price, "max_price": max_price, "price_label": price_label,
        "quantity_level": quantity_level, "min_quantity": min_quantity, "max_quantity": max_quantity,
        "quantity_label": quantity_label,
        "group_by": group_by, "price_buckets": buckets_list,
    }


@router.get("/builder", response_model=APIResponse[ReportBuilderResponse])
def build_report(
    filters: dict = Depends(_builder_filters),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    report = ReportBuilderService.generate(db, **filters)
    return APIResponse(success=True, message="Report generated", data=report)


@router.get("/builder/export/csv")
def export_builder_csv(
    filters: dict = Depends(_builder_filters),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    report = ReportBuilderService.generate(db, **filters)
    csv_content = ReportBuilderService.export_csv(report)
    filename = f"salesiq_report_{datetime.now(APP_TIMEZONE).strftime('%Y%m%d_%H%M')}.csv"
    return Response(
        content=csv_content, media_type="text/csv",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'}
    )


@router.get("/builder/export/pdf")
async def export_builder_pdf(
    filters: dict = Depends(_builder_filters),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    report = ReportBuilderService.generate(db, **filters)
    pdf_bytes = await ReportBuilderService.export_pdf(report)
    filename = f"salesiq_report_{datetime.now(APP_TIMEZONE).strftime('%Y%m%d_%H%M')}.pdf"
    return Response(
        content=pdf_bytes, media_type="application/pdf",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'}
    )


@router.get("/monthly", response_model=APIResponse[dict])
async def get_monthly_report_data(
    start_date: Optional[date] = Query(None),
    end_date: Optional[date] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    kpis = AnalyticsService.get_summary_kpis(db, start_date, end_date)
    top_prods = AnalyticsService.get_sales_by_product(db, start_date, end_date, limit=5)
    categories = AnalyticsService.get_sales_by_category(db, start_date, end_date)
    regions = AnalyticsService.get_sales_by_region(db, start_date, end_date)
    monthly_trend = AnalyticsService.get_monthly_comparison(db, months_count=6)

    context = {
        "kpis": kpis.model_dump(),
        "top_products": [p.model_dump() for p in top_prods],
        "categories": [c.model_dump() for c in categories],
        "regions": [r.model_dump() for r in regions],
    }
    ai_summary = await GroundedAIEngine().generate_insight(context)

    return APIResponse(
        success=True,
        message="Monthly intelligence report data compiled",
        data={
            "summary_kpis": kpis,
            "top_products": top_prods,
            "categories": categories,
            "regions": regions,
            "monthly_trend": monthly_trend,
            "ai_executive_summary": ai_summary,
        }
    )


@router.get("/export/csv")
def export_sales_csv(
    start_date: Optional[date] = Query(None),
    end_date: Optional[date] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    csv_content = ReportService.export_sales_csv(db, start_date=start_date, end_date=end_date)
    filename = f"sales_export_{date.today().strftime('%Y%m%d')}.csv"
    return Response(
        content=csv_content,
        media_type="text/csv",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'}
    )


@router.get("/export/pdf")
async def export_sales_pdf(
    start_date: Optional[date] = Query(None),
    end_date: Optional[date] = Query(None),
    period_title: str = Query("Monthly Sales Intelligence Report"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    pdf_bytes = await ReportService.generate_pdf_report(
        db,
        period_title=period_title,
        start_date=start_date,
        end_date=end_date
    )
    filename = f"sales_report_{date.today().strftime('%Y%m%d')}.pdf"
    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'}
    )
