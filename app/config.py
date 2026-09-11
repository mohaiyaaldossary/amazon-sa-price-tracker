"""
Central configuration.

WHY A SEPARATE FILE?
Every "magic value" (timeouts, headers, URLs) lives here instead of being
scattered across the code. That makes the behaviour easy to tune from a
``.env`` file WITHOUT editing Python, and keeps secrets out of the source.

HOW IT WORKS
1. ``load_dotenv()`` reads a local ``.env`` file (if present) and puts the
   keys into the process environment.
2. ``Settings`` then reads those values with ``os.getenv(name, default)`` so
   the app still runs even when nothing is configured.
3. ``get_settings()`` is cached, so the object is built once and reused.
"""

from __future__ import annotations

import os
from functools import lru_cache

from dotenv import load_dotenv

# Load .env into os.environ. Safe to call if the file does not exist.
load_dotenv()

# A believable desktop-Chrome User-Agent. Amazon is much more likely to serve
# a normal product page to a "browser" than to an obvious script.
_DEFAULT_USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36"
)


class Settings:
    """Typed view over the environment variables this service understands."""

    def __init__(self) -> None:
        # Base site. rstrip("/") so we never build ".../dp//B0..." by accident.
        self.amazon_base_url: str = os.getenv(
            "AMAZON_BASE_URL", "https://www.amazon.sa"
        ).rstrip("/")

        # Seconds before an Amazon request is considered "timed out" (-> 504).
        self.request_timeout: float = float(os.getenv("REQUEST_TIMEOUT", "15"))

        self.user_agent: str = os.getenv("USER_AGENT", _DEFAULT_USER_AGENT)
        self.accept_language: str = os.getenv(
            "ACCEPT_LANGUAGE", "en-SA,en;q=0.9,ar;q=0.8"
        )

        # Currency to report when we cannot detect one from the page.
        self.default_currency: str = os.getenv("DEFAULT_CURRENCY", "SAR")

        # Free-text label returned in the "source" field of the response.
        self.source_name: str = os.getenv("SOURCE_NAME", "Amazon.sa")

        # Optional outbound proxy. ``None`` (not "") means "no proxy".
        self.proxy_url: str | None = os.getenv("PROXY_URL") or None

        # SerpApi key used to retrieve Amazon.sa product data.
        self.serpapi_key: str | None = os.getenv("SERPAPI_KEY") or None

        self.log_level: str = os.getenv("LOG_LEVEL", "INFO").upper()

    @property
    def request_headers(self) -> dict[str, str]:
        """
        Headers a real Chrome browser sends for a top-level page navigation.
        Sending only a User-Agent is a classic bot signature; the extra
        ``Accept*`` and ``Sec-Fetch-*`` headers make the request look normal.
        """
        return {
            "User-Agent": self.user_agent,
            "Accept": (
                "text/html,application/xhtml+xml,application/xml;q=0.9,"
                "image/avif,image/webp,image/apng,*/*;q=0.8"
            ),
            "Accept-Language": self.accept_language,
            "Accept-Encoding": "gzip, deflate, br",
            "Connection": "keep-alive",
            "Upgrade-Insecure-Requests": "1",
            "Sec-Fetch-Dest": "document",
            "Sec-Fetch-Mode": "navigate",
            "Sec-Fetch-Site": "none",
            "Sec-Fetch-User": "?1",
            "Cache-Control": "max-age=0",
            "DNT": "1",
        }


@lru_cache
def get_settings() -> Settings:
    """Return a process-wide singleton ``Settings`` instance."""
    return Settings()
