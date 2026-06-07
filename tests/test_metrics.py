from __future__ import annotations

import math
import statistics
from datetime import date

import pytest

from risk_lens.analysis import analyze_points
from risk_lens.cli import to_markdown
from risk_lens.io import PricePoint, group_prices
from risk_lens.metrics import (
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


def test_daily_returns_are_simple_returns() -> None:
    assert daily_returns([100.0, 110.0, 104.5]) == pytest.approx([0.10, -0.05])


def test_annualized_volatility_uses_sample_standard_deviation() -> None:
    returns = [0.01, -0.02, 0.03, 0.00]
    expected = statistics.stdev(returns) * math.sqrt(252)
    assert annualized_volatility(returns) == pytest.approx(expected)


def test_max_drawdown_reports_worst_peak_to_trough_loss() -> None:
    prices = [100.0, 120.0, 90.0, 96.0, 80.0, 130.0]
    assert max_drawdown(prices) == pytest.approx(-1 / 3)


def test_sharpe_ratio_annualizes_daily_excess_returns() -> None:
    returns = [0.01, -0.005, 0.015, 0.0]
    expected = (
        (statistics.mean(returns) - (0.02 / 252))
        / statistics.stdev(returns)
    ) * math.sqrt(252)
    assert sharpe_ratio(returns, risk_free_rate=0.02) == pytest.approx(expected)


def test_sortino_ratio_uses_downside_deviation() -> None:
    returns = [0.01, -0.02, 0.03, -0.01]
    downside = [min(0.0, value) for value in returns]
    downside_deviation = math.sqrt(sum(value * value for value in downside) / len(downside))
    expected = (statistics.mean(returns) / downside_deviation) * math.sqrt(252)
    assert sortino_ratio(returns) == pytest.approx(expected)


def test_sortino_ratio_returns_none_without_downside_deviation() -> None:
    assert sortino_ratio([0.01, 0.02, 0.03]) is None


def test_cagr_annualizes_price_growth() -> None:
    prices = [100.0, 110.0, 121.0]
    expected = (121.0 / 100.0) ** (252 / 2) - 1.0
    assert cagr(prices) == pytest.approx(expected)


def test_calmar_ratio_divides_cagr_by_absolute_drawdown() -> None:
    prices = [100.0, 120.0, 90.0, 130.0]
    expected = cagr(prices) / abs(max_drawdown(prices))
    assert calmar_ratio(prices) == pytest.approx(expected)


def test_calmar_ratio_returns_none_when_no_drawdown() -> None:
    assert calmar_ratio([100.0, 110.0, 121.0]) is None


def test_rolling_volatility_returns_trailing_annualized_values() -> None:
    returns = [0.01, -0.02, 0.03, 0.00]
    expected = [
        None,
        statistics.stdev(returns[0:2]) * math.sqrt(252),
        statistics.stdev(returns[1:3]) * math.sqrt(252),
        statistics.stdev(returns[2:4]) * math.sqrt(252),
    ]
    assert rolling_volatility(returns, window=2) == pytest.approx(expected)


def test_historical_var_is_positive_loss_at_95_confidence() -> None:
    returns = [-0.10, -0.02, 0.01, 0.03, 0.06]
    assert historical_var(returns, confidence=0.95) == pytest.approx(0.084)


def test_analyze_points_groups_by_symbol_and_sorts_by_date() -> None:
    points = [
        PricePoint("BBB", date(2024, 1, 3), 11.0),
        PricePoint("AAA", date(2024, 1, 2), 100.0),
        PricePoint("BBB", date(2024, 1, 2), 10.0),
        PricePoint("AAA", date(2024, 1, 3), 110.0),
    ]

    report = analyze_points(points)

    assert [item["symbol"] for item in report["series"]] == ["AAA", "BBB"]
    assert report["series"][0]["daily_returns"][0]["date"] == "2024-01-03"
    assert report["series"][0]["daily_returns"][0]["return"] == pytest.approx(0.10)
    assert report["series"][0]["daily_returns"][0]["rolling_volatility"] is None
    assert report["series"][1]["daily_returns"][0]["date"] == "2024-01-03"
    assert report["series"][1]["daily_returns"][0]["return"] == pytest.approx(0.10)
    assert report["series"][1]["daily_returns"][0]["rolling_volatility"] is None
    assert "cagr" in report["series"][0]["metrics"]
    assert "sortino_ratio" in report["series"][0]["metrics"]
    assert "calmar_ratio" in report["series"][0]["metrics"]
    assert report["series"][0]["metrics"]["historical_var"] is not None


def test_analyze_points_adds_rolling_volatility_when_requested() -> None:
    points = [
        PricePoint("AAA", date(2024, 1, 2), 100.0),
        PricePoint("AAA", date(2024, 1, 3), 101.0),
        PricePoint("AAA", date(2024, 1, 4), 99.0),
        PricePoint("AAA", date(2024, 1, 5), 102.0),
    ]

    report = analyze_points(points, rolling_window=2)
    rows = report["series"][0]["daily_returns"]

    assert rows[0]["rolling_volatility"] is None
    assert rows[1]["rolling_volatility"] is not None
    assert rows[2]["rolling_volatility"] is not None


def test_analyze_points_rejects_invalid_parameters() -> None:
    points = [
        PricePoint("AAA", date(2024, 1, 2), 100.0),
        PricePoint("AAA", date(2024, 1, 3), 101.0),
    ]

    with pytest.raises(ValueError, match="trading_days"):
        analyze_points(points, trading_days=0)
    with pytest.raises(ValueError, match="var_confidence"):
        analyze_points(points, var_confidence=1.0)
    with pytest.raises(ValueError, match="rolling_window"):
        analyze_points(points, rolling_window=0)


def test_markdown_report_includes_new_metric_columns() -> None:
    points = [
        PricePoint("AAA", date(2024, 1, 2), 100.0),
        PricePoint("AAA", date(2024, 1, 3), 101.0),
        PricePoint("AAA", date(2024, 1, 4), 99.0),
    ]

    markdown = to_markdown(analyze_points(points, rolling_window=2))

    assert "CAGR" in markdown
    assert "Sortino" in markdown
    assert "Calmar" in markdown
    assert "Rolling vol" in markdown


def test_group_prices_rejects_duplicate_dates_per_symbol() -> None:
    points = [
        PricePoint("AAA", date(2024, 1, 2), 100.0),
        PricePoint("AAA", date(2024, 1, 2), 101.0),
    ]

    with pytest.raises(ValueError, match="duplicate date"):
        group_prices(points)
