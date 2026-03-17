# /// script
# requires-python = ">=3.11"
# dependencies = ["pynesys-pynecore[cli]", "pandas"]
# ///

"""
Use PyneCore indicators as data sources — then apply your own trading logic in Python.

This is the most flexible integration pattern: you pick any Pine Script indicator
(RSI, Bollinger Bands, custom indicators from TradingView) and combine them with
your own entry/exit rules written in Python.

No FreqTrade dependency needed — this demo generates sample data and runs standalone.
For a real FreqTrade strategy, see strategy.py.
"""

import random
from pathlib import Path

import pandas as pd

from pynecore_bridge import run_indicator

SCRIPTS_DIR = Path(__file__).parent / "scripts"


# -- Generate sample BTC/USDT data -------------------------------------------

def generate_btc_data(bars: int = 500) -> pd.DataFrame:
    """Generate realistic-looking BTC/USDT 1h candles with trending segments."""
    rng = random.Random(42)
    base_time = pd.Timestamp("2024-01-01", tz="UTC")

    price = 42000.0
    momentum = 0.0
    rows = []

    for _ in range(bars):
        # Random walk with momentum — creates realistic trends and reversals
        momentum = momentum * 0.95 + rng.gauss(0, 50)
        price += momentum
        price = max(price, 30000)  # floor

        spread = abs(momentum) + rng.uniform(50, 150)
        o = price + rng.uniform(-spread * 0.3, spread * 0.3)
        c = price + rng.uniform(-spread * 0.3, spread * 0.3)
        h = max(o, c) + rng.uniform(0, spread * 0.4)
        l = min(o, c) - rng.uniform(0, spread * 0.4)

        rows.append({
            "open": o, "high": h, "low": l, "close": c,
            "volume": rng.uniform(500, 5000),
        })

    df = pd.DataFrame(rows, index=pd.date_range(base_time, periods=bars, freq="h"))
    df.index.name = "date"
    return df


# -- Main ---------------------------------------------------------------------

df = generate_btc_data(500)

# Run two different indicators on the same data
print("Running RSI and Bollinger Bands on 500 BTC/USDT candles...\n")

rsi_results = run_indicator(df, SCRIPTS_DIR / "rsi.py", pair="BTC/USDT", timeframe="1h")
bb_results = run_indicator(df, SCRIPTS_DIR / "bollinger_bands.py", pair="BTC/USDT", timeframe="1h")

# Add indicator values to our DataFrame
df["rsi"] = rsi_results.get("RSI")
df["bb_upper"] = bb_results.get("Upper")
df["bb_basis"] = bb_results.get("Basis")
df["bb_lower"] = bb_results.get("Lower")

# Apply your own trading logic — this is pure Python, no Pine Script needed
print(f"{'Bar':>4}  {'Close':>10}  {'RSI':>6}  {'BB Low':>10}  {'BB Up':>10}  Signal")
print("-" * 72)

buy_signals = 0
sell_signals = 0
prev_signal = ""

for i, row in df.iterrows():
    rsi = row.get("rsi")
    bb_lower = row.get("bb_lower")
    bb_upper = row.get("bb_upper")
    close = row["close"]

    if rsi is None or rsi != rsi:  # skip NaN / warmup
        continue

    signal = ""

    # Your custom logic: RSI oversold + price near lower BB = buy signal
    if rsi < 30 and bb_lower is not None and bb_lower == bb_lower and close <= bb_lower * 1.02:
        signal = "BUY"
        buy_signals += 1

    # RSI overbought + price near upper BB = sell signal
    elif rsi > 70 and bb_upper is not None and bb_upper == bb_upper and close >= bb_upper * 0.98:
        signal = "SELL"
        sell_signals += 1

    bar_idx = df.index.get_loc(i)

    # Print: every 50th bar, or when a NEW signal type starts
    is_new_signal = signal and signal != prev_signal
    if is_new_signal or bar_idx % 50 == 0:
        label = f"  <<< {signal}" if signal else ""
        print(f"{bar_idx:>4}  {close:>10.2f}  {rsi:>6.2f}  {bb_lower:>10.2f}  {bb_upper:>10.2f}{label}")

    if signal:
        prev_signal = signal
    elif prev_signal:
        prev_signal = ""

print(f"\nBuy signals: {buy_signals}   Sell signals: {sell_signals}")
print("Done.")
