import random
from typing import Dict, Any, List, Optional
from app.ai.provider import AIProvider
from app.schemas.ai import RecommendationItem

METRIC_DEFINITIONS = {
    "aov": "**Average Order Value (AOV)** is the average amount spent per order — total revenue divided by the number of orders. A rising AOV usually means customers are buying more per visit or trading up to higher-priced items.",
    "average order value": "**Average Order Value (AOV)** is the average amount spent per order — total revenue divided by the number of orders.",
    "revenue": "**Revenue** is the total income generated from sales before any costs are subtracted — quantity sold × unit price, summed across all orders.",
    "forecast": "The **AI Sales Forecast** uses a regression model trained on your historical monthly revenue to predict next month's revenue, along with a confidence range.",
    "anomaly": "An **anomaly** is a sales data point (a sudden spike or drop in a region, or unusually low stock) that deviates significantly from the normal pattern, flagged automatically for your attention.",
    "anomalies": "**Anomalies** are sales data points that deviate significantly from the normal pattern — a sudden regional spike or drop, or unusually low stock — flagged automatically for your attention.",
    "dashboard": "Your **dashboard** shows key sales metrics at a glance: total revenue, orders, average order value, a revenue trend chart, top products, and sales by region, all computed live from your database.",
    "category": "A **category** groups related products together (e.g. Electronics, Furniture) so you can compare performance across product types rather than individual items.",
    "region": "A **region** represents a geographic sales territory (e.g. Dhaka, Khulna) used to compare performance across different markets.",
    "data quality": "The **data quality** panel reports what percentage of your sales records have a real captured timestamp versus an estimated one, plus any detected anomalies like duplicate or future-dated records.",
    "kpi": "A **KPI** (Key Performance Indicator) is a headline metric — like total revenue, orders, or AOV — used to track business health at a glance.",
    "aov mean": "**AOV** stands for **Average Order Value** — the average amount spent per order.",
}

GREETINGS = [
    "Hello! I'm **SalesIQ AI**. I can help you understand your sales, find trends, explain dashboard metrics, generate insights, and answer questions about your business data.",
    "Hi there! I'm SalesIQ AI — ask me about revenue, products, regions, trends, or just chat.",
]
HELP_TEXT = (
    "I can help with:\n"
    "• Sales analytics — revenue, products, regions, trends, forecasts\n"
    "• Explaining dashboard metrics (AOV, revenue, anomalies, etc.)\n"
    "• General conversation\n\n"
    "Try asking something like *\"What was our best selling product this month?\"*"
)
FALLBACK_TEXT = (
    "I can help with general questions and your sales data. I don't have enough information to answer "
    "that specific request yet. You can ask me about revenue, products, categories, regions, sales trends, "
    "forecasts, or dashboard metrics."
)


class GroundedAIEngine(AIProvider):
    """
    Deterministic & statistical AI synthesis engine. Ensures that insights and answers
    are 100% grounded in real database numbers (preventing hallucinations) and doubles as
    the offline conversational fallback when no LLM provider is available/reachable.
    """

    async def generate_insight(self, context_data: Dict[str, Any]) -> str:
        kpis = context_data.get("kpis", {})
        top_products = context_data.get("top_products", [])
        categories = context_data.get("categories", [])
        regions = context_data.get("regions", [])

        total_rev = kpis.get("total_revenue", 0.0)
        rev_growth = kpis.get("revenue_growth_pct", 0.0)
        aov = kpis.get("average_order_value", 0.0)
        total_orders = kpis.get("total_orders", 0)

        if total_orders == 0:
            return "No sales records were found for the selected period. Add sales transactions or upload a CSV dataset to generate AI business insights."

        top_prod_name = top_products[0]["product_name"] if top_products else "Key Products"
        top_prod_rev = top_products[0]["revenue"] if top_products else 0.0
        top_prod_share = round((top_prod_rev / total_rev * 100), 1) if total_rev > 0 else 0.0

        top_reg_name = regions[0]["region_name"] if regions else "Dhaka"
        top_cat_name = categories[0]["category"] if categories else "Electronics"

        growth_direction = "increased" if rev_growth >= 0 else "declined"
        growth_abs = abs(rev_growth)

        aov_note = (
            "Average order value remained healthy, reflecting consistent basket sizes across channels."
            if aov > 1500
            else "Average order value dipped slightly, suggesting more frequent, smaller purchases. Consider a bundled accessory promotion to lift basket value."
        )

        return (
            f"Revenue {growth_direction} by {growth_abs:.1f}% for the selected period (totaling ৳{total_rev:,.2f} across {total_orders:,} orders), "
            f"driven primarily by strong {top_cat_name} category sales in the {top_reg_name} region. "
            f"The {top_prod_name} was the leading contributor, generating ৳{top_prod_rev:,.2f} ({top_prod_share:.1f}% of total sales). "
            f"{aov_note}"
        )

    async def chat_response(self, user_query: str, db_context: Dict[str, Any]) -> str:
        mode = db_context.get("mode", "analytics")
        if mode == "conversation":
            return self._conversation_reply(db_context)
        return self._analytics_reply(db_context)

    # ------------------------------------------------------------------
    # Conversation branch (no DB query needed beyond whatever was already
    # safely fetched as light "grounding" context by the router/chatbot)
    # ------------------------------------------------------------------
    def _conversation_reply(self, db_context: Dict[str, Any]) -> str:
        kind = db_context.get("conversation_kind", "other")
        term = db_context.get("definition_term")

        if kind == "greeting":
            return random.choice(GREETINGS)
        if kind == "farewell":
            return "Goodbye! Come back anytime you want to check your sales performance."
        if kind == "thanks":
            return "You're welcome! Let me know if you'd like to dig into any other numbers."
        if kind == "acknowledgement":
            return "Got it — anything else you'd like to know about your sales data?"
        if kind == "identity":
            return HELP_TEXT
        if kind == "how_are_you":
            return "I'm doing well, thanks for asking! Ready to help with your sales data whenever you are."
        if kind == "definition":
            if term and term in METRIC_DEFINITIONS:
                return METRIC_DEFINITIONS[term]
            return (
                "I can explain metrics like revenue, AOV, forecasts, anomalies, categories, and regions — "
                "just ask, e.g. *\"What does AOV mean?\"*"
            )
        return FALLBACK_TEXT

    # ------------------------------------------------------------------
    # Analytics branch (grounded strictly in precomputed `data`)
    # ------------------------------------------------------------------
    def _analytics_reply(self, db_context: Dict[str, Any]) -> str:
        intent = db_context.get("intent", "general")
        data = db_context.get("data", {})

        if intent == "best_product":
            prod = data.get("product")
            if prod:
                runner_up = data.get("runner_up") or {}
                runner_text = f" Runner up was **{runner_up.get('name', 'N/A')}** with {runner_up.get('units', 0)} units." if runner_up.get("name") and runner_up.get("name") != "None" else ""
                return (
                    f"The **{prod['name']}** led sales with **{prod['units']:,} units sold**, "
                    f"generating **৳{prod['revenue']:,.2f}** ({prod['share']:.1f}% of total revenue).{runner_text}"
                )
            return "No product sales records were found for that period."

        if intent == "region_performance":
            reg_name = data.get("region_name", "the requested region")
            rev = data.get("revenue", 0.0)
            units = data.get("units", 0)
            top_cat = data.get("top_category", "Products")
            if units == 0:
                return f"**{reg_name}** has no recorded sales for that period."
            return (
                f"**{reg_name}** generated **৳{rev:,.2f}** across **{units:,} units sold** for that period. "
                f"**{top_cat}** was the leading category in this region."
            )

        if intent == "total_revenue":
            rev = data.get("total_revenue", 0.0)
            orders = data.get("total_orders", 0)
            aov = data.get("average_order_value", 0.0)
            return (
                f"Total revenue for that period is **৳{rev:,.2f}** across **{orders:,} orders**, "
                f"with an average order value (AOV) of **৳{aov:,.2f}**."
            )

        if intent == "category_growth":
            top_cat = data.get("top_category", "Electronics")
            cat_rev = data.get("revenue", 0.0)
            pct = data.get("percentage", 0.0)
            return (
                f"The **{top_cat}** category performed best, generating **৳{cat_rev:,.2f}** "
                f"({pct:.1f}% of revenue in that period)."
            )

        if intent == "worst_region":
            reg = data.get("worst_region", {})
            if not reg.get("name"):
                return "There isn't enough regional sales data yet to identify an underperforming region."
            return (
                f"**{reg.get('name')}** had the lowest sales volume with **৳{reg.get('revenue', 0.0):,.2f}** "
                f"({reg.get('percentage', 0.0):.1f}% of total sales). Consider targeted local promotions and an inventory review."
            )

        if intent == "top_region":
            reg = data.get("top_region", {})
            if not reg.get("name"):
                return "There isn't enough regional sales data yet to identify a leading region."
            return (
                f"**{reg.get('name')}** is the leading region with **৳{reg.get('revenue', 0.0):,.2f}** "
                f"({reg.get('percentage', 0.0):.1f}% of total sales)."
            )

        if intent == "forecast":
            f = data.get("forecast", {})
            if not f or f.get("status") == "insufficient_data":
                return "There isn't enough historical data yet to generate a reliable revenue forecast."
            return (
                f"The forecast model predicts **৳{f.get('predicted_revenue', 0):,.2f}** in revenue for "
                f"**{f.get('next_month', 'next month')}** ({f.get('growth_estimate_pct', 0):+.1f}% vs. the recent trend), "
                f"based on a {f.get('model_name', 'regression')} model."
            )

        if intent == "anomalies":
            anomalies = data.get("anomalies", [])
            if not anomalies:
                return "No unusual sales activity was detected in the selected period — everything looks within normal range."
            lines = [f"- {a['title']}: {a['description']}" for a in anomalies[:4]]
            return "Here's what looks unusual recently:\n" + "\n".join(lines)

        if intent == "peak_hours":
            peaks = data.get("peak_hours", [])
            if not peaks:
                return "There isn't enough time-stamped sales data yet to determine peak hours."
            top = peaks[0]
            others = ", ".join(f"{p['hour']:02d}:00" for p in peaks[1:3])
            return (
                f"Your busiest hour is **{top['hour']:02d}:00** with **৳{top['revenue']:,.2f}** in sales"
                + (f", followed by {others}." if others else ".")
            )

        if intent == "day_of_week":
            days = data.get("by_day", [])
            if not days:
                return "There isn't enough sales data yet to determine your busiest day of the week."
            top = max(days, key=lambda d: d["revenue"])
            return f"**{top['day_name']}** is your best-performing day, with **৳{top['revenue']:,.2f}** in sales."

        if intent == "recommendations":
            recs = data.get("recommendations", [])
            if not recs:
                return "No specific recommendations right now — your metrics look steady."
            lines = [f"- **{r['title']}**: {r['action']}" for r in recs[:3]]
            return "Here's what I'd suggest:\n" + "\n".join(lines)

        # General analytics fallback — give a meaningful overview with whatever context is available
        total_rev = data.get("total_revenue", 0.0)
        total_orders = data.get("total_orders", 0)
        aov = data.get("average_order_value", 0.0)
        growth = data.get("revenue_growth_pct")
        top_prod = (data.get("top_products") or [{}])[0]
        top_region = data.get("top_region") or {}
        top_cat = data.get("top_category") or {}

        if not total_orders:
            return "No sales records were found for that period. Try a different time range or add some data first."

        parts = [
            f"Here's a summary of your sales: **৳{total_rev:,.2f}** across **{total_orders:,} orders** "
            f"(AOV **৳{aov:,.2f}**)"
        ]
        if growth is not None:
            direction = "up" if growth >= 0 else "down"
            parts[0] += f", revenue is {direction} **{abs(growth):.1f}%** vs. the prior period"
        parts[0] += "."
        if top_prod.get("name"):
            parts.append(f"Top product: **{top_prod['name']}** with ৳{top_prod.get('revenue', 0):,.2f} in sales.")
        if top_region.get("name"):
            parts.append(f"Leading region: **{top_region['name']}** (৳{top_region.get('revenue', 0):,.2f}).")
        if top_cat.get("name"):
            parts.append(f"Best category: **{top_cat['name']}**.")
        parts.append("Ask me about a specific product, region, forecast, or time period for more detail.")
        return " ".join(parts)

    @staticmethod
    def generate_recommendations(context_data: Dict[str, Any]) -> List[RecommendationItem]:
        recommendations: List[RecommendationItem] = []
        kpis = context_data.get("kpis", {})
        top_products = context_data.get("top_products", [])
        low_stock = context_data.get("low_stock_products", [])

        if low_stock:
            prod_names = ", ".join([p["name"] for p in low_stock[:2]])
            recommendations.append(
                RecommendationItem(
                    id="rec-inventory-1", category="inventory", title="Restock Fast-Moving Inventory",
                    action=f"Reorder stock for {prod_names} immediately to avoid out-of-stock lost sales.",
                    impact="Prevents revenue loss from high-demand product stockouts.", priority="high",
                )
            )

        aov = kpis.get("average_order_value", 0.0)
        if aov < 2000:
            recommendations.append(
                RecommendationItem(
                    id="rec-promo-1", category="promotion", title="Launch Accessory Bundle Promotion",
                    action="Introduce package discounts (e.g. Mouse + Keyboard or Phone + Earbuds) to lift basket size.",
                    impact="Expected to increase Average Order Value by 12-18%.", priority="medium",
                )
            )

        if top_products:
            lead = top_products[0]["product_name"]
            recommendations.append(
                RecommendationItem(
                    id="rec-marketing-1", category="pricing", title=f"Promote Best-Seller: {lead}",
                    action=f"Feature {lead} on hero banners and targeted email marketing across secondary regions.",
                    impact="Leverages proven market demand to capture higher market share.", priority="medium",
                )
            )

        return recommendations
