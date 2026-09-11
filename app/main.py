"""
Application entry point.

Run locally with:
    uvicorn app.main:app --reload

What this file does:
    1. Configure logging from LOG_LEVEL.
    2. Create the FastAPI app (this also builds the Swagger docs at /docs).
    3. Register the JSON error handlers.
    4. Mount the /product router.
    5. Expose GET /health for uptime checks.
"""

from __future__ import annotations
from fastapi.middleware.cors import CORSMiddleware
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.config import get_settings
from app.database import create_tables
from app.errors import register_exception_handlers
from app.models.product import HealthResponse
from app.routes.products import router as products_router
from app.routes.users import router as users_router

settings = get_settings()

# ``force=True`` overrides any logging config Uvicorn set up first, so our
# format and level always win.
logging.basicConfig(
    level=settings.log_level,
    format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
    force=True,
)
logger = logging.getLogger("price_tracker")


@asynccontextmanager
async def lifespan(_: FastAPI):
    """Runs once on startup (before ``yield``) and once on shutdown (after)."""
    logger.info(
        "Price Tracker API started (base_url=%s, timeout=%ss, proxy=%s, log_level=%s)",
        settings.amazon_base_url,
        settings.request_timeout,
        bool(settings.proxy_url),
        settings.log_level,
    )

    create_tables()

    yield

    logger.info("Price Tracker API shutting down")
    
app = FastAPI(
    title="Price Tracker API",
    version="1.0.0",
    lifespan=lifespan,
    description=(
        "Tracks Amazon.sa products and retrieves current product data through "
        "SerpApi. Users can register, manage tracked products, and check for "
        "price changes. The `/check-all-prices` endpoint is designed for an "
        "n8n workflow that sends email notifications when prices change."
    ),
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
# Turn our custom exceptions into JSON responses.
register_exception_handlers(app)

# All product routes live under the router.
app.include_router(products_router)
app.include_router(users_router)


@app.get("/health", response_model=HealthResponse, tags=["system"], summary="Liveness probe")
def health() -> HealthResponse:
    """Return ``{"status": "ok"}``. Used by monitors, Docker, and n8n sanity checks."""
    return HealthResponse(status="ok")
