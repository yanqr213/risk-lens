from __future__ import annotations

from collections.abc import Iterable

from .io import PricePoint, group_prices
from .metrics import (
    DEFAULT_TRADING_DAYS,
    annualized_volatility,
    cagr,
    calmar_ratio,
    cumulative_return,
    daily_returns,
    historical_var,
    max_drawdown,
    mean_daily_return,
    rolling_volatility,
    sharpe_ratio,
    sortino_ratio,
)


def analyze_points(
    points: Iterable[PricePoint],
    risk_free_rate: float = 0.0,
    trading_days: int = DEFAULT_TRADING_DAYS,
    var_confidence: float = 0.95,
    rolling_window: int | None = None,
) -> dict[str, object]:
    if trading_days <= 0:
        raise ValueError("trading_days must be positive")
    if not 0 < var_confidence < 1:
        raise ValueError("var_confidence must be between 0 and 1")
    if rolling_window is not None and rolling_window <= 0:
        raise ValueError("rolling_window must be positive")

    grouped = group_prices(points)
    series_results = []

    for symbol in sorted(grouped):
        series = grouped[symbol]
        closes = [point.close for point in series]
        returns = daily_returns(closes)
        rolling_values = (
            rolling_volatility(returns, rolling_window, trading_days)
            if rolling_window is not None
            else None
        )

        series_results.append(
            {
                "symbol": symbol,
                "observations": len(series),
                "return_count": len(returns),
                "start_date": series[0].date.isoformat(),
                "end_date": series[-1].date.isoformat(),
                "last_close": closes[-1],
                "daily_returns": [
                    {
                        "date": point.date.isoformat(),
                        "return": value,
                        "rolling_volatility": (
                            rolling_values[index] if rolling_values is not None else None
                        ),
                    }
                    for index, (point, value) in enumerate(zip(series[1:], returns))
                ],
                "metrics": {
                    "mean_daily_return": mean_daily_return(returns),
                    "cumulative_return": cumulative_return(closes),
                    "cagr": cagr(closes, trading_days),
                    "annualized_volatility": annualized_volatility(returns, trading_days),
                    "max_drawdown": max_drawdown(closes),
                    "sharpe_ratio": sharpe_ratio(returns, risk_free_rate, trading_days),
                    "sortino_ratio": sortino_ratio(returns, risk_free_rate, trading_days),
                    "calmar_ratio": calmar_ratio(closes, trading_days),
                    "historical_var": historical_var(returns, var_confidence),
                },
            }
        )

    return {
        "parameters": {
            "risk_free_rate": risk_free_rate,
            "trading_days": trading_days,
            "var_confidence": var_confidence,
            "rolling_window": rolling_window,
        },
        "series": series_results,
    }
