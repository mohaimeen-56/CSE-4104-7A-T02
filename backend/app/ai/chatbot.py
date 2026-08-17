from datetime import date, datetime
from typing import Dict, Any, Tuple, Optional
from sqlalchemy.orm import Session
from sqlalchemy import func, desc
from app.models.sale import Sale
from app.models.product import Product
from app.models.region import Region
from app.services.analytics_service import AnalyticsService
from app.services.chat_history_service import ChatHistoryService
from app.ml.forecaster import SalesForecaster
from app.ml.anomaly_detector import AnomalyDetector
from app.ai.provider import AIProvider
from app.ai.grounded_engine import GroundedAIEngine
from app.ai.gemini_provider import GeminiProvider
from app.ai.openai_provider import OpenAIProvider
from app.ai.deepseek_provider import DeepSeekProvider
from app.ai.router import classify_message, Classification
from app.core.config import settings


def get_ai_provider() -> AIProvider:
    choice = settings.AI_PROVIDER.lower()
    if choice == "gemini" and settings.GEMINI_API_KEY:
        return GeminiProvider()
    elif choice == "openai" and settings.OPENAI_API_KEY:
        return OpenAIProvider()
    elif choice == "deepseek" and settings.DEEPSEEK_API_KEY:
        return DeepSeekProvider()
    return GroundedAIEngine()


class SalesChatbot:
    @staticmethod
    async def process_message(
        db: Session,
        user_id: int,
        user_query: str,
        conversation_id: str,
    ) -> Tuple[str, str, Optional[str], Dict[str, Any]]:
        """Returns (ai_response, route, analytics_intent, data_context)."""
        prior_intent = ChatHistoryService.get_last_analytics_intent(db, conversation_id)
        reference_year = datetime.now().year
        classification = classify_message(
            user_query, reference_year=reference_year, has_prior_analytics_intent=bool(prior_intent)
        )

        provider = get_ai_provider()

        if classification.route == "conversation":
            ai_response = await SalesChatbot._handle_conversation(db, provider, user_query, classification, conversation_id)
            route, intent, context = "conversation", None, {"conversation_kind": classification.conversation_kind}
        else:
            intent = classification.analytics_intent or prior_intent
            ai_response, context = await SalesChatbot._handle_analytics(db, provider, user_query, intent, classification)
            route = "analytics"

        ChatHistoryService.log_turn(
            db, user_id=user_id, conversation_id=conversation_id, query=user_query,
            response=ai_response, route=route, intent=intent,
        )
        return ai_response, route, intent, context

    @staticmethod
    async def _handle_conversation(
        db: Session, provider: AIProvider, user_query: str, classification: Classification, conversation_id: str,
    ) -> str:
        # Light, safe grounding (aggregate KPIs only) so the persona can mention a real
        # figure if a definitional question calls for it -- never a per-question DB query.
        grounding = None
        if classification.conversation_kind == "definition":
            kpis = AnalyticsService.get_summary_kpis(db)
            grounding = {"total_revenue": kpis.total_revenue, "total_orders": kpis.total_orders, "aov": kpis.average_order_value}

        history = ChatHistoryService.get_recent_turns(db, conversation_id, limit=6)
        db_context = {
            "mode": "conversation",
            "conversation_kind": classification.conversation_kind,
            "definition_term": classification.definition_term,
            "history": history,
            "grounding": grounding,
        }
        return await provider.chat_response(user_query=user_query, db_context=db_context)

    @staticmethod
    async def _handle_analytics(
        db: Session, provider: AIProvider, user_query: str, intent: Optional[str], classification: Classification,
    ) -> Tuple[str, Dict[str, Any]]:
        start_date, end_date = (classification.period or (None, None))
        context: Dict[str, Any] = {}

        if intent == "best_product":
            top_prods = AnalyticsService.get_sales_by_product(db, start_date=start_date, end_date=end_date, limit=2)
            total_rev = sum(p.revenue for p in top_prods) if top_prods else 1.0
            if top_prods:
                lead = top_prods[0]
                runner = top_prods[1] if len(top_prods) > 1 else None
                context = {
                    "product": {
                        "name": lead.product_name, "units": lead.units_sold, "revenue": lead.revenue,
                        "share": round((lead.revenue / total_rev * 100), 1) if total_rev > 0 else 0.0,
                    },
                    "runner_up": {"name": runner.product_name, "units": runner.units_sold} if runner else None,
                }

        elif intent == "region_performance":
            matched_region = next((r for r in ["Dhaka", "Khulna", "Chittagong", "Sylhet", "Rajshahi"]
                                    if r.lower() in user_query.lower()), None)
            region_obj = db.query(Region).filter(Region.name.ilike(matched_region)).first() if matched_region else None
            if region_obj:
                regs = AnalyticsService.get_sales_by_region(db, start_date=start_date, end_date=end_date)
                match = next((r for r in regs if r.region_id == region_obj.id), None)
                top_cat_row = (
                    db.query(Product.category, func.sum(Sale.total_price))
                    .join(Sale, Sale.product_id == Product.id)
                    .filter(Sale.region_id == region_obj.id)
                    .group_by(Product.category)
                    .order_by(desc(func.sum(Sale.total_price)))
                    .first()
                )
                context = {
                    "region_name": region_obj.name,
                    "revenue": match.revenue if match else 0.0,
                    "units": match.units_sold if match else 0,
                    "top_category": top_cat_row[0] if top_cat_row and top_cat_row[0] else "Products",
                }

        elif intent == "top_region":
            regs = AnalyticsService.get_sales_by_region(db, start_date=start_date, end_date=end_date)
            if regs:
                top = regs[0]
                context = {"top_region": {"name": top.region_name, "revenue": top.revenue, "percentage": top.percentage}}

        elif intent == "category_growth":
            cats = AnalyticsService.get_sales_by_category(db, start_date=start_date, end_date=end_date)
            if cats:
                top_c = cats[0]
                context = {"top_category": top_c.category, "revenue": top_c.revenue, "percentage": top_c.percentage}

        elif intent == "worst_region":
            regs = AnalyticsService.get_sales_by_region(db, start_date=start_date, end_date=end_date)
            if regs:
                worst_r = regs[-1]
                context = {"worst_region": {"name": worst_r.region_name, "revenue": worst_r.revenue, "percentage": worst_r.percentage}}

        elif intent == "forecast":
            forecast = SalesForecaster.forecast_next_month(db)
            context = {"forecast": forecast.model_dump()}

        elif intent == "anomalies":
            anomalies = AnomalyDetector.detect_anomalies(db, start_date=start_date, end_date=end_date)
            context = {"anomalies": [a.model_dump() for a in anomalies[:5]]}

        elif intent == "peak_hours":
            peaks = AnalyticsService.get_peak_hours(db, start_date=start_date, end_date=end_date, limit=3)
            context = {"peak_hours": [p.model_dump() for p in peaks]}

        elif intent == "day_of_week":
            by_day = AnalyticsService.get_sales_by_day_of_week(db, start_date=start_date, end_date=end_date)
            context = {"by_day": [d.model_dump() for d in by_day]}

        elif intent == "recommendations":
            kpis = AnalyticsService.get_summary_kpis(db, start_date=start_date, end_date=end_date)
            top_prods = AnalyticsService.get_sales_by_product(db, start_date=start_date, end_date=end_date, limit=3)
            low_stock = [{"name": p.name, "stock": p.stock} for p in db.query(Product).filter(Product.stock < 20).all()]
            recs = GroundedAIEngine.generate_recommendations({
                "kpis": kpis.model_dump(), "top_products": [p.model_dump() for p in top_prods], "low_stock_products": low_stock,
            })
            context = {"recommendations": [r.model_dump() for r in recs]}

        else:  # "total_revenue", "general", or unmatched analytics fallback
            kpis = AnalyticsService.get_summary_kpis(db, start_date=start_date, end_date=end_date)
            top_prods = AnalyticsService.get_sales_by_product(db, start_date=start_date, end_date=end_date, limit=3)
            regions = AnalyticsService.get_sales_by_region(db, start_date=start_date, end_date=end_date)
            categories = AnalyticsService.get_sales_by_category(db, start_date=start_date, end_date=end_date)
            context = {
                "total_revenue": kpis.total_revenue,
                "total_orders": kpis.total_orders,
                "average_order_value": kpis.average_order_value,
                "revenue_growth_pct": kpis.revenue_growth_pct,
                "top_products": [{"name": p.product_name, "units": p.units_sold, "revenue": p.revenue} for p in top_prods],
                "top_region": {"name": regions[0].region_name, "revenue": regions[0].revenue} if regions else None,
                "top_category": {"name": categories[0].category, "revenue": categories[0].revenue} if categories else None,
            }
            intent = intent or "general"

        ai_response = await provider.chat_response(
            user_query=user_query, db_context={"mode": "analytics", "intent": intent, "data": context}
        )
        return ai_response, context
