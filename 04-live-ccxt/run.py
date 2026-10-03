# /// script
# requires-python = ">=3.11"
# dependencies = [
#     "pynesys-pynecore[cli]>=6.10.7",
#     "ccxt",
# ]
# ///

"""
Fetch live OHLCV data from a crypto exchange using CCXT and run a PyneCore indicator on it.

This example shows how to:
  - Fetch historical + live candles from any CCXT-supported exchange
  - Stream them into a PyneCore script in live mode
  - React to indicator signals in real time, as soon as a candle closes

No API keys needed — uses public market data.
"""

import time
from pathlib import Path

import ccxt

from pynecore.core.script_runner import ScriptRunner, LIVE_TRANSITION
from pynecore.core.syminfo import SymInfo
from pynecore.types.ohlcv import OHLCV

# -- Configuration -----------------------------------------------------------

EXCHANGE = "binance"
SYMBOL = "BTC/USDT"
TIMEFRAME = "1m"             # short bars, so the demo sees new ones within minutes
PERIOD = "1"                 # the same timeframe as a Pine Script period ("60" = 1h, "D" = 1 day)
HISTORY_BARS = 100           # closed historical bars for the indicator warmup
LIVE_BARS = 3                # then wait for this many new closed bars
POLL_INTERVAL_SEC = 10       # seconds between live polls

SCRIPT = Path(__file__).parent / "simple_rsi.py"

# -- Fetch candles from exchange ---------------------------------------------


def fetch_closed_ohlcv(exchange: ccxt.Exchange, symbol: str, timeframe: str,
                       limit: int) -> list[OHLCV]:
    """
    Fetch the most recent CLOSED candles from a CCXT exchange.

    The exchange also returns the candle that is still forming; its values keep changing
    until it closes, so it is left out. The script sees every bar once, when it is final.
    """
    bar_ms = exchange.parse_timeframe(timeframe) * 1000
    now_ms = exchange.milliseconds()
    raw = exchange.fetch_ohlcv(symbol, timeframe, limit=limit + 1)
    return [
        OHLCV(
            timestamp=bar[0],  # CCXT and PyneCore both use milliseconds
            open=bar[1],
            high=bar[2],
            low=bar[3],
            close=bar[4],
            volume=bar[5],
        )
        for bar in raw
        if bar[0] + bar_ms <= now_ms
    ][-limit:]


def live_candle_generator(exchange: ccxt.Exchange, symbol: str, timeframe: str,
                          history: int, live_bars: int, poll_sec: int):
    """
    Generator that yields closed historical candles, then ``LIVE_TRANSITION``, then polls for
    newly closed ones.

    ``LIVE_TRANSITION`` tells the runner that the history is over: from then on it executes
    each candle as soon as it arrives. In production you'd replace the polling loop with a
    websocket stream.
    """
    # Phase 1: historical data (indicator warmup)
    print(f"Fetching {history} historical {timeframe} candles for {symbol}...")
    candles = fetch_closed_ohlcv(exchange, symbol, timeframe, limit=history)
    last_ts = 0

    for candle in candles:
        last_ts = candle.timestamp
        yield candle
    yield LIVE_TRANSITION

    # Phase 2: poll for newly closed candles
    print(f"\nSwitching to live mode — polling every {poll_sec}s...\n")
    received = 0
    while received < live_bars:
        time.sleep(poll_sec)
        for candle in fetch_closed_ohlcv(exchange, symbol, timeframe, limit=5):
            if candle.timestamp > last_ts:
                last_ts = candle.timestamp
                received += 1
                print(f"  New candle: {candle.close:.2f}")
                yield candle


# -- Main --------------------------------------------------------------------

# Build SymInfo for the pair
base_currency, quote_currency = SYMBOL.split("/")
syminfo = SymInfo(
    prefix=EXCHANGE.upper(),
    description=SYMBOL,
    ticker=SYMBOL.replace("/", ""),
    currency=quote_currency,
    basecurrency=base_currency,
    period=PERIOD,
    type="crypto",
    mintick=0.01,
    pricescale=100,
    minmove=1,
    pointvalue=1.0,
    mincontract=0.00001,
    timezone="UTC",
    volumetype="base",
    opening_hours=[],
    session_starts=[],
    session_ends=[],
)

# Create the exchange client (no API key needed for public data)
client = getattr(ccxt, EXCHANGE)({"enableRateLimit": True})

# Run the indicator on live data
runner = ScriptRunner(
    script_path=SCRIPT,
    ohlcv_iter=live_candle_generator(
        client, SYMBOL, TIMEFRAME, HISTORY_BARS, LIVE_BARS, POLL_INTERVAL_SEC
    ),
    syminfo=syminfo,
    live=True,
)

print(f"\nRunning RSI on {SYMBOL} ({EXCHANGE})\n")

for i, (ohlcv, plot_data) in enumerate(runner.run_iter()):
    rsi = plot_data.get("RSI")

    signal = ""
    if rsi > 70:
        signal = " >>> OVERBOUGHT"
    elif rsi < 30:
        signal = " >>> OVERSOLD"

    # Print the last few historical bars + all live bars
    if i >= HISTORY_BARS - 5 or signal:
        print(f"Bar {i:>4}  Close={ohlcv.close:>10.2f}  RSI={rsi:>6.2f}{signal}")

print("\nDone.")
