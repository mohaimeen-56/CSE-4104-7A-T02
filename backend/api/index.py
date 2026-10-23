import sys
import os
from pathlib import Path

backend_dir = Path(__file__).resolve().parent.parent
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

try:
    from app.main import app as fastapi_app

    # ASGI wrapper to handle Vercel internal rewritten destination path routing
    async def app(scope, receive, send):
        if scope.get("type") == "http":
            headers = dict(scope.get("headers", []))
            matched = headers.get(b"x-matched-path")
            if matched:
                try:
                    orig_path = matched.decode("utf-8").split("?")[0]
                    if orig_path:
                        scope["path"] = orig_path
                except Exception:
                    pass
        await fastapi_app(scope, receive, send)

except Exception as exc:
    import traceback
    err_trace = traceback.format_exc()
    from fastapi import FastAPI
    from fastapi.responses import JSONResponse
    
    app = FastAPI(title="Diagnostic Fallback")

    @app.api_route("/{full_path:path}", methods=["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"])
    def diagnostic_handler(full_path: str):
        return JSONResponse(
            status_code=500,
            content={
                "success": False,
                "error": "FastAPI failed to initialize on Vercel",
                "details": str(exc),
                "traceback": err_trace,
                "sys_path": sys.path,
                "backend_exists": backend_dir.exists(),
                "backend_files": os.listdir(str(backend_dir)) if backend_dir.exists() else [],
            }
        )
