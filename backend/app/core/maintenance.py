from contextlib import contextmanager
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse

from app.db.session import SessionLocal, get_db
from app.core.security import decode_access_token
from app.services.system_setting_service import SystemSettingService


@contextmanager
def _maintenance_db_session(app):
    """Middleware runs outside FastAPI's Depends() graph, so it must look up any
    get_db override itself (e.g. the test suite's SQLite session) instead of always
    opening a fresh connection against the real configured engine."""
    override = app.dependency_overrides.get(get_db)
    if override:
        gen = override()
        db = next(gen)
        try:
            yield db
        finally:
            try:
                next(gen)
            except StopIteration:
                pass
    else:
        db = SessionLocal()
        try:
            yield db
        finally:
            db.close()

# Explicit exceptions to the global maintenance lock, per SalesIQ's maintenance-mode spec:
# health checks, auth (so users can still log in/out/identify themselves), the admin
# maintenance-management endpoints themselves, and API docs.
EXEMPT_PATH_PREFIXES = (
    "/api/health",
    "/api/auth/login",
    "/api/auth/logout",
    "/api/auth/me",
    "/api/admin/maintenance",
    "/docs",
    "/redoc",
    "/openapi.json",
)


class MaintenanceMiddleware(BaseHTTPMiddleware):
    """Backend-enforced maintenance lock: when enabled, every non-exempt endpoint
    returns 503 for non-admin requests (including unauthenticated ones), regardless
    of what the frontend does -- the lock must not rely on the UI hiding features."""

    async def dispatch(self, request: Request, call_next):
        path = request.url.path
        if request.method == "OPTIONS" or any(path == p or path.startswith(p) for p in EXEMPT_PATH_PREFIXES):
            return await call_next(request)

        with _maintenance_db_session(request.app) as db:
            enabled = SystemSettingService.get_bool(db, "maintenance_mode", default=False)
            if not enabled:
                return await call_next(request)

            role = None
            auth_header = request.headers.get("authorization", "")
            if auth_header.lower().startswith("bearer "):
                payload = decode_access_token(auth_header[7:])
                if payload:
                    role = payload.get("role")

            if role == "admin":
                return await call_next(request)

            message = SystemSettingService.get_str(
                db, "maintenance_message",
                "SalesIQ is currently under maintenance. Please check back shortly.",
            )
            return JSONResponse(
                status_code=503,
                content={
                    "success": False,
                    "error": {"code": "MAINTENANCE_MODE", "message": message, "details": None},
                },
            )
