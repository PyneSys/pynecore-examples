# /// script
# requires-python = ">=3.11"
# dependencies = ["pynesys-pynecore[cli]>=6.10.6"]
# ///

"""
Run a PyneCore strategy programmatically and process trade results in Python.

This example shows how to:
  - Run a strategy with ScriptRunner
  - Capture closed trades as they happen
  - Override script input parameters and strategy settings at runtime
  - Calculate custom statistics from trade results
"""

from pathlib import Path
from pynecore.core.data_converter import DataConverter
from pynecore.core.ohlcv import OHLCVReader
from pynecore.core.script_runner import ScriptRunner
from pynecore.core.syminfo import SymInfo

# Paths
SCRIPT = Path(__file__).parent / "scripts" / "sma_crossover.py"
CSV_FILE = Path(__file__).parent / "data" / "EURUSD_1h.csv"
DATA_DIR = Path(__file__).parent / "data"

# Convert CSV if needed
DataConverter().convert_to_ohlcv(CSV_FILE)

# Load data
ohlcv_path = DATA_DIR / "EURUSD_1h.ohlcv"
toml_path = DATA_DIR / "EURUSD_1h.toml"
syminfo = SymInfo.load_toml(toml_path)

with OHLCVReader(ohlcv_path) as reader:
    runner = ScriptRunner(
        script_path=SCRIPT,
        ohlcv_iter=reader.read_from(reader.start_timestamp, reader.end_timestamp),
        syminfo=syminfo,
        # Override script inputs at runtime — keyed by the main() parameter names
        inputs={"length": 15, "confirmBars": 2},
        # Override the strategy's own settings: trade 10% of equity per entry instead of
        # Pine's default 100%, which leaves no room for adverse moves (margin calls)
        settings={"default_qty_type": "percent_of_equity", "default_qty_value": 10},
    )

    print(f"Running SMA Crossover on {syminfo.ticker} ({reader.size} bars)")
    print(f"Inputs: length=15, confirmBars=2; size: 10% of equity\n")

    # Strategies yield a third element: list of newly closed trades
    all_trades = []

    for candle, plot_data, new_trades in runner.run_iter():
        for trade in new_trades:
            all_trades.append(trade)
            direction = "LONG" if trade.size > 0 else "SHORT"
            print(
                f"Trade #{len(all_trades):>3}  {direction:<5}  "
                f"entry={trade.entry_price:.5f}  exit={trade.exit_price:.5f}  "
                f"P&L={trade.profit:+.2f}  cum={trade.cum_profit:+.2f}"
            )

    # Summary
    if all_trades:
        wins = [t for t in all_trades if t.profit > 0]
        losses = [t for t in all_trades if t.profit <= 0]
        total_pnl = sum(t.profit for t in all_trades)

        print(f"\n{'='*60}")
        print(f"Total trades: {len(all_trades)}")
        print(f"Winners:      {len(wins)} ({len(wins)/len(all_trades)*100:.1f}%)")
        print(f"Losers:       {len(losses)} ({len(losses)/len(all_trades)*100:.1f}%)")
        print(f"Total P&L:    {total_pnl:+.2f}")
    else:
        print("\nNo trades executed.")
