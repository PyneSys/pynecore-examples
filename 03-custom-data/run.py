# /// script
# requires-python = ">=3.11"
# dependencies = ["pynesys-pynecore[cli]"]
# ///

"""
Feed custom OHLCV data into PyneCore from any source — no CSV files needed.

This example shows how to:
  - Create OHLCV objects from any data source (API, database, websocket, etc.)
  - Build a SymInfo manually (without a TOML file)
  - Use a Python generator as the data feed
  - Process indicator output in real time
"""

from pathlib import Path
from pynecore.core.script_runner import ScriptRunner
from pynecore.core.syminfo import SymInfo
from pynecore.types.ohlcv import OHLCV


# -- Example script (inline for simplicity) ----------------------------------

SCRIPT = Path(__file__).parent / "simple_rsi.py"


# -- Custom data source -------------------------------------------------------

def generate_candles() -> list[OHLCV]:
    """
    Simulate fetching OHLCV data from an external source.

    In a real application, this could be:
      - A database query
      - A REST API call (e.g., Binance, Coinbase)
      - A websocket stream
      - A pandas DataFrame
    """
    import math

    candles = []
    base_price = 42000.0
    base_time = 1704067200  # 2024-01-01 00:00:00 UTC in seconds

    for i in range(200):
        # Generate a realistic-looking price series
        trend = i * 5.0
        cycle = math.sin(i / 20.0) * 200
        noise = (hash(f"seed_{i}") % 100 - 50) * 2.0

        mid = base_price + trend + cycle + noise
        spread = abs(noise) + 50

        candles.append(OHLCV(
            timestamp=base_time + i * 3600,  # 1 hour = 3600 seconds
            open=mid - spread * 0.3,
            high=mid + spread * 0.5,
            low=mid - spread * 0.5,
            close=mid + spread * 0.2,
            volume=1000.0 + abs(noise) * 10,
        ))

    return candles


# -- Main logic ---------------------------------------------------------------

# Build SymInfo manually — no TOML file needed
syminfo = SymInfo(
    prefix="BINANCE",
    description="Bitcoin / US Dollar",
    ticker="BTCUSD",
    currency="USD",
    basecurrency="BTC",
    period="60",                       # 60-minute bars
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

# Generate our custom data
candles = generate_candles()


def candle_iterator():
    """Generator that yields OHLCV candles one by one."""
    yield from candles


# Create and run the ScriptRunner
runner = ScriptRunner(
    script_path=SCRIPT,
    ohlcv_iter=candle_iterator(),
    syminfo=syminfo,
)

print(f"Running RSI on {len(candles)} custom-generated BTCUSD candles\n")

for i, (candle, plot_data) in enumerate(runner.run_iter()):
    rsi = plot_data.get("RSI")

    signal = ""
    if rsi > 70:
        signal = " <-- OVERBOUGHT"
    elif rsi < 30:
        signal = " <-- OVERSOLD"

    if signal or i % 20 == 0:
        print(f"Bar {i:>4}  Close={candle.close:>10.2f}  RSI={rsi:>6.2f}{signal}")

print("\nDone.")
