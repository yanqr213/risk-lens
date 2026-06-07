# API Reference

The public API is intentionally small. Functions operate on plain Python values and return floats, `None`, lists, or dictionaries.

## Loading Data

```python
from risk_lens import load_prices

points = load_prices("examples/prices.csv")
```

`load_prices(path)` returns a list of `PricePoint(symbol, date, close)` records.

## Full Report

```python
from risk_lens import analyze_points, load_prices

points = load_prices("examples/prices.csv")
report = analyze_points(
    points,
    risk_free_rate=0.02,
    trading_days=252,
    var_confidence=0.95,
    rolling_window=20,
)
```

`analyze_points` returns the same dictionary structure used by the CLI JSON output.

Parameters:

- `points`: iterable of `PricePoint` objects.
- `risk_free_rate`: annual risk-free rate, for example `0.02`.
- `trading_days`: positive annualization period count.
- `var_confidence`: historical VaR confidence between `0` and `1`.
- `rolling_window`: optional positive trailing return count.

## Metric Functions

```python
from risk_lens import (
    annualized_volatility,
    cagr,
    calmar_ratio,
    daily_returns,
    historical_var,
    max_drawdown,
    rolling_volatility,
    sharpe_ratio,
    sortino_ratio,
)

prices = [100.0, 101.5, 99.2, 103.1]
returns = daily_returns(prices)

annualized_volatility(returns)
cagr(prices)
max_drawdown(prices)
sharpe_ratio(returns, risk_free_rate=0.02)
sortino_ratio(returns, risk_free_rate=0.02)
calmar_ratio(prices)
historical_var(returns, confidence=0.95)
rolling_volatility(returns, window=2)
```

Return conventions:

- Metrics return `None` when not enough observations exist or the ratio is undefined.
- Drawdown is a negative fraction.
- Historical VaR is a positive loss fraction.
- Rolling volatility returns one value per return. Values before the first complete window are `None`.

## Exceptions

Functions raise `ValueError` for invalid data or parameters, such as non-positive prices, non-positive `trading_days`, invalid VaR confidence, or invalid rolling windows.
