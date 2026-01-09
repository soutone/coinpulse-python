"""Custom exceptions for CoinPulse SDK"""


class CoinPulseError(Exception):
    """Base exception for CoinPulse SDK"""

    def __init__(self, message: str, status_code: int | None = None):
        self.message = message
        self.status_code = status_code
        super().__init__(message)


class AuthenticationError(CoinPulseError):
    """Raised when API key is invalid or missing"""

    pass


class RateLimitError(CoinPulseError):
    """Raised when rate limit is exceeded"""

    def __init__(self, message: str, retry_after: int | None = None):
        super().__init__(message, status_code=429)
        self.retry_after = retry_after


class NotFoundError(CoinPulseError):
    """Raised when requested resource doesn't exist"""

    pass


class ValidationError(CoinPulseError):
    """Raised when request data is invalid"""

    pass
