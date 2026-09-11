"""
Amazon product service using SerpApi.

Gets product information from Amazon.sa through SerpApi
instead of directly scraping Amazon HTML.
"""

from __future__ import annotations

import logging
import re

import requests

from app.config import get_settings
from app.errors import (
    AmazonRequestError,
    AmazonTimeoutError,
    InvalidASINError,
    ProductNotFoundError,
)

logger = logging.getLogger(__name__)

SERPAPI_URL = "https://serpapi.com/search"


def get_product(asin: str) -> dict:
    """
    Get product information from Amazon.sa using SerpApi.

    Returns:
        {
            "asin": "...",
            "product": "...",
            "price": ...,
            "currency": "SAR",
            "source": "Amazon.sa",
            "url": "..."
        }
    """

    if not re.fullmatch(r"[A-Za-z0-9]{10}", asin):
        raise InvalidASINError(
            f"{asin} is not a valid 10-character Amazon ASIN."
        )

    settings = get_settings()

    if not settings.serpapi_key:
        raise AmazonRequestError(
            "SERPAPI_KEY is missing from the .env file."
        )

    params = {
        "engine": "amazon_product",
        "asin": asin,
        "amazon_domain": "amazon.sa",
        "api_key": settings.serpapi_key,
    }

    try:
        response = requests.get(
            SERPAPI_URL,
            params=params,
            timeout=settings.request_timeout,
        )

    except requests.Timeout as exc:
        raise AmazonTimeoutError(
            "SerpApi request timed out."
        ) from exc

    except requests.RequestException as exc:
        raise AmazonRequestError(
            f"SerpApi request failed: {exc}"
        ) from exc

    if response.status_code != 200:
        raise AmazonRequestError(
            f"SerpApi returned status code {response.status_code}."
        )

    data = response.json()

    if "error" in data:
        raise AmazonRequestError(
            f"SerpApi error: {data['error']}"
        )

    product = data.get("product_results")

    if not product:
        raise ProductNotFoundError(
            "Product information was not returned by SerpApi."
        )

    product_name = product.get("title")

    if not product_name:
        raise ProductNotFoundError(
            "Product title was not found."
        )

    price = product.get("extracted_price")

    if price is None:
        prices = data.get("prices", [])

        if prices:
            price = prices[0].get("extracted_price")

    if price is None:
        raise ProductNotFoundError(
            "Product price was not found."
        )

    product_url = product.get(
        "link",
        f"https://www.amazon.sa/dp/{asin}",
    )

    logger.info(
        "Product found through SerpApi: %s | Price: %s",
        product_name,
        price,
    )

    return {
        "asin": asin,
        "product": product_name,
        "price": float(price),
        "currency": "SAR",
        "source": "Amazon.sa",
        "url": product_url,
    }