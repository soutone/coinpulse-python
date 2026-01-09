"""Data models for CoinPulse SDK responses"""

from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class Price:
    """Current price for a coin"""

    coin_id: str
    price_usd: float
    market_cap: Optional[float] = None
    volume_24h: Optional[float] = None
    price_change_24h: Optional[float] = None
    last_updated: Optional[datetime] = None


@dataclass
class HistoricalPrice:
    """Historical price point"""

    coin_id: str
    price_usd: float
    timestamp: datetime


@dataclass
class BacktestResult:
    """Backtesting result for a coin"""

    coin_id: str
    start_date: str
    end_date: str
    start_price: float
    end_price: float
    price_change_percent: float
    high_price: float
    low_price: float
    volatility: Optional[float] = None


@dataclass
class Holding:
    """A crypto holding in a portfolio"""

    id: int
    coin_id: str
    amount: float
    purchase_price: float
    purchase_date: str
    current_price: Optional[float] = None
    current_value: Optional[float] = None
    profit_loss: Optional[float] = None
    profit_loss_percent: Optional[float] = None


@dataclass
class Portfolio:
    """A crypto portfolio"""

    id: int
    name: str
    description: Optional[str] = None
    created_at: Optional[str] = None
    holdings: Optional[list[Holding]] = None
    total_value: Optional[float] = None
    total_profit_loss: Optional[float] = None


@dataclass
class Alert:
    """A price alert"""

    id: int
    coin_id: str
    target_price: float
    condition: str  # "above" or "below"
    is_active: bool
    notification_method: str
    webhook_url: Optional[str] = None
    email: Optional[str] = None
    created_at: Optional[str] = None
    triggered_at: Optional[str] = None


@dataclass
class PerformanceMetrics:
    """Portfolio performance metrics"""

    total_value: float
    total_invested: float
    total_profit_loss: float
    total_profit_loss_percent: float
    best_performer: Optional[str] = None
    worst_performer: Optional[str] = None
