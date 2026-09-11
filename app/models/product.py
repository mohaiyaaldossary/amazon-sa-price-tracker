"""
Pydantic response models.

WHY MODELS?
- FastAPI uses them to VALIDATE what we return (a typo like price="abc"
  becomes an error instead of silently shipping bad data).
- They generate the Swagger / OpenAPI schema at /docs automatically.
- They give n8n a stable, documented contract to rely on.
"""

from __future__ import annotations

from pydantic import BaseModel, Field


class ProductResponse(BaseModel):
    """The successful payload returned by GET /product/{asin}."""

    asin: str = Field(..., description="The ASIN that was requested (normalised to upper-case).",
                      examples=["B09ZFD9CBB"])
    product: str = Field(..., description="Product title returned for the Amazon.sa listing.",
                         examples=["Sony WH-1000XM5 Wireless Headphones"])
    price: float = Field(..., description="Current price as a plain number (no symbols, no commas).",
                         examples=[1299.0])
    currency: str = Field(..., description="Currency code for the returned price.",
                          examples=["SAR"])
    source: str = Field(..., description="Where the data came from.", examples=["Amazon.sa"])
    url: str = Field(..., description="The Amazon.sa product URL returned by the provider.",
                     examples=["https://www.amazon.sa/dp/B09ZFD9CBB"])

    # Shown as the example response body in Swagger UI.
    model_config = {
        "json_schema_extra": {
            "example": {
                "asin": "B09ZFD9CBB",
                "product": "Sony WH-1000XM5",
                "price": 1299.0,
                "currency": "SAR",
                "source": "Amazon.sa",
                "url": "https://www.amazon.sa/dp/B09ZFD9CBB",
            }
        }
    }


class HealthResponse(BaseModel):
    """Returned by GET /health so uptime monitors have something to poll."""

    status: str = Field(default="ok", examples=["ok"])


class ErrorResponse(BaseModel):
    """Shape of every error body (documented in Swagger for each status code)."""

    error: str = Field(..., description="Short machine-readable error code.",
                       examples=["invalid_asin"])
    detail: str = Field(..., description="Human-readable explanation.",
                        examples=["'123' is not a valid 10-character Amazon ASIN."])
from pydantic import BaseModel


class TrackedProductCreate(BaseModel):
    user_id: int
    asin: str


class TrackedProductResponse(BaseModel):
    id: int
    user_id: int
    asin: str
    product_name: str
    current_price: float
    product_url: str