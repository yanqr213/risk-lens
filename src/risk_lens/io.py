from __future__ import annotations

import csv
import math
from collections import defaultdict
from collections.abc import Iterable
from dataclasses import dataclass
from datetime import date
from pathlib import Path


DEFAULT_SYMBOL = "SERIES"


@dataclass(frozen=True)
class PricePoint:
    symbol: str
    date: date
    close: float


def load_prices(path: str | Path) -> list[PricePoint]:
    """Load prices from CSV with date, close or symbol, date, close columns."""
    csv_path = Path(path)
    with csv_path.open("r", encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        if reader.fieldnames is None:
            raise ValueError("CSV must include a header row")

        headers = {field.strip().lower(): field for field in reader.fieldnames}
        date_key = _required_header(headers, "date")
        close_key = _required_header(headers, "close")
        symbol_key = headers.get("symbol")

        points: list[PricePoint] = []
        for line_number, row in enumerate(reader, start=2):
            if _is_empty_row(row):
                continue

            raw_symbol = row.get(symbol_key, "") if symbol_key else ""
            symbol = (raw_symbol or "").strip() or DEFAULT_SYMBOL
            raw_date = (row.get(date_key) or "").strip()
            raw_close = (row.get(close_key) or "").strip()

            try:
                parsed_date = date.fromisoformat(raw_date)
            except ValueError as exc:
                raise ValueError(f"line {line_number}: invalid date {raw_date!r}") from exc

            try:
                close = float(raw_close)
            except ValueError as exc:
                raise ValueError(f"line {line_number}: invalid close {raw_close!r}") from exc

            if not math.isfinite(close) or close <= 0:
                raise ValueError(f"line {line_number}: close must be a positive number")

            points.append(PricePoint(symbol=symbol, date=parsed_date, close=close))

    if not points:
        raise ValueError("CSV does not contain any price rows")
    return points


def group_prices(points: Iterable[PricePoint]) -> dict[str, list[PricePoint]]:
    grouped: dict[str, list[PricePoint]] = defaultdict(list)
    for point in points:
        grouped[point.symbol].append(point)

    result: dict[str, list[PricePoint]] = {}
    for symbol, series in grouped.items():
        ordered = sorted(series, key=lambda item: item.date)
        seen_dates: set[date] = set()
        for point in ordered:
            if point.date in seen_dates:
                raise ValueError(f"symbol {symbol!r} has duplicate date {point.date.isoformat()}")
            seen_dates.add(point.date)
        result[symbol] = ordered
    return result


def _required_header(headers: dict[str, str], name: str) -> str:
    try:
        return headers[name]
    except KeyError as exc:
        raise ValueError(f"CSV must include a {name!r} column") from exc


def _is_empty_row(row: dict[str, str | None]) -> bool:
    return all((value or "").strip() == "" for value in row.values())
