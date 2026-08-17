import logging
from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.core.config import settings
from app.db.session import engine, Base
import app.models  # Ensure all SQLAlchemy models are registered
from app.core.maintenance import MaintenanceMiddleware

# Import routers
from app.api.auth import router as auth_router
from app.api.users import router as users_router
from app.api.products import router as products_router
from app.api.regions import router as regions_router
from app.api.sales import router as sales_router
from app.api.analytics import router as analytics_router
from app.api.ai import router as ai_router
from app.api.reports import router as reports_router
from app.api.notifications import router as notif_router
from app.api.health import router as health_router
from app.api.admin import router as admin_router

# Setup Logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger("SalesIQ")

# Schema is managed exclusively via Alembic migrations (see backend/alembic/versions).
# Run `alembic upgrade head` before starting the server.

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.PROJECT_VERSION,
    description="AI Sales Analytics Dashboard: An Intelligent, Data-Driven Business Intelligence System (CSE4104-7A-T02)",
    docs_url="/docs",
    redoc_url="/redoc",
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"] if settings.cors_origin_list == ["*"] else settings.cors_origin_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global maintenance-mode enforcement (backend-authoritative, not just a frontend screen)
app.add_middleware(MaintenanceMiddleware)


# Exception Handlers
@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "success": False,
            "error": {
                "code": "HTTP_ERROR",
                "message": exc.detail,
                "details": None,
            },
        },
    )


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    error_messages = []
    for err in exc.errors():
        loc = " -> ".join([str(x) for x in err.get("loc", [])])
        msg = err.get("msg", "Invalid value")
        error_messages.append(f"{loc}: {msg}")

    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "success": False,
            "error": {
                "code": "VALIDATION_ERROR",
                "message": "Validation failed on request payload",
                "details": error_messages,
            },
        },
    )


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.exception(f"Unhandled Exception: {str(exc)}")
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "success": False,
            "error": {
                "code": "INTERNAL_SERVER_ERROR",
                "message": "An unexpected error occurred. Please try again later.",
                "details": str(exc) if settings.ENVIRONMENT == "development" else None,
            },
        },
    )


# Mount API Routers under /api
app.include_router(health_router, prefix="/api")
app.include_router(auth_router, prefix="/api")
app.include_router(users_router, prefix="/api")
app.include_router(products_router, prefix="/api")
app.include_router(regions_router, prefix="/api")
app.include_router(sales_router, prefix="/api")
app.include_router(analytics_router, prefix="/api")
app.include_router(ai_router, prefix="/api")
app.include_router(reports_router, prefix="/api")
app.include_router(notif_router, prefix="/api")
app.include_router(admin_router, prefix="/api")


@app.get("/")
def root():
    return {
        "message": "Welcome to AI Sales Analytics Dashboard API (SalesIQ - CSE4104-7A-T02)",
        "docs": "/docs",
        "health": "/api/health",
    }
