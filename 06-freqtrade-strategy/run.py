# /// script
# requires-python = ">=3.11"
# dependencies = ["pynesys-pynecore[cli]>=6.10.6", "pandas"]
# ///

"""
Let a Pine Script strategy generate buy/sell signals — FreqTrade just executes them.

This pattern is ideal when you already have a working strategy on TradingView and want
to run it live through FreqTrade without rewriting the logic in Python.

No FreqTrade dependency needed — this demo generates sample data and runs standalone.
For a real FreqTrade strategy, see strategy.py.
"""

import random
from pathlib import Path

import pandas as pd

from pynecore_bridge import run_strategy

SCRIPT = Path(__file__).parent / "scripts" / "sma_crossover.py"


# -- Generate sample BTC/USDT data -------------------------------------------

def generate_btc_data(bars: int = 500) -> pd.DataFrame:
    """Generate realistic-looking BTC/USDT 1h candles with trending segments."""
    rng = random.Random(123)
    base_time = pd.Timestamp("2024-01-01", tz="UTC")

    price = 42000.0
    momentum = 0.0
    rows = []

    for _ in range(bars):
        momentum = momentum * 0.95 + rng.gauss(0, 50)
        price += momentum
        price = max(price, 30000)

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

print("Running SMA Crossover strategy on 500 BTC/USDT candles...\n")

indicators, trades, open_trades = run_strategy(
    df,
    SCRIPT,
    pair="BTC/USDT",
    timeframe="1h",
    inputs={"length": 20, "confirmBars": 2},  # keyed by the script's main() parameter names
    # 10% of equity per entry instead of Pine's default 100%, which leaves no room for
    # adverse moves (margin calls)
    settings={"default_qty_type": "percent_of_equity", "default_qty_value": 10},
)

# Print trades (first 10 + last 5 if there are many)
SHOW_FIRST = 10
SHOW_LAST = 5

print(f"{'#':>3}  {'Dir':<5}  {'Entry':>10}  {'Exit':>10}  {'P&L':>10}  {'Cumulative':>10}")
print("-" * 60)

for i, trade in enumerate(trades, 1):
    if i <= SHOW_FIRST or i > len(trades) - SHOW_LAST:
        direction = "LONG" if trade.size > 0 else "SHORT"
        print(
            f"{i:>3}  {direction:<5}  "
            f"{trade.entry_price:>10.2f}  {trade.exit_price:>10.2f}  "
            f"{trade.profit:>+10.2f}  {trade.cum_profit:>+10.2f}"
        )
    elif i == SHOW_FIRST + 1:
        print(f"     ... ({len(trades) - SHOW_FIRST - SHOW_LAST} more trades) ...")

# Summary
if trades:
    wins = [t for t in trades if t.profit > 0]
    losses = [t for t in trades if t.profit <= 0]
    total_pnl = sum(t.profit for t in trades)

    print(f"\n{'=' * 60}")
    print(f"Total trades: {len(trades)}")
    print(f"Winners:      {len(wins)} ({len(wins) / len(trades) * 100:.1f}%)")
    print(f"Losers:       {len(losses)} ({len(losses) / len(trades) * 100:.1f}%)")
    print(f"Total P&L:    {total_pnl:+.2f}")
else:
    print("\nNo trades closed.")

for trade in open_trades:
    direction = "LONG" if trade.size > 0 else "SHORT"
    print(f"Open:         {direction} since bar {trade.entry_bar_index} at {trade.entry_price:.2f}")

print("\nDone.")
