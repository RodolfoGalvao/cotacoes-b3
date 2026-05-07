import ssl
import time
import requests
import urllib3
import yfinance as yf
from config import TICKERS, CACHE_TTL_SECONDS

ssl._create_default_https_context = ssl._create_unverified_context
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

_session = requests.Session()
_session.verify = False

_cache: dict = {}
_cache_timestamp: float = 0.0


def _is_cache_valid() -> bool:
    return bool(_cache) and (time.time() - _cache_timestamp) < CACHE_TTL_SECONDS


def fetch_all_quotes() -> dict:
    global _cache, _cache_timestamp

    if _is_cache_valid():
        return _cache

    results = {}
    for short_code, meta in TICKERS.items():
        sym = meta["symbol"]
        try:
            hist = yf.Ticker(sym, session=_session).history(period="5d")
            price = round(float(hist["Close"].iloc[-1]), 2)
            prev_close = round(float(hist["Close"].iloc[-2]), 2)
            change = round(price - prev_close, 2)
            change_pct = round((change / prev_close) * 100, 2) if prev_close else 0.0

            results[short_code] = {
                "name": meta["name"],
                "symbol": sym,
                "color": meta["color"],
                "price": price,
                "prev_close": prev_close,
                "change": change,
                "change_pct": change_pct,
                "currency": "BRL",
                "error": None,
            }
        except Exception as exc:
            results[short_code] = {
                "name": meta["name"],
                "symbol": sym,
                "color": meta["color"],
                "price": None,
                "prev_close": None,
                "change": None,
                "change_pct": None,
                "currency": "BRL",
                "error": str(exc),
            }

    _cache = results
    _cache_timestamp = time.time()
    return results


def fetch_history(code: str) -> dict:
    meta = TICKERS.get(code)
    if not meta:
        return {"dates": [], "closes": [], "error": "Ticker não encontrado"}
    try:
        hist = yf.Ticker(meta["symbol"], session=_session).history(start="2026-01-01")
        dates = [d.strftime("%d/%m") for d in hist.index]
        closes = [round(float(v), 2) for v in hist["Close"]]
        return {"dates": dates, "closes": closes, "error": None}
    except Exception as exc:
        return {"dates": [], "closes": [], "error": str(exc)}
