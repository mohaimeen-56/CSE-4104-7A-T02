from app.schemas.common import APIResponse, PaginatedResponse, PaginationMeta, APIErrorResponse, ErrorDetail
from app.schemas.user import UserCreate, UserLogin, UserUpdate, UserResponse, Token, TokenPayload
from app.schemas.product import ProductCreate, ProductUpdate, ProductResponse
from app.schemas.region import RegionCreate, RegionUpdate, RegionResponse
from app.schemas.sale import SaleCreate, SaleUpdate, SaleResponse, CsvUploadResponse, CsvRowError
from app.schemas.analytics import (
    SummaryKPI,
    RevenueTrendItem,
    ProductSalesItem,
    CategorySalesItem,
    RegionSalesItem,
    TopProductItem,
    MonthlyComparisonItem,
    DashboardOverviewResponse,
)
from app.schemas.ai import (
    AIInsightRequest,
    AIInsightResponse,
    AnomalyItem,
    RecommendationItem,
    ForecastResponse,
    ChatMessageRequest,
    ChatMessageResponse,
)
from app.schemas.notification import NotificationCreate, NotificationResponse, NotificationUnreadCount

__all__ = [
    "APIResponse",
    "PaginatedResponse",
    "PaginationMeta",
    "APIErrorResponse",
    "ErrorDetail",
    "UserCreate",
    "UserLogin",
    "UserUpdate",
    "UserResponse",
    "Token",
    "TokenPayload",
    "ProductCreate",
    "ProductUpdate",
    "ProductResponse",
    "RegionCreate",
    "RegionUpdate",
    "RegionResponse",
    "SaleCreate",
    "SaleUpdate",
    "SaleResponse",
    "CsvUploadResponse",
    "CsvRowError",
    "SummaryKPI",
    "RevenueTrendItem",
    "ProductSalesItem",
    "CategorySalesItem",
    "RegionSalesItem",
    "TopProductItem",
    "MonthlyComparisonItem",
    "DashboardOverviewResponse",
    "AIInsightRequest",
    "AIInsightResponse",
    "AnomalyItem",
    "RecommendationItem",
    "ForecastResponse",
    "ChatMessageRequest",
    "ChatMessageResponse",
    "NotificationCreate",
    "NotificationResponse",
    "NotificationUnreadCount",
]
