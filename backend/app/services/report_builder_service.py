import io
import csv
from datetime import date, datetime
from decimal import Decimal
from typing import Optional, List, Dict, Any
from sqlalchemy.orm import Session
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch

from app.models.product import Product
from app.models.region import Region
from app.services.analytics_service import AnalyticsService
from app.core.timeutil import APP_TIMEZONE
from app.schemas.report import (
    ReportRow, PriceRangeRow, ReportTotals, ReportFilterSummary, ReportDefinitions, ReportBuilderResponse,
)

# Sensible, documented defaults -- not permanently hardcoded: callers may override
# both via query params (report builder API accepts custom quantity_ranges/price_buckets).
DEFAULT_QUANTITY_LEVELS = {
    "low": "1-2 units",
    "medium": "3-5 units",
    "high": "6+ units",
}
DEFAULT_QUANTITY_RANGES = {"low": (1, 2), "medium": (3, 5), "high": (6, None)}
DEFAULT_PRICE_BUCKETS = [1000.0, 5000.0, 20000.0, 50000.0]  # BDT boundaries

GROUP_BY_TIME = {"hour", "day", "week", "month", "quarter", "year"}
GROUP_BY_DIMENSION = {"category", "subcategory", "brand", "product", "region"}


def _price_bucket_label(price: float, buckets: List[float]) -> str:
    prev = 0.0
    for b in buckets:
        if price < b:
            return f"< BDT {b:,.0f}" if prev == 0 else f"BDT {prev:,.0f}-{b:,.0f}"
        prev = b
    return f"> BDT {prev:,.0f}"


def _quantity_level_of(qty: int, ranges: Dict[str, tuple]) -> Optional[str]:
    for level, (lo, hi) in ranges.items():
        if hi is None:
            if qty >= lo:
                return level
        elif lo <= qty <= hi:
            return level
    return None


class ReportBuilderService:
    @staticmethod
    def _fetch_filtered_sales(
        db: Session,
        start_date: Optional[date],
        end_date: Optional[date],
        region_id: Optional[int],
        category: Optional[str],
        product_id: Optional[int],
        min_price: Optional[Decimal],
        max_price: Optional[Decimal],
        quantity_level: Optional[str],
        min_quantity: Optional[int],
        max_quantity: Optional[int],
        quantity_ranges: Dict[str, tuple],
    ):
        query = AnalyticsService.build_filtered_query(
            db, start_date, end_date, region_id=region_id, category=category,
            product_id=product_id, min_price=min_price, max_price=max_price,
        )
        sales = query.all()

        if quantity_level and quantity_level != "all":
            if quantity_level == "custom":
                lo = min_quantity if min_quantity is not None else 0
                hi = max_quantity
                sales = [s for s in sales if s.quantity >= lo and (hi is None or s.quantity <= hi)]
            else:
                lo, hi = quantity_ranges.get(quantity_level, (None, None))
                if lo is not None:
                    sales = [s for s in sales if s.quantity >= lo and (hi is None or s.quantity <= hi)]

        return sales

    @staticmethod
    def _group_key(sale, group_by: str) -> str:
        if group_by == "hour":
            return sale.sale_datetime.astimezone(APP_TIMEZONE).strftime("%Y-%m-%d %H:00")
        if group_by == "day":
            return sale.sale_date.strftime("%Y-%m-%d")
        if group_by == "week":
            iso_year, iso_week, _ = sale.sale_date.isocalendar()
            return f"{iso_year}-W{iso_week:02d}"
        if group_by == "month":
            return sale.sale_date.strftime("%Y-%m")
        if group_by == "quarter":
            q = (sale.sale_date.month - 1) // 3 + 1
            return f"{sale.sale_date.year}-Q{q}"
        if group_by == "year":
            return str(sale.sale_date.year)
        if group_by == "category":
            return sale.product.category or "Uncategorized"
        if group_by == "subcategory":
            return sale.product.subcategory or "Unspecified"
        if group_by == "brand":
            return sale.product.brand or "Unbranded"
        if group_by == "product":
            return sale.product.name
        if group_by == "region":
            return sale.region.name
        return "All"

    @staticmethod
    def generate(
        db: Session,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
        date_label: str = "All time",
        region_id: Optional[int] = None,
        region_label: str = "All regions",
        category: Optional[str] = None,
        category_label: str = "All categories",
        product_id: Optional[int] = None,
        product_label: str = "All products",
        min_price: Optional[Decimal] = None,
        max_price: Optional[Decimal] = None,
        price_label: str = "All prices",
        quantity_level: Optional[str] = None,
        min_quantity: Optional[int] = None,
        max_quantity: Optional[int] = None,
        quantity_label: str = "All quantities",
        group_by: str = "month",
        price_buckets: Optional[List[float]] = None,
        quantity_ranges: Optional[Dict[str, tuple]] = None,
    ) -> ReportBuilderResponse:
        buckets = price_buckets or DEFAULT_PRICE_BUCKETS
        q_ranges = quantity_ranges or DEFAULT_QUANTITY_RANGES

        sales = ReportBuilderService._fetch_filtered_sales(
            db, start_date, end_date, region_id, category, product_id, min_price, max_price,
            quantity_level, min_quantity, max_quantity, q_ranges,
        )

        # Grouped rows (time or dimension based)
        grouped: Dict[str, Dict[str, Any]] = {}
        for s in sales:
            key = ReportBuilderService._group_key(s, group_by)
            g = grouped.setdefault(key, {"units": 0, "revenue": 0.0, "orders": 0})
            g["units"] += s.quantity
            g["revenue"] += float(s.total_price)
            g["orders"] += 1

        rows = [
            ReportRow(
                group_key=k, units=v["units"], revenue=round(v["revenue"], 2), orders=v["orders"],
                avg_price=round(v["revenue"] / v["units"], 2) if v["units"] > 0 else 0.0,
            )
            for k, v in sorted(grouped.items())
        ]

        # Price-range breakdown (always computed, independent of group_by)
        price_grouped: Dict[str, Dict[str, Any]] = {}
        for s in sales:
            label = _price_bucket_label(float(s.unit_price), buckets)
            g = price_grouped.setdefault(label, {"units": 0, "revenue": 0.0})
            g["units"] += s.quantity
            g["revenue"] += float(s.total_price)
        price_rows = [
            PriceRangeRow(range_label=k, units=v["units"], revenue=round(v["revenue"], 2))
            for k, v in price_grouped.items()
        ]

        total_units = sum(s.quantity for s in sales)
        total_revenue = sum(float(s.total_price) for s in sales)
        total_orders = len(sales)

        totals = ReportTotals(
            units=total_units, revenue=round(total_revenue, 2), orders=total_orders,
            avg_order_value=round(total_revenue / total_orders, 2) if total_orders > 0 else 0.0,
        )

        filter_summary = ReportFilterSummary(
            date_label=date_label,
            category_label=category_label,
            region_label=region_label,
            product_label=product_label,
            price_label=price_label,
            quantity_label=quantity_label,
            grouping_label=group_by.replace("_", " ").title(),
            generated_at=datetime.now(APP_TIMEZONE).strftime("%d %b %Y, %H:%M"),
        )

        definitions = ReportDefinitions(
            quantity_levels=DEFAULT_QUANTITY_LEVELS,
            price_buckets=buckets,
        )

        return ReportBuilderResponse(
            rows=rows, price_range_rows=price_rows, totals=totals,
            filter_summary=filter_summary, definitions=definitions,
        )

    @staticmethod
    def export_csv(report: ReportBuilderResponse) -> str:
        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow(["Report: Product Performance"])
        writer.writerow(["Date", report.filter_summary.date_label])
        writer.writerow(["Category", report.filter_summary.category_label])
        writer.writerow(["Region", report.filter_summary.region_label])
        writer.writerow(["Product", report.filter_summary.product_label])
        writer.writerow(["Price", report.filter_summary.price_label])
        writer.writerow(["Quantity", report.filter_summary.quantity_label])
        writer.writerow(["Grouping", report.filter_summary.grouping_label])
        writer.writerow(["Generated", report.filter_summary.generated_at])
        writer.writerow([])
        writer.writerow(["Group", "Units", "Orders", "Revenue (BDT)", "Avg Price (BDT)"])
        for r in report.rows:
            writer.writerow([r.group_key, r.units, r.orders, f"{r.revenue:.2f}", f"{r.avg_price:.2f}"])
        writer.writerow([])
        writer.writerow(["Totals", report.totals.units, report.totals.orders, f"{report.totals.revenue:.2f}", ""])
        writer.writerow([])
        writer.writerow(["Price Range", "Units", "Revenue (BDT)"])
        for pr in report.price_range_rows:
            writer.writerow([pr.range_label, pr.units, f"{pr.revenue:.2f}"])
        return output.getvalue()

    @staticmethod
    async def export_pdf(report: ReportBuilderResponse) -> bytes:
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=letter, rightMargin=36, leftMargin=36, topMargin=36, bottomMargin=36)
        styles = getSampleStyleSheet()

        primary_color = colors.HexColor("#1F3864")
        secondary_color = colors.HexColor("#2E86AB")
        dark_text = colors.HexColor("#2D2D2D")

        title_style = ParagraphStyle("DocTitle", parent=styles["Heading1"], fontSize=20, leading=24,
                                      textColor=primary_color, fontName="Helvetica-Bold", spaceAfter=4)
        subtitle_style = ParagraphStyle("DocSubtitle", parent=styles["Normal"], fontSize=10, leading=14,
                                         textColor=colors.HexColor("#6B7280"), spaceAfter=6)
        section_heading = ParagraphStyle("SectionHead", parent=styles["Heading2"], fontSize=13, leading=17,
                                          textColor=primary_color, fontName="Helvetica-Bold", spaceBefore=12, spaceAfter=6)

        story = [
            Paragraph("SalesIQ Report Builder", title_style),
            Paragraph("Product Performance Report", subtitle_style),
        ]

        fs = report.filter_summary
        filter_data = [
            ["Date", fs.date_label],
            ["Category", fs.category_label],
            ["Region", fs.region_label],
            ["Product", fs.product_label],
            ["Price", fs.price_label],
            ["Quantity", fs.quantity_label],
            ["Grouping", fs.grouping_label],
            ["Generated", fs.generated_at],
        ]
        filter_table = Table(filter_data, colWidths=[1.4 * inch, 5.3 * inch])
        filter_table.setStyle(TableStyle([
            ("FONTSIZE", (0, 0), (-1, -1), 9),
            ("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold"),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
            ("TOPPADDING", (0, 0), (-1, -1), 3),
        ]))
        story.append(filter_table)
        story.append(HRFlowable(width="100%", thickness=1.5, color=secondary_color, spaceBefore=8, spaceAfter=14))

        story.append(Paragraph(f"Results by {fs.grouping_label}", section_heading))
        row_data = [["Group", "Units", "Orders", "Revenue (BDT)", "Avg Price (BDT)"]]
        for r in report.rows[:60]:
            row_data.append([r.group_key, f"{r.units:,}", f"{r.orders:,}", f"{r.revenue:,.2f}", f"{r.avg_price:,.2f}"])
        row_table = Table(row_data, colWidths=[2.2 * inch, 1.1 * inch, 1.1 * inch, 1.4 * inch, 1.4 * inch])
        row_table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), primary_color),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("FONTSIZE", (0, 0), (-1, -1), 8.5),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
            ("TOPPADDING", (0, 0), (-1, -1), 5),
            ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#E3E7EC")),
            ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#F8FAFC")]),
        ]))
        story.append(row_table)
        story.append(Spacer(1, 12))

        story.append(Paragraph("Revenue by Price Range", section_heading))
        pr_data = [["Price Range", "Units", "Revenue (BDT)"]]
        for pr in report.price_range_rows:
            pr_data.append([pr.range_label, f"{pr.units:,}", f"{pr.revenue:,.2f}"])
        pr_table = Table(pr_data, colWidths=[2.5 * inch, 2.0 * inch, 2.2 * inch])
        pr_table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), secondary_color),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("FONTSIZE", (0, 0), (-1, -1), 8.5),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
            ("TOPPADDING", (0, 0), (-1, -1), 5),
            ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#E3E7EC")),
            ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#F8FAFC")]),
        ]))
        story.append(pr_table)
        story.append(Spacer(1, 12))

        totals_text = (
            f"<b>Totals:</b> {report.totals.units:,} units · {report.totals.orders:,} orders · "
            f"BDT {report.totals.revenue:,.2f} revenue · BDT {report.totals.avg_order_value:,.2f} avg order value"
        )
        story.append(Paragraph(totals_text, ParagraphStyle("Totals", parent=styles["Normal"], fontSize=10, textColor=dark_text)))
        story.append(HRFlowable(width="100%", thickness=0.5, color=colors.HexColor("#CBD5E1"), spaceBefore=12, spaceAfter=6))
        story.append(Paragraph("SalesIQ · CSE4104-7A-T02 · Confidential Business Report", subtitle_style))

        doc.build(story)
        pdf_bytes = buffer.getvalue()
        buffer.close()
        return pdf_bytes
