# /// script
# requires-python = ">=3.11"
# dependencies = [
#     "pynesys-pynecore[cli]",
#     "ccxt",
# ]
# ///

"""
Fetch live OHLCV data from a crypto exchange using CCXT and run a PyneCore indicator on it.

This example shows how to:
  - Fetch historical + live candles from any CCXT-supported exchange
  - Stream them into a PyneCore script
  - React to indicator signals in real time

No API keys needed — uses public market data.
"""

import time
from pathlib import Path

import ccxt

from pynecore.core.script_runner import ScriptRunner
from pynecore.core.syminfo import SymInfo
from pynecore.types.ohlcv import OHLCV

# -- Configuration -----------------------------------------------------------

EXCHANGE = "binance"
SYMBOL = "BTC/USDT"
TIMEFRAME = "1h"
HISTORY_BARS = 100           # fetch this many historical bars first
LIVE_UPDATES = 5             # then poll for this many live updates
POLL_INTERVAL_SEC = 10       # seconds between live polls

SCRIPT = Path(__file__).parent / "simple_rsi.py"

# -- Fetch candles from exchange ---------------------------------------------


def fetch_ohlcv(exchange: ccxt.Exchange, symbol: str, timeframe: str,
                limit: int) -> list[OHLCV]:
    """Fetch OHLCV candles from a CCXT exchange."""
    raw = exchange.fetch_ohlcv(symbol, timeframe, limit=limit)
    return [
        OHLCV(
            timestamp=bar[0] // 1000,  # CCXT returns ms, PyneCore expects seconds
            open=bar[1],
            high=bar[2],
            low=bar[3],
            close=bar[4],
            volume=bar[5],
        )
        for bar in raw
    ]


def live_candle_generator(exchange: ccxt.Exchange, symbol: str, timeframe: str,
                          history: int, updates: int, poll_sec: int):
    """
    Generator that yields historical candles, then polls for new ones.

    In production you'd replace the polling loop with a websocket stream.
    """
    # Phase 1: historical data (indicator warmup)
    print(f"Fetching {history} historical {timeframe} candles for {symbol}...")
    candles = fetch_ohlcv(exchange, symbol, timeframe, limit=history)
    last_ts = 0

    for candle in candles:
        last_ts = candle.timestamp
        yield candle

    # Phase 2: poll for new candles
    print(f"\nSwitching to live mode — polling every {poll_sec}s...\n")
    for _ in range(updates):
        time.sleep(poll_sec)
        new_candles = fetch_ohlcv(exchange, symbol, timeframe, limit=5)
        for candle in new_candles:
            if candle.timestamp > last_ts:
                last_ts = candle.timestamp
                print(f"  New candle: {candle.close:.2f}")
                yield candle


# -- Main --------------------------------------------------------------------

# Build SymInfo for the pair
syminfo = SymInfo(
    prefix=EXCHANGE.upper(),
    description=SYMBOL,
    ticker=SYMBOL.replace("/", ""),
    currency="USDT",
    basecurrency="BTC",
    period="60",
    type="crypto",
    mintick=0.01,
    pricescale=100,
    minmove=1,
    pointvalue=1.0,
    timezone="UTC",
    volumetype="base",
    opening_hours=[],
    session_starts=[],
    session_ends=[],
)

# Create exchange instance (no API key needed for public data)
exchange = ccxt.binance({"enableRateLimit": True})

# Run the indicator on live data
runner = ScriptRunner(
    script_path=SCRIPT,
    ohlcv_iter=live_candle_generator(
        exchange, SYMBOL, TIMEFRAME, HISTORY_BARS, LIVE_UPDATES, POLL_INTERVAL_SEC
    ),
    syminfo=syminfo,
)

print(f"\nRunning RSI on {SYMBOL} ({EXCHANGE})\n")

for i, (candle, plot_data) in enumerate(runner.run_iter()):
    rsi = plot_data.get("RSI")

    if rsi is not None and rsi == rsi:
        signal = ""
        if rsi > 70:
            signal = " >>> OVERBOUGHT"
        elif rsi < 30:
            signal = " >>> OVERSOLD"

        # Print the last few historical bars + all live bars
        if i >= HISTORY_BARS - 5 or signal:
            print(f"Bar {i:>4}  Close={candle.close:>10.2f}  RSI={rsi:>6.2f}{signal}")

print("\nDone.")
