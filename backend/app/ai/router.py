"""
Intent / message router for the SalesIQ chatbot.

Splits every incoming message into one of two branches:
  - "conversation": small talk, greetings, thanks, identity questions, and requests to
    explain a concept/metric. Handled by the AI provider's persona, never touches the DB.
  - "analytics": a real question about the business's sales data. Routed to a specific,
    deterministic intent (best_product, region_performance, forecast, ...) whose data comes
    ONLY from safe AnalyticsService/ML calls -- the LLM is never allowed to decide what data
    to fetch or to invent figures, only to phrase results that were already computed.

This is intentionally rule-based (regex/keyword) rather than LLM-based: it must run even when
Gemini is unavailable, and it must be auditable/deterministic for a safety-critical routing
decision (never let the model silently "query" the database on its own).
"""
import re
import calendar
from dataclasses import dataclass, field
from datetime import date, timedelta
from typing import Optional, Tuple, Literal

ConversationKind = Literal[
    "greeting", "farewell", "thanks", "acknowledgement", "identity", "how_are_you", "definition", "other"
]
AnalyticsIntent = Literal[
    "best_product", "region_performance", "top_region", "category_growth", "worst_region",
    "total_revenue", "forecast", "anomalies", "peak_hours", "day_of_week", "recommendations", "general",
]

REGION_NAMES = ["dhaka", "khulna", "chittagong", "sylhet", "rajshahi"]

MONTH_NAME_MAP = {
    "january": 1, "february": 2, "march": 3, "april": 4, "may": 5, "june": 6,
    "july": 7, "august": 8, "september": 9, "october": 10, "november": 11, "december": 12,
}

GREETING_PATTERNS = [r"^\s*(hi|hello|hey|yo|hiya|hi there|hello there)\b", r"^\s*good (morning|afternoon|evening|night)\b"]
FAREWELL_PATTERNS = [r"^\s*(bye|goodbye|see you|see ya|farewell|take care)\b"]
THANKS_PATTERNS = [r"\b(thanks|thank you|thx|appreciate it|cheers)\b"]
ACK_PATTERNS = [r"^\s*(ok|okay|k|cool|nice|great|got it|understood|sounds good|alright|perfect)\s*[.!]?\s*$",
                r"that'?s (useful|helpful|great|cool|nice)"]
IDENTITY_PATTERNS = [r"\bwho are you\b", r"\bwhat can you (do|help)\b", r"\bwhat is this (dashboard|app|tool)\b",
                      r"^\s*(can you help me|help)\s*[?.!]?\s*$", r"\btell me what this dashboard does\b",
                      r"\bwhat do you do\b"]
HOW_ARE_YOU_PATTERNS = [r"\bhow are you\b", r"how'?s it going\b", r"\bhow do you do\b"]

DEFINITION_PATTERN = re.compile(r"^\s*(what is|what does|what'?s|explain|define|meaning of)\b", re.IGNORECASE)
TIME_SCOPE_WORDS = [
    "this month", "last month", "this week", "last week", "today", "yesterday", "this year", "last year",
    "between", "since", " to ", "q1", "q2", "q3", "q4", "quarter",
] + list(MONTH_NAME_MAP.keys())

FOLLOWUP_PATTERNS = [r"^\s*what about\b", r"^\s*and\b", r"^\s*how about\b", r"^\s*what of\b", r"^\s*what'?s\b.*\?$"]

ANALYTICS_INTENT_KEYWORDS: dict = {
    "forecast": [
        "forecast", "predict", "next month", "projection", "predicted revenue",
        "future sales", "future revenue", "will we make", "expected revenue",
        "anticipated", "upcoming month",
    ],
    "anomalies": [
        "anomaly", "anomalies", "unusual", "spike", "drop", "suspicious activity",
        "anything weird", "strange", "outlier", "abnormal", "irregularity",
        "unexpected", "odd pattern", "data issue",
    ],
    "peak_hours": [
        "peak hour", "busiest hour", "busiest time", "what time", "peak time",
        "rush hour", "most active hour", "when are sales highest", "hour of day",
        "time of day", "hourly sales",
    ],
    "day_of_week": [
        "day of week", "which day", "busiest day", "weekday", "weekend",
        "best day", "worst day", "day analysis", "weekly pattern",
        "what day", "day performance",
    ],
    "recommendations": [
        "recommend", "suggestion", "what should we do", "actionable", "advice",
        "improve sales", "boost sales", "increase revenue", "what can we do",
        "action items", "what do you suggest", "next steps", "strategy",
        "how to grow", "how can we improve",
    ],
    "best_product": [
        "best product", "top product", "best sales", "top sales", "highest selling",
        "best performing", "best selling", "most popular", "most sold", "top item",
        "which product", "what product", "product performance", "selling most",
        "most revenue product", "leading product", "number one product",
        "what sold the most", "what's selling", "what is selling",
    ],
    "category_growth": [
        "category", "categories", "fastest growing", "growing fastest",
        "which category", "product type", "product category", "what type of product",
        "best category", "top category", "category performance", "by category",
        "what kind of product",
    ],
    "worst_region": [
        "worst region", "lowest region", "least sales", "lowest sales",
        "underperforming", "weakest region", "poor region", "struggling region",
        "least revenue", "region doing badly", "region doing poorly",
    ],
    "total_revenue": [
        "total revenue", "total sales", "how much did we make", "aov", "average order",
        "total orders", "how many orders", "how many sales", "units sold",
        "revenue this", "revenue did we", "how much revenue", "revenue",
        "how are sales", "sales doing", "sales performance", "sales figures",
        "how did we do", "how is business", "overall sales", "overall revenue",
        "business performance", "how much have we", "how much money",
        "how much have we made", "what are our sales", "what is our revenue",
        "show me sales", "show me revenue", "sales numbers", "revenue numbers",
        "how are we doing", "how is it going", "sales report", "summary",
        "business overview", "kpi", "key metrics", "numbers",
        "earned", "generated", "made so far", "sales today", "sales this",
        "monthly sales", "yearly sales", "quarterly sales", "weekly sales",
    ],
}

METRIC_DEFINITION_KEYS = [
    "aov", "average order value", "revenue", "forecast", "anomaly", "anomalies", "dashboard",
    "category", "region", "data quality", "kpi", "aov mean",
]


@dataclass
class Classification:
    route: Literal["conversation", "analytics"]
    conversation_kind: Optional[ConversationKind] = None
    definition_term: Optional[str] = None
    analytics_intent: Optional[AnalyticsIntent] = None
    period: Optional[Tuple[date, date]] = None
    period_label: Optional[str] = None
    is_followup: bool = False


def extract_period(msg_lower: str, reference_year: int) -> Optional[Tuple[date, date]]:
    for name, num in MONTH_NAME_MAP.items():
        if name in msg_lower:
            start = date(reference_year, num, 1)
            end_day = calendar.monthrange(reference_year, num)[1]
            return start, date(reference_year, num, end_day)
    if "this month" in msg_lower:
        today = date.today()
        return date(today.year, today.month, 1), today
    if "last month" in msg_lower:
        today = date.today()
        first_this = date(today.year, today.month, 1)
        last_month_end = first_this - timedelta(days=1)
        return date(last_month_end.year, last_month_end.month, 1), last_month_end
    if "this year" in msg_lower:
        today = date.today()
        return date(today.year, 1, 1), today
    if "today" in msg_lower:
        today = date.today()
        return today, today
    if "yesterday" in msg_lower:
        y = date.today() - timedelta(days=1)
        return y, y
    return None


def _matches_any(patterns, msg: str) -> bool:
    return any(re.search(p, msg) for p in patterns)


def classify_message(message: str, reference_year: int, has_prior_analytics_intent: bool) -> Classification:
    msg = (message or "").strip().lower()
    if not msg:
        return Classification(route="conversation", conversation_kind="other")

    # 1. Definitional / explanatory questions ("what is X", "explain X") without a time/entity
    #    scope are conversation, not a live data query -- even if they mention "revenue"/"AOV".
    if DEFINITION_PATTERN.match(msg) and not any(w in msg for w in TIME_SCOPE_WORDS) and not any(r in msg for r in REGION_NAMES):
        term = next((k for k in METRIC_DEFINITION_KEYS if k in msg), None)
        return Classification(route="conversation", conversation_kind="definition", definition_term=term)

    # 2. Pure small talk
    if _matches_any(GREETING_PATTERNS, msg):
        return Classification(route="conversation", conversation_kind="greeting")
    if _matches_any(FAREWELL_PATTERNS, msg):
        return Classification(route="conversation", conversation_kind="farewell")
    if _matches_any(HOW_ARE_YOU_PATTERNS, msg):
        return Classification(route="conversation", conversation_kind="how_are_you")
    if _matches_any(IDENTITY_PATTERNS, msg):
        return Classification(route="conversation", conversation_kind="identity")
    if _matches_any(ACK_PATTERNS, msg):
        return Classification(route="conversation", conversation_kind="acknowledgement")
    if _matches_any(THANKS_PATTERNS, msg) and len(msg.split()) <= 6:
        return Classification(route="conversation", conversation_kind="thanks")

    # 3. Region growth/leadership questions that don't name a specific region
    #    ("Which region is growing fastest?") must resolve to top_region, not the more
    #    generic category_growth bucket, even though they share words like "fastest".
    if "region" in msg and not any(r in msg for r in REGION_NAMES):
        if any(w in msg for w in ["fastest", "growing", "leading", "top region", "best region", "which region"]):
            period = extract_period(msg, reference_year)
            return Classification(route="analytics", analytics_intent="top_region", period=period)

    # 4. Direct analytics keyword match (checked in priority order: most specific first)
    for intent, keywords in ANALYTICS_INTENT_KEYWORDS.items():
        if any(kw in msg for kw in keywords):
            period = extract_period(msg, reference_year)
            return Classification(route="analytics", analytics_intent=intent, period=period)

    matched_region = next((r for r in REGION_NAMES if r in msg), None)
    if matched_region:
        period = extract_period(msg, reference_year)
        return Classification(route="analytics", analytics_intent="region_performance", period=period)

    # 5. Follow-up continuation of a prior analytics turn ("What about February?")
    period = extract_period(msg, reference_year)
    if has_prior_analytics_intent and (period is not None or _matches_any(FOLLOWUP_PATTERNS, msg)):
        return Classification(route="analytics", analytics_intent=None, period=period, is_followup=True)

    # 6. If the message contains any period word (month/year/time scope) it is almost certainly
    #    a business data question even if we didn't match a specific intent keyword.
    period = extract_period(msg, reference_year)
    if period is not None:
        return Classification(route="analytics", analytics_intent="general", period=period)

    # 7. Final fallback: route to analytics/general with KPI context so Gemini can attempt a
    #    meaningful answer. This is better than a dead-end "I can't help with that" conversation reply.
    return Classification(route="analytics", analytics_intent="general")
