from datetime import datetime, date, timedelta
from typing import Optional, List
from fastapi import APIRouter, Depends, Query, HTTPException, status
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.schemas.ai import (
    AIInsightRequest,
    AIInsightResponse,
    ForecastResponse,
    AnomalyItem,
    RecommendationItem,
    ChatMessageRequest,
    ChatMessageResponse,
)
from app.schemas.common import APIResponse
from app.services.analytics_service import AnalyticsService
from app.ml.forecaster import SalesForecaster
from app.ml.anomaly_detector import AnomalyDetector
from app.ai.chatbot import SalesChatbot, get_ai_provider
from app.ai.grounded_engine import GroundedAIEngine
from app.services.chat_history_service import ChatHistoryService
from app.models.product import Product
from app.models.user import User
from app.core.deps import get_current_user

router = APIRouter(prefix="/ai", tags=["AI & Machine Learning"])


@router.post("/insights", response_model=APIResponse[AIInsightResponse])
async def generate_ai_insight(
    payload: AIInsightRequest,
    db: Session = Depends(get_db)
):
    # Parse date boundaries from period
    start_date: Optional[date] = None
    end_date: Optional[date] = None

    today = date.today()
    if payload.period == "this_month":
        start_date = date(today.year, today.month, 1)
        end_date = today
    elif payload.period == "last_3_months":
        start_date = today - timedelta(days=90)
        end_date = today
    elif payload.period == "last_6_months":
        start_date = today - timedelta(days=180)
        end_date = today
    elif payload.period == "all_time":
        start_date = None
        end_date = None

    if payload.start_date:
        try:
            start_date = datetime.strptime(payload.start_date, "%Y-%m-%d").date()
        except ValueError:
            pass
    if payload.end_date:
        try:
            end_date = datetime.strptime(payload.end_date, "%Y-%m-%d").date()
        except ValueError:
            pass

    # Collect data context
    kpis = AnalyticsService.get_summary_kpis(db, start_date, end_date)
    top_prods = AnalyticsService.get_sales_by_product(db, start_date, end_date, limit=5)
    categories = AnalyticsService.get_sales_by_category(db, start_date, end_date)
    regions = AnalyticsService.get_sales_by_region(db, start_date, end_date)

    low_stock_prods = [
        {"name": p.name, "stock": p.stock}
        for p in db.query(Product).filter(Product.stock < 20).all()
    ]

    context = {
        "kpis": kpis.model_dump(),
        "top_products": [p.model_dump() for p in top_prods],
        "categories": [c.model_dump() for c in categories],
        "regions": [r.model_dump() for r in regions],
        "low_stock_products": low_stock_prods,
    }

    provider = get_ai_provider()
    summary_text = await provider.generate_insight(context)

    # Detect anomalies and generate recommendations
    anomalies = AnomalyDetector.detect_anomalies(db, start_date, end_date)
    recommendations = GroundedAIEngine.generate_recommendations(context)

    response_data = AIInsightResponse(
        period=payload.period,
        summary_text=summary_text,
        generated_at=datetime.utcnow(),
        anomalies=anomalies[:4],
        recommendations=recommendations,
        key_metrics=context["kpis"]
    )

    return APIResponse(
        success=True,
        message="AI insights generated successfully",
        data=response_data
    )


@router.get("/forecast", response_model=APIResponse[ForecastResponse])
def get_revenue_forecast(db: Session = Depends(get_db)):
    forecast = SalesForecaster.forecast_next_month(db)
    return APIResponse(
        success=True,
        message="Machine learning revenue forecast generated",
        data=forecast
    )


@router.get("/anomalies", response_model=APIResponse[List[AnomalyItem]])
def get_anomalies(
    start_date: Optional[date] = Query(None),
    end_date: Optional[date] = Query(None),
    db: Session = Depends(get_db)
):
    anomalies = AnomalyDetector.detect_anomalies(db, start_date=start_date, end_date=end_date)
    return APIResponse(
        success=True,
        message="Anomalies detected",
        data=anomalies
    )


@router.get("/recommendations", response_model=APIResponse[List[RecommendationItem]])
def get_recommendations(db: Session = Depends(get_db)):
    kpis = AnalyticsService.get_summary_kpis(db)
    top_prods = AnalyticsService.get_sales_by_product(db, limit=3)
    low_stock = [{"name": p.name, "stock": p.stock} for p in db.query(Product).filter(Product.stock < 20).all()]
    context = {
        "kpis": kpis.model_dump(),
        "top_products": [p.model_dump() for p in top_prods],
        "low_stock_products": low_stock,
    }
    recs = GroundedAIEngine.generate_recommendations(context)
    return APIResponse(
        success=True,
        message="Actionable recommendations generated",
        data=recs
    )


@router.post("/chat", response_model=APIResponse[ChatMessageResponse])
async def chat_with_sales_ai(
    payload: ChatMessageRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    conversation_id = payload.conversation_id or ChatHistoryService.new_conversation_id()

    ai_reply, route, intent, context = await SalesChatbot.process_message(
        db=db,
        user_id=current_user.id,
        user_query=payload.message.strip(),
        conversation_id=conversation_id,
    )

    return APIResponse(
        success=True,
        message="Chat response generated",
        data=ChatMessageResponse(
            user_message=payload.message,
            ai_response=ai_reply,
            conversation_id=conversation_id,
            route=route,
            intent_detected=intent,
            data_context=context,
            timestamp=datetime.utcnow(),
        )
    )
