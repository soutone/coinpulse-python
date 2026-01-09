"""
CoinPulse API Client

Simple, typed Python wrapper for the CoinPulse crypto portfolio API.
"""

import requests
from typing import Optional
from datetime import datetime

from coinpulse.exceptions import (
    CoinPulseError,
    AuthenticationError,
    RateLimitError,
    NotFoundError,
    ValidationError,
)
from coinpulse.models import (
    Price,
    HistoricalPrice,
    BacktestResult,
    Portfolio,
    Holding,
    Alert,
    PerformanceMetrics,
)


class CoinPulse:
    """
    CoinPulse API Client

    Usage:
        client = CoinPulse(api_key="your-api-key")
        prices = client.get_prices(["bitcoin", "ethereum"])

    Args:
        api_key: Your CoinPulse API key
        base_url: API base URL (default: https://coinpulse.dev)
        timeout: Request timeout in seconds (default: 30)
    """

    DEFAULT_BASE_URL = "https://coinpulse.dev"

    def __init__(
        self,
        api_key: str,
        base_url: str = DEFAULT_BASE_URL,
        timeout: int = 30,
    ):
        self.api_key = api_key
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self._session = requests.Session()
        self._session.headers.update({"X-API-Key": api_key})

    def _request(
        self,
        method: str,
        endpoint: str,
        params: Optional[dict] = None,
        json: Optional[dict] = None,
    ) -> dict:
        """Make an API request"""
        # Add trailing slash only for collection endpoints (those ending with a resource name, not ID)
        # e.g., /portfolios/ but not /portfolios/1/holdings
        collection_endpoints = ["/portfolios", "/alerts"]
        if method in ("POST",) and endpoint in collection_endpoints:
            endpoint = endpoint + "/"
        url = f"{self.base_url}{endpoint}"

        try:
            response = self._session.request(
                method=method,
                url=url,
                params=params,
                json=json,
                timeout=self.timeout,
            )
        except requests.RequestException as e:
            raise CoinPulseError(f"Request failed: {e}")

        # Handle errors
        if response.status_code == 401:
            raise AuthenticationError("Invalid API key")
        elif response.status_code == 403:
            raise AuthenticationError("Access denied - check your subscription tier")
        elif response.status_code == 404:
            raise NotFoundError("Resource not found")
        elif response.status_code == 422:
            error_detail = response.json().get("detail", "Validation error")
            raise ValidationError(str(error_detail))
        elif response.status_code == 429:
            retry_after = response.headers.get("Retry-After")
            raise RateLimitError(
                "Rate limit exceeded",
                retry_after=int(retry_after) if retry_after else None,
            )
        elif response.status_code >= 400:
            try:
                error = response.json().get("error", response.text)
            except Exception:
                error = response.text
            raise CoinPulseError(error, status_code=response.status_code)

        return response.json()

    # ==================== PRICES ====================

    def get_prices(self, coin_ids: list[str]) -> list[Price]:
        """
        Get current prices for multiple coins

        Args:
            coin_ids: List of coin IDs (e.g., ["bitcoin", "ethereum"])

        Returns:
            List of Price objects

        Example:
            prices = client.get_prices(["bitcoin", "ethereum", "solana"])
            for p in prices:
                print(f"{p.coin_id}: ${p.price_usd:,.2f}")
        """
        data = self._request(
            "GET",
            "/prices/current",
            params={"coin_ids": ",".join(coin_ids)},
        )

        return [
            Price(
                coin_id=p["coin_id"],
                price_usd=p["price_usd"],
                market_cap=p.get("market_cap"),
                volume_24h=p.get("volume_24h"),
                price_change_24h=p.get("percent_change_24h"),
                last_updated=datetime.fromisoformat(p["timestamp"])
                if p.get("timestamp")
                else None,
            )
            for p in data
        ]

    def get_price(self, coin_id: str) -> Price:
        """
        Get current price for a single coin

        Args:
            coin_id: Coin ID (e.g., "bitcoin")

        Returns:
            Price object
        """
        prices = self.get_prices([coin_id])
        if not prices:
            raise NotFoundError(f"Coin not found: {coin_id}")
        return prices[0]

    def get_historical_prices(
        self,
        coin_id: str,
        days: int = 30,
    ) -> list[HistoricalPrice]:
        """
        Get historical prices for a coin

        Args:
            coin_id: Coin ID (e.g., "bitcoin")
            days: Number of days of history (default: 30, max: 365)

        Returns:
            List of HistoricalPrice objects
        """
        data = self._request(
            "GET",
            f"/prices/historical/{coin_id}",
            params={"days": days},
        )

        return [
            HistoricalPrice(
                coin_id=coin_id,
                price_usd=p["price_usd"],
                timestamp=datetime.fromisoformat(p["timestamp"]),
            )
            for p in data.get("prices", [])
        ]

    def backtest(
        self,
        coin_id: str,
        start_date: str,
        end_date: str,
        initial_investment: float = 1000.0,
    ) -> BacktestResult:
        """
        Run a backtest for a coin over a date range

        Args:
            coin_id: Coin ID (e.g., "bitcoin")
            start_date: Start date (YYYY-MM-DD)
            end_date: End date (YYYY-MM-DD)
            initial_investment: Initial investment amount (default: 1000)

        Returns:
            BacktestResult object

        Example:
            result = client.backtest("bitcoin", "2024-01-01", "2024-12-31")
            print(f"Return: {result.price_change_percent:.1f}%")
        """
        data = self._request(
            "POST",
            f"/prices/backtest/{coin_id}",
            json={
                "start_date": start_date,
                "end_date": end_date,
                "initial_investment": initial_investment,
            },
        )

        return BacktestResult(
            coin_id=coin_id,
            start_date=start_date,
            end_date=end_date,
            start_price=data.get("start_price", 0),
            end_price=data.get("end_price", 0),
            price_change_percent=data.get("price_change_percent", 0),
            high_price=data.get("high_price", 0),
            low_price=data.get("low_price", 0),
            volatility=data.get("volatility"),
        )

    def get_supported_coins(self) -> list[str]:
        """
        Get list of supported coin IDs

        Returns:
            List of coin ID strings
        """
        data = self._request("GET", "/prices/supported-coins")
        return data.get("supported_coins", [])

    # ==================== PORTFOLIOS ====================

    def create_portfolio(
        self,
        name: str,
        description: Optional[str] = None,
    ) -> Portfolio:
        """
        Create a new portfolio

        Args:
            name: Portfolio name
            description: Optional description

        Returns:
            Portfolio object
        """
        data = self._request(
            "POST",
            "/portfolios",
            json={"name": name, "description": description},
        )

        return Portfolio(
            id=data["id"],
            name=data["name"],
            description=data.get("description"),
            created_at=data.get("created_at"),
        )

    def get_portfolios(
        self,
        limit: int = 100,
        offset: int = 0,
    ) -> list[Portfolio]:
        """
        Get all portfolios

        Args:
            limit: Max results (default: 100)
            offset: Skip results (default: 0)

        Returns:
            List of Portfolio objects
        """
        data = self._request(
            "GET",
            "/portfolios",
            params={"limit": limit, "offset": offset},
        )

        return [
            Portfolio(
                id=p["id"],
                name=p["name"],
                description=p.get("description"),
                created_at=p.get("created_at"),
            )
            for p in data
        ]

    def get_portfolio(self, portfolio_id: int) -> Portfolio:
        """
        Get a specific portfolio with calculated values

        Args:
            portfolio_id: Portfolio ID

        Returns:
            Portfolio object with holdings and calculated values
        """
        data = self._request("GET", f"/portfolios/{portfolio_id}")

        # Parse holdings if present
        holdings = None
        if "holdings" in data:
            holdings = [
                Holding(
                    id=0,  # Not returned in this endpoint
                    coin_id=h["coin_id"],
                    amount=h["amount"],
                    purchase_price=h.get("average_buy_price", 0),
                    purchase_date="",
                    current_price=h.get("current_price"),
                    current_value=h.get("current_value"),
                    profit_loss=h.get("profit_loss"),
                    profit_loss_percent=h.get("profit_loss_percent"),
                )
                for h in data["holdings"]
            ]

        return Portfolio(
            id=data.get("portfolio_id", data.get("id")),
            name=data.get("portfolio_name", data.get("name")),
            description=None,
            created_at=data.get("created_at"),
            holdings=holdings,
            total_value=data.get("total_current_value"),
            total_profit_loss=data.get("total_profit_loss"),
        )

    def delete_portfolio(self, portfolio_id: int) -> None:
        """Delete a portfolio"""
        self._request("DELETE", f"/portfolios/{portfolio_id}")

    # ==================== HOLDINGS ====================

    def add_holding(
        self,
        portfolio_id: int,
        coin_id: str,
        symbol: str,
        amount: float,
        average_buy_price: float,
        notes: Optional[str] = None,
    ) -> Holding:
        """
        Add a holding to a portfolio

        Args:
            portfolio_id: Portfolio ID
            coin_id: Coin ID (e.g., "bitcoin")
            symbol: Coin symbol (e.g., "btc")
            amount: Amount of coins
            average_buy_price: Average price per coin at purchase
            notes: Optional notes

        Returns:
            Holding object
        """
        payload = {
            "coin_id": coin_id,
            "symbol": symbol,
            "amount": amount,
            "average_buy_price": average_buy_price,
        }
        if notes:
            payload["notes"] = notes

        data = self._request(
            "POST",
            f"/portfolios/{portfolio_id}/holdings",
            json=payload,
        )

        return Holding(
            id=data["id"],
            coin_id=data["coin_id"],
            amount=data["amount"],
            purchase_price=data.get("average_buy_price", average_buy_price),
            purchase_date="",
        )

    def get_holdings(self, portfolio_id: int) -> list[Holding]:
        """
        Get all holdings in a portfolio

        Args:
            portfolio_id: Portfolio ID

        Returns:
            List of Holding objects with current values
        """
        data = self._request("GET", f"/portfolios/{portfolio_id}/holdings")

        return [
            Holding(
                id=h["id"],
                coin_id=h["coin_id"],
                amount=h["amount"],
                purchase_price=h["purchase_price"],
                purchase_date=h.get("purchase_date", ""),
                current_price=h.get("current_price"),
                current_value=h.get("current_value"),
                profit_loss=h.get("profit_loss"),
                profit_loss_percent=h.get("profit_loss_percent"),
            )
            for h in data
        ]

    def delete_holding(self, portfolio_id: int, holding_id: int) -> None:
        """Delete a holding from a portfolio"""
        self._request("DELETE", f"/portfolios/{portfolio_id}/holdings/{holding_id}")

    def get_performance(self, portfolio_id: int) -> PerformanceMetrics:
        """
        Get portfolio performance metrics

        Args:
            portfolio_id: Portfolio ID

        Returns:
            PerformanceMetrics object
        """
        data = self._request("GET", f"/portfolios/{portfolio_id}/performance")

        return PerformanceMetrics(
            total_value=data.get("total_value", 0),
            total_invested=data.get("total_invested", 0),
            total_profit_loss=data.get("total_profit_loss", 0),
            total_profit_loss_percent=data.get("total_profit_loss_percent", 0),
            best_performer=data.get("best_performer"),
            worst_performer=data.get("worst_performer"),
        )

    # ==================== ALERTS ====================

    def create_alert(
        self,
        coin_id: str,
        target_price: float,
        condition: str,
        notification_method: str = "webhook",
        webhook_url: Optional[str] = None,
        email: Optional[str] = None,
    ) -> Alert:
        """
        Create a price alert (PRO tier required)

        Args:
            coin_id: Coin ID (e.g., "bitcoin")
            target_price: Target price in USD
            condition: "above" or "below"
            notification_method: "webhook" or "email"
            webhook_url: Webhook URL (if notification_method is "webhook")
            email: Email address (if notification_method is "email")

        Returns:
            Alert object

        Example:
            alert = client.create_alert(
                coin_id="bitcoin",
                target_price=100000,
                condition="above",
                notification_method="webhook",
                webhook_url="https://your-webhook.com/alert"
            )
        """
        payload = {
            "coin_id": coin_id,
            "target_price": target_price,
            "condition": condition,
            "notification_method": notification_method,
        }
        if webhook_url:
            payload["webhook_url"] = webhook_url
        if email:
            payload["email"] = email

        data = self._request("POST", "/alerts", json=payload)

        return Alert(
            id=data["id"],
            coin_id=data["coin_id"],
            target_price=data["target_price"],
            condition=data["condition"],
            is_active=data.get("is_active", True),
            notification_method=data["notification_method"],
            webhook_url=data.get("webhook_url"),
            email=data.get("email"),
            created_at=data.get("created_at"),
        )

    def get_alerts(
        self,
        limit: int = 100,
        offset: int = 0,
    ) -> list[Alert]:
        """
        Get all alerts (PRO tier required)

        Returns:
            List of Alert objects
        """
        data = self._request(
            "GET",
            "/alerts",
            params={"limit": limit, "offset": offset},
        )

        return [
            Alert(
                id=a["id"],
                coin_id=a["coin_id"],
                target_price=a["target_price"],
                condition=a["condition"],
                is_active=a.get("is_active", True),
                notification_method=a["notification_method"],
                webhook_url=a.get("webhook_url"),
                email=a.get("email"),
                created_at=a.get("created_at"),
                triggered_at=a.get("triggered_at"),
            )
            for a in data
        ]

    def get_alert(self, alert_id: int) -> Alert:
        """Get a specific alert"""
        data = self._request("GET", f"/alerts/{alert_id}")

        return Alert(
            id=data["id"],
            coin_id=data["coin_id"],
            target_price=data["target_price"],
            condition=data["condition"],
            is_active=data.get("is_active", True),
            notification_method=data["notification_method"],
            webhook_url=data.get("webhook_url"),
            email=data.get("email"),
            created_at=data.get("created_at"),
            triggered_at=data.get("triggered_at"),
        )

    def toggle_alert(self, alert_id: int) -> Alert:
        """Toggle an alert on/off"""
        data = self._request("POST", f"/alerts/{alert_id}/toggle")

        return Alert(
            id=data["id"],
            coin_id=data["coin_id"],
            target_price=data["target_price"],
            condition=data["condition"],
            is_active=data.get("is_active", True),
            notification_method=data["notification_method"],
            webhook_url=data.get("webhook_url"),
            email=data.get("email"),
        )

    def delete_alert(self, alert_id: int) -> None:
        """Delete an alert"""
        self._request("DELETE", f"/alerts/{alert_id}")
