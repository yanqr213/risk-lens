# Metrics

This document describes the calculations used by `risk-lens`. All returns are
simple returns:

```text
return[t] = close[t] / close[t-1] - 1
```

## Annualization

Annualized metrics use the `--trading-days` value, which defaults to `252`.
The tool treats each adjacent CSV observation as one return period after sorting
by date.

## Summary Metrics

| Metric | Formula or behavior |
| --- | --- |
| Mean daily return | Arithmetic mean of daily returns. |
| Cumulative return | `last_close / first_close - 1`. |
| CAGR | `(last_close / first_close) ** (trading_days / periods) - 1`. |
| Annualized volatility | Sample standard deviation of returns times `sqrt(trading_days)`. |
| Rolling volatility | Same volatility formula over each trailing return window. Values are `null` until enough returns exist. |
| Maximum drawdown | Minimum value of `close / running_peak - 1`. |
| Sharpe ratio | Annualized mean excess daily return divided by sample standard deviation. |
| Sortino ratio | Annualized mean excess daily return divided by downside deviation below the daily risk-free target. |
| Calmar ratio | CAGR divided by absolute maximum drawdown. |
| Historical VaR | Quantile of historical returns at `1 - confidence`, reported as a positive loss fraction. |

## Edge Cases

- Metrics that require at least two returns return `null` when the sample is too
  short.
- Sharpe returns `null` when sample volatility is zero.
- Sortino returns `null` when downside deviation is zero.
- Calmar returns `null` when there is no drawdown.
- Prices must be positive for return, CAGR, cumulative return, and drawdown
  calculations.
- Historical VaR is clipped at zero when the selected quantile is positive.

## Interpretation Notes

High Sharpe, Sortino, or Calmar values over short samples can be misleading.
Historical VaR only summarizes losses observed in the input sample and does not
forecast future market stress. Use these outputs as diagnostics, not as standalone
investment decisions.
