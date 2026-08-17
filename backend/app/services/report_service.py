import io
import csv
from datetime import datetime, date
from typing import Optional, List
from sqlalchemy.orm import Session
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch

from app.models.sale import Sale
from app.models.product import Product
from app.models.region import Region
from app.services.analytics_service import AnalyticsService
from app.ai.grounded_engine import GroundedAIEngine


class ReportService:
    @staticmethod
    def export_sales_csv(
        db: Session,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None
    ) -> str:
        query = (
            db.query(Sale)
            .join(Product, Sale.product_id == Product.id)
            .join(Region, Sale.region_id == Region.id)
            .order_by(Sale.sale_date.desc())
        )
        if start_date:
            query = query.filter(Sale.sale_date >= start_date)
        if end_date:
            query = query.filter(Sale.sale_date <= end_date)

        sales = query.all()

        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow(["ID", "Sale Date", "Product Name", "Category", "Region", "Quantity", "Unit Price (BDT)", "Total Price (BDT)"])

        for s in sales:
            writer.writerow([
                s.id,
                s.sale_date.strftime("%Y-%m-%d"),
                s.product.name if s.product else "",
                s.product.category if s.product and s.product.category else "",
                s.region.name if s.region else "",
                s.quantity,
                f"{float(s.unit_price):.2f}",
                f"{float(s.total_price):.2f}",
            ])

        return output.getvalue()

    @staticmethod
    async def generate_pdf_report(
        db: Session,
        period_title: str = "Monthly Sales Intelligence Report",
        start_date: Optional[date] = None,
        end_date: Optional[date] = None
    ) -> bytes:
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(
            buffer,
            pagesize=letter,
            rightMargin=36,
            leftMargin=36,
            topMargin=36,
            bottomMargin=36
        )

        styles = getSampleStyleSheet()

        # Custom styles
        primary_color = colors.HexColor("#1F3864")
        secondary_color = colors.HexColor("#2E86AB")
        dark_text = colors.HexColor("#2D2D2D")

        title_style = ParagraphStyle(
            "DocTitle",
            parent=styles["Heading1"],
            fontSize=20,
            leading=24,
            textColor=primary_color,
            fontName="Helvetica-Bold",
            spaceAfter=4,
        )
        subtitle_style = ParagraphStyle(
            "DocSubtitle",
            parent=styles["Normal"],
            fontSize=10,
            leading=14,
            textColor=colors.HexColor("#6B7280"),
            spaceAfter=14,
        )
        section_heading = ParagraphStyle(
            "SectionHead",
            parent=styles["Heading2"],
            fontSize=13,
            leading=17,
            textColor=primary_color,
            fontName="Helvetica-Bold",
            spaceBefore=12,
            spaceAfter=6,
        )
        body_style = ParagraphStyle(
            "Body",
            parent=styles["Normal"],
            fontSize=9.5,
            leading=14,
            textColor=dark_text,
            spaceAfter=8,
        )

        story = []

        # Header Title
        story.append(Paragraph("AI Sales Analytics Dashboard — SalesIQ", title_style))
        gen_time = datetime.now().strftime("%B %d, %Y - %I:%M %p")
        story.append(Paragraph(f"{period_title} &nbsp;|&nbsp; Generated on: {gen_time} &nbsp;|&nbsp; CSE4104-7A-T02", subtitle_style))
        story.append(HRFlowable(width="100%", thickness=1.5, color=secondary_color, spaceBefore=0, spaceAfter=14))

        # 1. KPI Summary Block
        kpis = AnalyticsService.get_summary_kpis(db, start_date=start_date, end_date=end_date)
        story.append(Paragraph("Executive KPI Summary", section_heading))

        kpi_data = [
            ["Metric", "Value", "MoM Growth"],
            ["Total Revenue", f"BDT {kpis.total_revenue:,.2f}", f"{'+' if kpis.revenue_growth_pct >= 0 else ''}{kpis.revenue_growth_pct:.1f}%"],
            ["Total Orders", f"{kpis.total_orders:,}", f"{'+' if kpis.orders_growth_pct >= 0 else ''}{kpis.orders_growth_pct:.1f}%"],
            ["Average Order Value (AOV)", f"BDT {kpis.average_order_value:,.2f}", f"{'+' if kpis.aov_growth_pct >= 0 else ''}{kpis.aov_growth_pct:.1f}%"],
        ]
        kpi_table = Table(kpi_data, colWidths=[2.5 * inch, 2.5 * inch, 2.2 * inch])
        kpi_table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), primary_color),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("FONTSIZE", (0, 0), (-1, -1), 9),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
            ("TOPPADDING", (0, 0), (-1, -1), 6),
            ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#E3E7EC")),
            ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#F8FAFC")]),
        ]))
        story.append(kpi_table)
        story.append(Spacer(1, 12))

        # 2. AI Executive Narrative
        story.append(Paragraph("AI-Generated Business Intelligence Summary", section_heading))
        top_prods = AnalyticsService.get_sales_by_product(db, start_date=start_date, end_date=end_date, limit=5)
        top_cats = AnalyticsService.get_sales_by_category(db, start_date=start_date, end_date=end_date)
        top_regs = AnalyticsService.get_sales_by_region(db, start_date=start_date, end_date=end_date)

        context_data = {
            "kpis": kpis.model_dump(),
            "top_products": [p.model_dump() for p in top_prods],
            "categories": [c.model_dump() for c in top_cats],
            "regions": [r.model_dump() for r in top_regs],
        }
        ai_summary = await GroundedAIEngine().generate_insight(context_data)
        story.append(Paragraph(ai_summary, body_style))
        story.append(Spacer(1, 10))

        # 3. Top Products Table
        story.append(Paragraph("Top Performing Products", section_heading))
        prod_table_data = [["#", "Product Name", "Category", "Units Sold", "Revenue (BDT)"]]
        for idx, p in enumerate(top_prods[:5]):
            prod_table_data.append([
                str(idx + 1),
                p.product_name,
                p.category,
                f"{p.units_sold:,}",
                f"{p.revenue:,.2f}"
            ])
        prod_table = Table(prod_table_data, colWidths=[0.4 * inch, 2.8 * inch, 1.6 * inch, 1.0 * inch, 1.4 * inch])
        prod_table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), secondary_color),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("FONTSIZE", (0, 0), (-1, -1), 8.5),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
            ("TOPPADDING", (0, 0), (-1, -1), 5),
            ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#E3E7EC")),
            ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#F8FAFC")]),
        ]))
        story.append(prod_table)
        story.append(Spacer(1, 12))

        # 4. Regional Distribution
        story.append(Paragraph("Sales Distribution by Region", section_heading))
        reg_table_data = [["Region", "Units Sold", "Revenue (BDT)", "Share (%)"]]
        for r in top_regs:
            reg_table_data.append([
                r.region_name,
                f"{r.units_sold:,}",
                f"{r.revenue:,.2f}",
                f"{r.percentage:.1f}%"
            ])
        reg_table = Table(reg_table_data, colWidths=[2.2 * inch, 1.5 * inch, 2.0 * inch, 1.5 * inch])
        reg_table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), primary_color),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("FONTSIZE", (0, 0), (-1, -1), 8.5),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
            ("TOPPADDING", (0, 0), (-1, -1), 5),
            ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#E3E7EC")),
            ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#F8FAFC")]),
        ]))
        story.append(reg_table)
        story.append(Spacer(1, 14))

        # Footer note
        footer_text = "Northern University of Business and Technology, Khulna · CSE4104-7A-T02 · Confidential Business Report"
        story.append(HRFlowable(width="100%", thickness=0.5, color=colors.HexColor("#CBD5E1"), spaceBefore=8, spaceAfter=6))
        story.append(Paragraph(footer_text, subtitle_style))

        doc.build(story)
        pdf_bytes = buffer.getvalue()
        buffer.close()
        return pdf_bytes
