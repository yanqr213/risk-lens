"""Risk Lens: quantitative risk metrics for CSV price series."""

from .analysis import analyze_points
from .io import PricePoint, load_prices
from .metrics import (
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

__all__ = [
    "PricePoint",
    "analyze_points",
    "annualized_volatility",
    "cagr",
    "calmar_ratio",
    "daily_returns",
    "historical_var",
    "load_prices",
    "max_drawdown",
    "rolling_volatility",
    "sharpe_ratio",
    "sortino_ratio",
]

__version__ = "0.1.0"
