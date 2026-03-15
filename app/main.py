import uuid

import structlog
from fastapi import FastAPI, Request
from fastapi.responses import ORJSONResponse

from app.api.v1.routes import router as v1_router
from app.core.config import get_settings
from app.core.logging import configure_logging

settings = get_settings()
configure_logging(settings.log_level)
logger = structlog.get_logger(__name__)

app = FastAPI(title=settings.app_name, default_response_class=ORJSONResponse)
app.include_router(v1_router)


@app.middleware("http")
async def add_request_context(request: Request, call_next):
    request_id = request.headers.get("x-request-id", str(uuid.uuid4()))
    logger.info(
        "request.started", path=request.url.path, method=request.method, request_id=request_id
    )
    response = await call_next(request)
    response.headers["x-request-id"] = request_id
    logger.info(
        "request.completed",
        path=request.url.path,
        status_code=response.status_code,
        request_id=request_id,
    )
    return response


@app.get("/healthz")
def healthz_root():
    return {"status": "ok"}


@app.get("/readyz")
def readyz_root():
    return {"status": "ready", "service": app.title}
