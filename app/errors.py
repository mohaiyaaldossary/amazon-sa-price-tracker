"""
Error handling — one place that maps "something went wrong" to an HTTP status.

DESIGN
------
The product-data service (``services/amazon.py``) never imports FastAPI. Instead it
raises plain Python exceptions defined here. Each exception class carries:

  * ``status_code`` — the HTTP code the client should receive
  * ``code``        — a short machine-readable string ("invalid_asin", ...)
  * ``detail``      — a human-readable message

``register_exception_handlers(app)`` (called from ``main.py``) teaches FastAPI
how to turn any of these into a clean JSON response:

    { "error": "<code>", "detail": "<message>" }

This keeps the service layer framework-agnostic and easy to unit-test.
"""

from __future__ import annotations

import logging

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

logger = logging.getLogger(__name__)


class ProductAPIError(Exception):
    """Base class for every error this API knows how to report."""

    status_code: int = 500
    code: str = "internal_error"

    def __init__(self, detail: str | None = None) -> None:
        # Fall back to the subclass docstring so each error has a sane message.
        self.detail = detail or (self.__doc__ or "Unexpected error").strip()
        super().__init__(self.detail)


class InvalidASINError(ProductAPIError):
    """The provided ASIN is not a valid 10-character Amazon identifier."""

    status_code = 400
    code = "invalid_asin"


class ProductNotFoundError(ProductAPIError):
    """No product data could be found for this Amazon.sa ASIN."""

    status_code = 404
    code = "product_not_found"


class PriceUnavailableError(ProductAPIError):
    """Product data was returned, but no price was available."""

    status_code = 404
    code = "price_unavailable"


class AmazonRequestError(ProductAPIError):
    """The upstream product-data request failed or returned an unexpected response."""

    status_code = 502
    code = "amazon_request_failed"


class AmazonTimeoutError(ProductAPIError):
    """The upstream product-data request took too long and was aborted."""

    status_code = 504
    code = "amazon_timeout"


def register_exception_handlers(app: FastAPI) -> None:
    """Attach JSON error handlers to the FastAPI application."""

    @app.exception_handler(ProductAPIError)
    async def _handle_known(request: Request, exc: ProductAPIError) -> JSONResponse:
        # 4xx = client's fault (log at INFO), 5xx = our/upstream provider's fault (WARNING).
        log = logger.info if exc.status_code < 500 else logger.warning
        log("%s %s -> %s (%s): %s",
            request.method, request.url.path, exc.status_code, exc.code, exc.detail)
        return JSONResponse(
            status_code=exc.status_code,
            content={"error": exc.code, "detail": exc.detail},
        )

    @app.exception_handler(RequestValidationError)
    async def _handle_validation(
        request: Request, exc: RequestValidationError
    ) -> JSONResponse:
        # e.g. a path parameter that FastAPI itself rejects.
        return JSONResponse(
            status_code=422,
            content={"error": "validation_error", "detail": exc.errors()},
        )

    @app.exception_handler(Exception)
    async def _handle_unexpected(request: Request, exc: Exception) -> JSONResponse:
        # Never leak a stack trace to the caller; log it fully on our side.
        logger.exception("Unhandled error on %s %s", request.method, request.url.path)
        return JSONResponse(
            status_code=500,
            content={"error": "internal_error", "detail": "An unexpected error occurred."},
        )
