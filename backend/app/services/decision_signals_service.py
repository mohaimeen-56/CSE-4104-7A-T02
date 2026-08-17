"""
Decision Signals Service — computes structured business intelligence signals
from real analytics data. Never uses LLM to fabricate numbers.
Signals are: opportunities, risks, anomalies, trends, actions.
"""
from datetime import date, timedelta
from typing import List, Optional
from sqlalchemy.orm import Session

from app.services.analytics_service import AnalyticsService
from app.ml.anomaly_detector import AnomalyDetector
from app.schemas.analytics import DecisionSignal, DecisionSignalsResponse


def _pct_change(current: float, previous: float) -> Optional[float]:
    if previous == 0:
        return None
    return round((current - previous) / previous * 100, 1)


def generate_decision_signals(db: Session) -> DecisionSignalsResponse:
    today = date.today()
    # Current period: last 30 days
    period_start = today - timedelta(days=30)
    # Previous period: 30 days before that
    prev_start = today - timedelta(days=60)
    prev_end = today - timedelta(days=31)

    # Gather category data for both periods
    curr_cats = AnalyticsService.get_sales_by_category(db, period_start, today)
    prev_cats = AnalyticsService.get_sales_by_category(db, prev_start, prev_end)

    # Gather region data for both periods
    curr_regions = AnalyticsService.get_sales_by_region(db, period_start, today)
    prev_regions = AnalyticsService.get_sales_by_region(db, prev_start, prev_end)

    # Overall KPIs for both periods
    curr_kpis = AnalyticsService.get_summary_kpis(db, period_start, today)
    prev_kpis = AnalyticsService.get_summary_kpis(db, prev_start, prev_end)

    # Anomalies from ML detector
    anomalies = AnomalyDetector.detect_anomalies(db, period_start, today)

    signals: List[DecisionSignal] = []

    # ── Opportunities: categories growing faster than average ──────────────────
    avg_rev_change = _pct_change(curr_kpis.total_revenue, prev_kpis.total_revenue) or 0
    prev_cat_map = {c.category: c.revenue for c in prev_cats}

    for cat in curr_cats:
        prev_rev = prev_cat_map.get(cat.category, 0)
        change = _pct_change(cat.revenue, prev_rev)
        if change is not None and change > avg_rev_change + 5:
            signals.append(DecisionSignal(
                signal_type="opportunity",
                title=f"{cat.category} Category Growth",
                description=(
                    f"{cat.category} revenue grew {change:+.1f}% vs previous 30 days, "
                    f"outpacing overall growth of {avg_rev_change:+.1f}%. "
                    f"Expanding focus here could accelerate total revenue."
                ),
                severity="high" if change > avg_rev_change + 15 else "medium",
                link_path="/explorer?category=" + cat.category,
                metric_value=change,
                metric_label="% growth",
                confidence="high",
            ))

    # ── Risks: regions with meaningful revenue decline ─────────────────────────
    prev_region_map = {r.region_name: r.revenue for r in prev_regions}
    for reg in curr_regions:
        prev_rev = prev_region_map.get(reg.region_name, 0)
        change = _pct_change(reg.revenue, prev_rev)
        if change is not None and change < -8:
            signals.append(DecisionSignal(
                signal_type="risk",
                title=f"{reg.region_name} Revenue Decline",
                description=(
                    f"{reg.region_name} revenue declined {change:.1f}% over the last 30 days. "
                    f"This warrants investigation into local demand, pricing, or inventory."
                ),
                severity="high" if change < -15 else "medium",
                link_path=f"/explorer?region={reg.region_id}",
                metric_value=change,
                metric_label="% change",
                confidence="high",
            ))

    # ── AOV trend ─────────────────────────────────────────────────────────────
    aov_change = _pct_change(curr_kpis.average_order_value, prev_kpis.average_order_value)
    if aov_change is not None:
        if aov_change < -5:
            signals.append(DecisionSignal(
                signal_type="trend",
                title="Average Order Value Declining",
                description=(
                    f"AOV fell {aov_change:.1f}% to ৳{curr_kpis.average_order_value:,.0f}. "
                    f"Bundling strategies or minimum-order promotions may help reverse this."
                ),
                severity="medium",
                link_path="/insights",
                metric_value=curr_kpis.average_order_value,
                metric_label="৳ AOV",
                confidence="high",
            ))
        elif aov_change > 5:
            signals.append(DecisionSignal(
                signal_type="trend",
                title="Average Order Value Rising",
                description=(
                    f"AOV increased {aov_change:+.1f}% to ৳{curr_kpis.average_order_value:,.0f}. "
                    f"Customers are spending more per transaction — a positive sign for margin."
                ),
                severity="low",
                link_path="/insights",
                metric_value=curr_kpis.average_order_value,
                metric_label="৳ AOV",
                confidence="high",
            ))

    # ── Anomalies from ML ─────────────────────────────────────────────────────
    for anom in anomalies[:3]:
        product_name = getattr(anom, 'product_name', None) or "unknown product"
        region_name = getattr(anom, 'region_name', None) or "unknown region"
        anomaly_date = getattr(anom, 'sale_date', None) or str(today)
        signals.append(DecisionSignal(
            signal_type="anomaly",
            title=f"Unusual Activity Detected",
            description=(
                f"{product_name} in {region_name} showed unusual sales on {anomaly_date}. "
                f"Statistical deviation detected — may indicate data entry issues or genuine demand shift."
            ),
            severity="medium",
            link_path="/insights",
            confidence="medium",
        ))

    # ── Revenue overall trend signal ──────────────────────────────────────────
    rev_change = _pct_change(curr_kpis.total_revenue, prev_kpis.total_revenue)
    if rev_change is not None:
        if abs(rev_change) >= 5:
            signals.append(DecisionSignal(
                signal_type="trend",
                title=f"Overall Revenue {'Gaining' if rev_change > 0 else 'Declining'}",
                description=(
                    f"Total revenue {'grew' if rev_change > 0 else 'fell'} {abs(rev_change):.1f}% "
                    f"over the last 30 days. "
                    + (f"Growth is ahead of expectations — sustain current strategy." if rev_change > 0
                       else f"Review product mix and regional performance for root cause.")
                ),
                severity="high" if abs(rev_change) > 15 else "medium",
                link_path="/dashboard",
                metric_value=rev_change,
                metric_label="% vs previous period",
                confidence="high",
            ))

    # Limit to most important 8 signals, prioritize high severity
    signals.sort(key=lambda s: (
        0 if s.severity == "high" else (1 if s.severity == "medium" else 2),
        ["risk", "anomaly", "opportunity", "action", "trend"].index(s.signal_type)
        if s.signal_type in ["risk", "anomaly", "opportunity", "action", "trend"] else 5
    ))
    signals = signals[:8]

    opp_count = sum(1 for s in signals if s.signal_type == "opportunity")
    risk_count = sum(1 for s in signals if s.signal_type == "risk")
    anom_count = sum(1 for s in signals if s.signal_type == "anomaly")
    trend_count = sum(1 for s in signals if s.signal_type == "trend")

    from datetime import datetime
    return DecisionSignalsResponse(
        signals=signals,
        opportunities_count=opp_count,
        risks_count=risk_count,
        anomalies_count=anom_count,
        trends_count=trend_count,
        generated_at=datetime.utcnow().isoformat(),
    )


def generate_executive_summary(db: Session) -> dict:
    today = date.today()
    period_start = today - timedelta(days=30)
    prev_start = today - timedelta(days=60)
    prev_end = today - timedelta(days=31)

    curr_kpis = AnalyticsService.get_summary_kpis(db, period_start, today)
    prev_kpis = AnalyticsService.get_summary_kpis(db, prev_start, prev_end)
    top_prods = AnalyticsService.get_sales_by_product(db, period_start, today, limit=1)
    top_regions = AnalyticsService.get_sales_by_region(db, period_start, today)
    curr_cats = AnalyticsService.get_sales_by_category(db, period_start, today)

    rev_change = _pct_change(curr_kpis.total_revenue, prev_kpis.total_revenue) or 0
    aov_change = _pct_change(curr_kpis.average_order_value, prev_kpis.average_order_value) or 0

    top_prod_name = top_prods[0].product_name if top_prods else "your top product"
    top_prod_cat = top_prods[0].category if top_prods else "this category"
    top_region = top_regions[0].region_name if top_regions else "your leading region"

    # Find fastest growing category
    prev_cats = AnalyticsService.get_sales_by_category(db, prev_start, prev_end)
    prev_cat_map = {c.category: c.revenue for c in prev_cats}
    best_cat = None
    best_cat_growth = None
    for cat in curr_cats:
        prev_rev = prev_cat_map.get(cat.category, 0)
        chg = _pct_change(cat.revenue, prev_rev)
        if chg is not None and (best_cat_growth is None or chg > best_cat_growth):
            best_cat = cat.category
            best_cat_growth = chg

    # Build headline
    if rev_change > 5:
        headline = f"Revenue is growing strongly — up {rev_change:+.1f}% this month"
    elif rev_change < -5:
        headline = f"Revenue declined {rev_change:.1f}% — investigation recommended"
    else:
        headline = f"Revenue is stable at ৳{curr_kpis.total_revenue:,.0f} this period"

    # Build body
    body_parts = []
    if top_prods:
        body_parts.append(f"{top_prod_name} ({top_prod_cat}) leads sales in {top_region}.")
    if aov_change < -3:
        body_parts.append(f"Average order value has eased {aov_change:.1f}% — consider bundling strategies.")
    elif aov_change > 3:
        body_parts.append(f"Average order value rose {aov_change:+.1f}% — customers are spending more per transaction.")
    if best_cat and best_cat_growth and best_cat_growth > 5:
        body_parts.append(f"{best_cat} is the fastest-growing category at {best_cat_growth:+.1f}% vs last month.")

    body = " ".join(body_parts) if body_parts else "Overall business performance is within normal parameters."

    # Key opportunity
    key_opportunity = None
    if best_cat and best_cat_growth and best_cat_growth > 10:
        key_opportunity = f"Expanding {best_cat} range could amplify the {best_cat_growth:+.1f}% momentum."

    # Key risk
    key_risk = None
    prev_region_map = {r.region_name: r.revenue for r in AnalyticsService.get_sales_by_region(db, prev_start, prev_end)}
    for reg in top_regions:
        prev_rev = prev_region_map.get(reg.region_name, 0)
        chg = _pct_change(reg.revenue, prev_rev)
        if chg is not None and chg < -10:
            key_risk = f"{reg.region_name} revenue is down {chg:.1f}% — regional investigation needed."
            break

    # Confidence based on data volume
    confidence_pct = 85 if curr_kpis.total_orders > 50 else (70 if curr_kpis.total_orders > 10 else 55)

    return {
        "headline": headline,
        "body": body,
        "key_opportunity": key_opportunity,
        "key_risk": key_risk,
        "confidence_pct": confidence_pct,
        "top_performer": top_prod_name if top_prods else None,
        "top_performer_type": "product",
    }
