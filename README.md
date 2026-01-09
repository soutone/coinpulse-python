# coinpulse-python

Simple Python SDK for the [CoinPulse](https://coinpulse.dev) crypto portfolio API.

No OAuth, no complex setup. Just prices and portfolios.

## Install

```bash
pip install coinpulse
```

## Quick Start

```python
from coinpulse import CoinPulse

# Get your free API key at https://coinpulse.dev
client = CoinPulse(api_key="your-api-key")

# Get current prices
prices = client.get_prices(["bitcoin", "ethereum", "solana"])
for p in prices:
    print(f"{p.coin_id}: ${p.price_usd:,.2f}")

# bitcoin: $91,187.00
# ethereum: $3,245.00
# solana: $187.50
```

## Features

### Prices

```python
# Current prices for multiple coins
prices = client.get_prices(["bitcoin", "ethereum"])

# Single coin
btc = client.get_price("bitcoin")
print(f"BTC: ${btc.price_usd:,.2f}")

# Historical prices (up to 365 days)
history = client.get_historical_prices("bitcoin", days=30)
for h in history:
    print(f"{h.timestamp}: ${h.price_usd:,.2f}")

# Backtesting
result = client.backtest(
    coin_id="bitcoin",
    start_date="2024-01-01",
    end_date="2024-12-31",
    initial_investment=1000
)
print(f"Return: {result.price_change_percent:.1f}%")

# List supported coins
coins = client.get_supported_coins()
# ['bitcoin', 'ethereum', 'solana', ...]
```

### Portfolios

```python
# Create a portfolio
portfolio = client.create_portfolio(name="My Crypto")

# Add holdings
client.add_holding(
    portfolio_id=portfolio.id,
    coin_id="bitcoin",
    symbol="btc",
    amount=0.5,
    average_buy_price=45000
)

client.add_holding(
    portfolio_id=portfolio.id,
    coin_id="ethereum",
    symbol="eth",
    amount=5.0,
    average_buy_price=2500
)

# Get portfolio with current values
details = client.get_portfolio(portfolio.id)
print(f"Total value: ${details.total_value:,.2f}")
print(f"Total P/L: ${details.total_profit_loss:,.2f}")

for h in details.holdings:
    print(f"{h.coin_id}: {h.amount} coins")
    print(f"  Bought at: ${h.purchase_price:,.2f}")
    print(f"  Now worth: ${h.current_value:,.2f}")
    print(f"  P/L: {h.profit_loss_percent:+.1f}%")
```

### Price Alerts (PRO tier)

```python
# Create an alert
alert = client.create_alert(
    coin_id="bitcoin",
    target_price=100000,
    condition="above",
    notification_method="webhook",
    webhook_url="https://your-webhook.com/alert"
)

# List alerts
alerts = client.get_alerts()

# Toggle on/off
client.toggle_alert(alert.id)

# Delete
client.delete_alert(alert.id)
```

## Pricing

| Tier | Price | Requests/hr | Features |
|------|-------|-------------|----------|
| Free | $0 | 25 | Prices, portfolios, historical |
| Starter | $15/mo | 500 | All features, higher limits |
| Pro | $49/mo | 2,500 | + Price alerts, backtesting |
| Enterprise | $149/mo | 10,000 | + Priority support |

Get your API key at [coinpulse.dev](https://coinpulse.dev)

## Error Handling

```python
from coinpulse import (
    CoinPulse,
    AuthenticationError,
    RateLimitError,
    NotFoundError,
)

client = CoinPulse(api_key="your-key")

try:
    prices = client.get_prices(["bitcoin"])
except AuthenticationError:
    print("Invalid API key")
except RateLimitError as e:
    print(f"Rate limited. Retry after: {e.retry_after}s")
except NotFoundError:
    print("Coin not found")
```

## Type Hints

Everything is typed. Works great with your IDE:

```python
from coinpulse import CoinPulse
from coinpulse.models import Price, Portfolio, Holding

client = CoinPulse(api_key="...")
prices: list[Price] = client.get_prices(["bitcoin"])
```

## Configuration

```python
client = CoinPulse(
    api_key="your-key",
    base_url="https://coinpulse.dev",  # default
    timeout=30,  # seconds
)
```

## License

MIT

## Links

- API Docs: [coinpulse.dev/docs](https://coinpulse.dev/docs)
- Issues: [github.com/soutone/coinpulse-python/issues](https://github.com/soutone/coinpulse-python/issues)
