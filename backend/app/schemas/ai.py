from datetime import datetime
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field


class AIInsightRequest(BaseModel):
    period: str = Field(default="this_month", description="this_month, last_3_months, last_6_months, all_time, or YYYY-MM")
    start_date: Optional[str] = None
    end_date: Optional[str] = None


class AnomalyItem(BaseModel):
    id: str
    date: str
    title: str
    description: str
    metric: str
    actual_value: float
    expected_value: float
    deviation_pct: float
    severity: str  # "high", "medium", "low"
    type: str  # "spike", "drop", "stock"


class RecommendationItem(BaseModel):
    id: str
    category: str  # "inventory", "promotion", "regional", "pricing"
    title: str
    action: str
    impact: str
    priority: str  # "high", "medium", "low"


class AIInsightResponse(BaseModel):
    period: str
    summary_text: str
    generated_at: datetime
    anomalies: List[AnomalyItem]
    recommendations: List[RecommendationItem]
    key_metrics: Dict[str, Any]


class ForecastMonthItem(BaseModel):
    month: str
    predicted_revenue: float
    lower_bound: float
    upper_bound: float


class ForecastResponse(BaseModel):
    next_month: str
    predicted_revenue: float
    growth_estimate_pct: float
    historical_months: List[Dict[str, Any]]
    forecast_curve: List[ForecastMonthItem]
    model_name: str
    r2_score: Optional[float] = None
    status: str  # "confident", "insufficient_data", "provisional"
    message: str


class ChatMessageRequest(BaseModel):
    message: str = Field(..., min_length=1)
    conversation_id: Optional[str] = Field(None, description="Omit to start a new conversation")


class ChatMessageResponse(BaseModel):
    user_message: str
    ai_response: str
    conversation_id: str
    route: str  # 'conversation' | 'analytics'
    intent_detected: Optional[str] = None
    data_context: Optional[Dict[str, Any]] = None
    timestamp: datetime
