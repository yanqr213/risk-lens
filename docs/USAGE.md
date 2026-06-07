# Usage Guide

`risk-lens` accepts a CSV file and writes either JSON or Markdown to standard
output. JSON is the default because it is stable for scripts and downstream
automation.

## Install

```powershell
python -m pip install -e .
```

For development:

```powershell
python -m pip install -e ".[dev]"
```

## Basic Commands

```powershell
risk-lens examples/prices.csv
risk-lens examples/prices.csv --format markdown
```

Run without installing the console script:

```powershell
$env:PYTHONPATH = "src"
python -m risk_lens examples/prices.csv --format json
```

## Options

| Option | Default | Description |
| --- | ---: | --- |
| `--format` | `json` | Output as `json` or `markdown`. |
| `--risk-free-rate` | `0.0` | Annual risk-free rate used by Sharpe and Sortino. Use `0.02` for 2%. |
| `--trading-days` | `252` | Annualization periods per year. |
| `--var-confidence` | `0.95` | Historical VaR confidence level between 0 and 1. |
| `--rolling-window` | disabled | Trailing return count for annualized rolling volatility. |

## CSV Requirements

The CSV must include `date` and `close`. `symbol` is optional.

```csv
symbol,date,close
AAA,2024-01-02,100.00
AAA,2024-01-03,101.50
```

Dates must be ISO formatted as `YYYY-MM-DD`. Prices must be positive finite
numbers. Duplicate dates within the same symbol are rejected because they make
return ordering ambiguous.

## Exit Codes

| Code | Meaning |
| ---: | --- |
| `0` | Report generated successfully. |
| `2` | Input, file, or parameter error. |

## Scripting Example

```powershell
risk-lens data\prices.csv --rolling-window 20 --var-confidence 0.99 > risk-report.json
```
