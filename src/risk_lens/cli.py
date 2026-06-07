from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

from .analysis import analyze_points
from .io import load_prices
from .metrics import DEFAULT_TRADING_DAYS


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="risk-lens",
        description="Calculate quantitative risk metrics from CSV price series.",
    )
    parser.add_argument(
        "csv",
        type=Path,
        help="CSV file with date,close or symbol,date,close columns.",
    )
    parser.add_argument(
        "--format",
        choices=("json", "markdown"),
        default="json",
        help="Output format. Defaults to json.",
    )
    parser.add_argument(
        "--risk-free-rate",
        type=float,
        default=0.0,
        help="Annual risk-free rate used for Sharpe ratio, e.g. 0.02 for 2%%.",
    )
    parser.add_argument(
        "--trading-days",
        type=int,
        default=DEFAULT_TRADING_DAYS,
        help="Trading days per year for annualization. Defaults to 252.",
    )
    parser.add_argument(
        "--var-confidence",
        type=float,
        default=0.95,
        help="Historical VaR confidence level between 0 and 1. Defaults to 0.95.",
    )
    parser.add_argument(
        "--rolling-window",
        type=int,
        default=None,
        help="Optional trailing return window for annualized rolling volatility.",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    try:
        points = load_prices(args.csv)
        report = analyze_points(
            points,
            risk_free_rate=args.risk_free_rate,
            trading_days=args.trading_days,
            var_confidence=args.var_confidence,
            rolling_window=args.rolling_window,
        )
    except (OSError, ValueError) as exc:
        print(f"risk-lens: {exc}", file=sys.stderr)
        return 2

    if args.format == "markdown":
        print(to_markdown(report))
    else:
        print(json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True))
    return 0


def to_markdown(report: dict[str, Any]) -> str:
    parameters = report["parameters"]
    lines = [
        "# Risk Lens Report",
        "",
        f"- Risk-free rate: {_format_percent(parameters['risk_free_rate'])}",
        f"- Trading days: {parameters['trading_days']}",
        f"- Historical VaR confidence: {_format_percent(parameters['var_confidence'])}",
        f"- Rolling volatility window: {parameters['rolling_window'] or 'disabled'}",
        "",
        "| Symbol | Period | Obs. | Cum. return | CAGR | Ann. vol | Max drawdown | Sharpe | Sortino | Calmar | Hist. VaR |",
        "| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |",
    ]

    for item in report["series"]:
        metrics = item["metrics"]
        period = f"{item['start_date']} to {item['end_date']}"
        lines.append(
            "| {symbol} | {period} | {observations} | {cumulative} | {cagr} | {vol} | {drawdown} | {sharpe} | {sortino} | {calmar} | {var} |".format(
                symbol=item["symbol"],
                period=period,
                observations=item["observations"],
                cumulative=_format_percent(metrics["cumulative_return"]),
                cagr=_format_percent(metrics["cagr"]),
                vol=_format_percent(metrics["annualized_volatility"]),
                drawdown=_format_percent(metrics["max_drawdown"]),
                sharpe=_format_number(metrics["sharpe_ratio"]),
                sortino=_format_number(metrics["sortino_ratio"]),
                calmar=_format_number(metrics["calmar_ratio"]),
                var=_format_percent(metrics["historical_var"]),
            )
        )

    for item in report["series"]:
        lines.extend(
            [
                "",
                f"## {item['symbol']} Daily Returns",
                "",
                "| Date | Return | Rolling vol |",
                "| --- | ---: | ---: |",
            ]
        )
        if item["daily_returns"]:
            for row in item["daily_returns"]:
                lines.append(
                    f"| {row['date']} | {_format_percent(row['return'])} | {_format_percent(row['rolling_volatility'])} |"
                )
        else:
            lines.append("| n/a | n/a | n/a |")

    lines.extend(
        [
            "",
            "> This report is for informational and educational use only. It is not investment advice.",
        ]
    )
    return "\n".join(lines)


def _format_percent(value: float | None) -> str:
    if value is None:
        return "n/a"
    return f"{value:.2%}"


def _format_number(value: float | None) -> str:
    if value is None:
        return "n/a"
    return f"{value:.4f}"
