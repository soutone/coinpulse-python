"""
CoinPulse Python SDK - Simple crypto portfolio tracking API

Usage:
    from coinpulse import CoinPulse

    client = CoinPulse(api_key="your-api-key")
    prices = client.get_prices(["bitcoin", "ethereum"])
"""

from coinpulse.client import CoinPulse
from coinpulse.exceptions import (
    CoinPulseError,
    AuthenticationError,
    RateLimitError,
    NotFoundError,
    ValidationError,
)

__version__ = "0.1.0"
__all__ = [
    "CoinPulse",
    "CoinPulseError",
    "AuthenticationError",
    "RateLimitError",
    "NotFoundError",
    "ValidationError",
]
