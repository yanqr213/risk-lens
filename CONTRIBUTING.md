# Contributing

Thanks for improving `risk-lens`. The project aims to stay small, readable, and
useful as a command-line risk reporting tool.

## Local Setup

```powershell
python -m pip install -e ".[dev]"
python -m pytest
```

## Development Guidelines

- Keep runtime dependencies out of the core package unless there is a strong
  reason to add one.
- Prefer clear standard-library implementations for metrics.
- Add or update tests for every behavior change.
- Keep JSON field names stable when possible.
- Document new CLI flags, CSV assumptions, and output fields in `README.md` and
  `docs/`.
- Do not include credentials, private datasets, or generated cache directories.

## Pull Request Checklist

- Tests pass with `python -m pytest`.
- New metrics include formulas or interpretation notes.
- Error messages are actionable for CLI users.
- Example commands still work on Windows PowerShell and POSIX shells with minor
  path changes.
