# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Commands

```bash
# Install dependencies
pip install -r requirements.txt

# Run the development server
python app.py
# App runs at http://localhost:5000
```

## Architecture

This is a Flask web app that displays real-time B3 stock quotes fetched via `yfinance`.

**Request flow:**
1. Browser loads `/` → Flask renders `templates/index.html` with initial quotes (server-side via Jinja2)
2. Every `REFRESH_INTERVAL_SECONDS` (default 60s), `static/js/refresh.js` polls `/api/quotes` and updates the DOM in-place
3. On page load, `refresh.js` also calls `/api/history/<code>` for each ticker to render a Chart.js sparkline

**Key files:**
- [config.py](config.py) — source of truth for which tickers to track (`TICKERS` dict), refresh interval, and cache TTL. Add new stocks here.
- [services/stock_service.py](services/stock_service.py) — all yfinance interaction. Maintains a module-level in-memory cache keyed by the full `_cache` dict with a single timestamp. `fetch_all_quotes()` returns all tickers at once; `fetch_history()` fetches YTD history for a single ticker (hardcoded `start="2026-01-01"`).
- [app.py](app.py) — thin Flask layer: three routes, no business logic.
- [static/js/refresh.js](static/js/refresh.js) — polling loop (`setInterval`) + Chart.js initialization on `DOMContentLoaded`.

**SSL note:** `stock_service.py` disables SSL verification globally (`ssl._create_unverified_context`, `urllib3.disable_warnings`) to work around corporate proxy environments. This is intentional — do not remove without verifying connectivity still works.

**Adding a new ticker:** Add an entry to `TICKERS` in `config.py` with keys `symbol` (Yahoo Finance format, e.g. `"BBDC4.SA"`), `name`, and `color`. No other changes needed.
