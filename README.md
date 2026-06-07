# risk-lens

`risk-lens` is a small, dependency-free Python CLI for calculating portfolio and
asset risk metrics from CSV close-price series. It is designed for developers,
analysts, and educators who want a transparent command-line tool that can be
used in scripts, CI jobs, notebooks, or lightweight data-quality checks without
pulling in a full quantitative finance stack.

The project intentionally uses the Python standard library at runtime. Metrics
are implemented in readable Python modules, output is stable JSON or Markdown,
and input is a plain CSV file.

> Outputs are for informational, educational, and research use only. `risk-lens`
> is not investment advice, trading advice, or a recommendation to buy or sell
> any security.

## Real Use Cases

- Check a vendor or internal price file before handing it to a larger risk
  pipeline.
- Generate quick drawdown, volatility, Sharpe, Sortino, Calmar, and VaR
  summaries for several symbols from one CSV.
- Add a reproducible risk report step to a data repository or scheduled job.
- Teach common return and risk metrics using auditable standard-library code.
- Compare JSON outputs between branches, datasets, or model-generated data.

## Features

- Reads either `date,close` or `symbol,date,close` CSV files.
- Automatically groups multi-symbol files and sorts each symbol by date.
- Rejects empty files, invalid dates, duplicate dates per symbol, non-finite
  closes, and non-positive prices.
- Calculates simple daily returns and summary metrics:
  - mean daily return
  - cumulative return
  - CAGR
  - annualized volatility
  - optional trailing rolling volatility
  - maximum drawdown
  - Sharpe ratio
  - Sortino ratio
  - Calmar ratio
  - historical VaR
- Supports JSON for machines and Markdown for reports.
- Runtime dependency footprint is zero beyond Python itself.
- Includes tests and GitHub Actions CI.

## Quick Start

```powershell
cd "E:\Documents\New project\public-projects\finance\risk-lens"
python -m pip install -e .
risk-lens examples/prices.csv --format markdown --rolling-window 3
```

Without installation:

```powershell
$env:PYTHONPATH = "src"
python -m risk_lens examples/prices.csv --format json
```

Install development tools and run tests:

```powershell
python -m pip install -e ".[dev]"
python -m pytest
```

## CLI Usage

```text
risk-lens [-h] [--format {json,markdown}]
          [--risk-free-rate RISK_FREE_RATE]
          [--trading-days TRADING_DAYS]
          [--var-confidence VAR_CONFIDENCE]
          [--rolling-window ROLLING_WINDOW]
          csv
```

Examples:

```powershell
risk-lens examples/prices.csv
risk-lens examples/prices.csv --format markdown
risk-lens examples/prices.csv --risk-free-rate 0.02
risk-lens examples/prices.csv --trading-days 250
risk-lens examples/prices.csv --var-confidence 0.99
risk-lens examples/prices.csv --rolling-window 20
```

## CSV Input Specification

Required columns:

| Column | Required | Description |
| --- | --- | --- |
| `date` | yes | ISO calendar date, for example `2024-01-02`. |
| `close` | yes | Positive finite closing price. |
| `symbol` | no | Asset identifier. Missing values use `SERIES`. |

Rules:

- Header names are case-insensitive after trimming whitespace.
- Rows are sorted by `date` inside each symbol before calculations.
- Each symbol can have at most one row per date.
- Blank rows are ignored.
- `close` must be greater than zero.
- Return calculations use the provided row sequence after date sorting; missing
  market days are not filled.

Example multi-symbol file:

```csv
symbol,date,close
AAA,2024-01-02,100.00
AAA,2024-01-03,101.50
BBB,2024-01-02,50.00
BBB,2024-01-03,49.50
```

Example single-series file:

```csv
date,close
2024-01-02,100.00
2024-01-03,101.50
```

## Metric Interpretation

All return values are simple returns, not log returns.

| Metric | Meaning |
| --- | --- |
| `mean_daily_return` | Arithmetic average of daily simple returns. |
| `cumulative_return` | Total return from first close to last close. |
| `cagr` | Compound annual growth rate using `--trading-days`. |
| `annualized_volatility` | Sample standard deviation of daily returns multiplied by `sqrt(trading_days)`. |
| `rolling_volatility` | Optional annualized sample volatility over a trailing return window. |
| `max_drawdown` | Worst peak-to-trough decline, returned as a negative fraction. |
| `sharpe_ratio` | Annualized mean excess return divided by sample volatility. |
| `sortino_ratio` | Annualized mean excess return divided by downside deviation. |
| `calmar_ratio` | CAGR divided by absolute maximum drawdown. |
| `historical_var` | Historical VaR as a positive loss fraction at `--var-confidence`. |

See [docs/METRICS.md](docs/METRICS.md) for formulas and edge-case behavior.

## Output Format

JSON output includes run parameters and one result object per symbol:

```json
{
  "parameters": {
    "risk_free_rate": 0.0,
    "rolling_window": 3,
    "trading_days": 252,
    "var_confidence": 0.95
  },
  "series": [
    {
      "symbol": "AAA",
      "observations": 6,
      "return_count": 5,
      "start_date": "2024-01-02",
      "end_date": "2024-01-09",
      "last_close": 105.0,
      "daily_returns": [
        {
          "date": "2024-01-03",
          "return": 0.015,
          "rolling_volatility": null
        }
      ],
      "metrics": {
        "mean_daily_return": 0.0102,
        "cumulative_return": 0.05,
        "cagr": 10.9846,
        "annualized_volatility": 0.36,
        "max_drawdown": -0.0227,
        "sharpe_ratio": 2.1,
        "sortino_ratio": 3.0,
        "calmar_ratio": 483.5,
        "historical_var": 0.019
      }
    }
  ]
}
```

Markdown output contains the same summary metrics plus a daily-return table.

## Development

```powershell
python -m pip install -e ".[dev]"
python -m pytest
python -m risk_lens examples/prices.csv --format markdown --rolling-window 3
```

The CI workflow runs the test suite on Python 3.10, 3.11, and 3.12.

## Limitations

- This is a close-price risk summary tool, not a portfolio optimizer.
- It does not fetch market data or validate corporate actions.
- It does not infer risk-free curves, benchmark returns, calendars, dividends,
  splits, or missing observations.
- Annualization assumes the supplied `--trading-days` value and treats each
  adjacent CSV observation as one return period.
- Short samples can produce unstable or unavailable ratios.
- Historical VaR is backward-looking and does not model tail events, liquidity,
  leverage, or future market conditions.

## License

MIT License. See [LICENSE](LICENSE).
