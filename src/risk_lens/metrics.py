from __future__ import annotations

import math
import statistics
from collections.abc import Sequence


DEFAULT_TRADING_DAYS = 252


def daily_returns(prices: Sequence[float]) -> list[float]:
    """Return simple day-over-day returns from a price sequence."""
    returns: list[float] = []
    for previous, current in zip(prices, prices[1:]):
        if previous <= 0:
            raise ValueError("prices must be positive to calculate returns")
        returns.append((current / previous) - 1.0)
    return returns


def annualized_volatility(
    returns: Sequence[float], trading_days: int = DEFAULT_TRADING_DAYS
) -> float | None:
    """Annualized sample standard deviation of daily returns."""
    if len(returns) < 2:
        return None
    _validate_trading_days(trading_days)
    return statistics.stdev(returns) * math.sqrt(trading_days)


def rolling_volatility(
    returns: Sequence[float],
    window: int,
    trading_days: int = DEFAULT_TRADING_DAYS,
) -> list[float | None]:
    """Annualized sample volatility for each trailing return window."""
    if window <= 0:
        raise ValueError("window must be positive")
    _validate_trading_days(trading_days)

    values: list[float | None] = []
    for index in range(len(returns)):
        start = index - window + 1
        if start < 0:
            values.append(None)
            continue

        window_returns = returns[start : index + 1]
        if len(window_returns) < 2:
            values.append(None)
        else:
            values.append(statistics.stdev(window_returns) * math.sqrt(trading_days))
    return values


def max_drawdown(prices: Sequence[float]) -> float | None:
    """Worst peak-to-trough drawdown as a negative fraction."""
    if not prices:
        return None

    peak = prices[0]
    worst = 0.0
    for price in prices:
        if price <= 0:
            raise ValueError("prices must be positive to calculate drawdown")
        if price > peak:
            peak = price
        drawdown = (price / peak) - 1.0
        worst = min(worst, drawdown)
    return worst


def cagr(prices: Sequence[float], trading_days: int = DEFAULT_TRADING_DAYS) -> float | None:
    """Compound annual growth rate from the first to last price."""
    if len(prices) < 2:
        return None
    _validate_trading_days(trading_days)
    if any(price <= 0 for price in prices):
        raise ValueError("prices must be positive to calculate CAGR")
    periods = len(prices) - 1
    return (prices[-1] / prices[0]) ** (trading_days / periods) - 1.0


def sharpe_ratio(
    returns: Sequence[float],
    risk_free_rate: float = 0.0,
    trading_days: int = DEFAULT_TRADING_DAYS,
) -> float | None:
    """Annualized Sharpe ratio using an annual risk-free rate."""
    if len(returns) < 2:
        return None

    _validate_trading_days(trading_days)
    stddev = statistics.stdev(returns)
    if stddev == 0:
        return None

    daily_excess_mean = statistics.mean(returns) - (risk_free_rate / trading_days)
    return (daily_excess_mean / stddev) * math.sqrt(trading_days)


def sortino_ratio(
    returns: Sequence[float],
    risk_free_rate: float = 0.0,
    trading_days: int = DEFAULT_TRADING_DAYS,
) -> float | None:
    """Annualized Sortino ratio using downside deviation below the risk-free rate."""
    if len(returns) < 2:
        return None

    _validate_trading_days(trading_days)
    daily_target = risk_free_rate / trading_days
    downside_returns = [min(0.0, value - daily_target) for value in returns]
    downside_deviation = math.sqrt(
        sum(value * value for value in downside_returns) / len(downside_returns)
    )
    if downside_deviation == 0:
        return None

    daily_excess_mean = statistics.mean(returns) - daily_target
    return (daily_excess_mean / downside_deviation) * math.sqrt(trading_days)


def calmar_ratio(
    prices: Sequence[float], trading_days: int = DEFAULT_TRADING_DAYS
) -> float | None:
    """CAGR divided by absolute maximum drawdown."""
    growth = cagr(prices, trading_days)
    drawdown = max_drawdown(prices)
    if growth is None or drawdown is None or drawdown == 0:
        return None
    return growth / abs(drawdown)


def historical_var(
    returns: Sequence[float],
    confidence: float = 0.95,
) -> float | None:
    """Historical VaR as a positive loss fraction at the requested confidence."""
    if not returns:
        return None
    if not 0 < confidence < 1:
        raise ValueError("confidence must be between 0 and 1")

    threshold = _quantile(sorted(returns), 1.0 - confidence)
    return max(0.0, -threshold)


def cumulative_return(prices: Sequence[float]) -> float | None:
    if len(prices) < 2:
        return None
    if prices[0] <= 0:
        raise ValueError("prices must be positive to calculate cumulative return")
    return (prices[-1] / prices[0]) - 1.0


def mean_daily_return(returns: Sequence[float]) -> float | None:
    if not returns:
        return None
    return statistics.mean(returns)


def _quantile(sorted_values: Sequence[float], probability: float) -> float:
    if not sorted_values:
        raise ValueError("cannot calculate a quantile for an empty sequence")
    if len(sorted_values) == 1:
        return sorted_values[0]

    position = (len(sorted_values) - 1) * probability
    lower_index = math.floor(position)
    upper_index = math.ceil(position)
    if lower_index == upper_index:
        return sorted_values[lower_index]

    lower = sorted_values[lower_index]
    upper = sorted_values[upper_index]
    fraction = position - lower_index
    return lower + ((upper - lower) * fraction)


def _validate_trading_days(trading_days: int) -> None:
    if trading_days <= 0:
        raise ValueError("trading_days must be positive")
