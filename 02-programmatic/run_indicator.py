# /// script
# requires-python = ">=3.11"
# dependencies = ["pynesys-pynecore[cli]"]
# ///

"""
Run a PyneCore indicator programmatically and process its output in Python.

This example shows how to:
  - Convert a CSV file to PyneCore's binary OHLCV format
  - Load symbol info and OHLCV data
  - Run a script with ScriptRunner
  - Read indicator values bar-by-bar
"""

from pathlib import Path
from pynecore.core.data_converter import DataConverter
from pynecore.core.ohlcv_file import OHLCVReader
from pynecore.core.script_runner import ScriptRunner
from pynecore.core.syminfo import SymInfo

# Paths
SCRIPT = Path(__file__).parent / "scripts" / "bollinger_bands.py"
CSV_FILE = Path(__file__).parent / "data" / "EURUSD_1h.csv"
DATA_DIR = Path(__file__).parent / "data"

# Step 1: Convert CSV to binary OHLCV format
# This creates EURUSD_1h.ohlcv (binary data) and EURUSD_1h.toml (symbol info)
DataConverter().convert_to_ohlcv(CSV_FILE)

# Step 2: Load symbol info and open the OHLCV reader
ohlcv_path = DATA_DIR / "EURUSD_1h.ohlcv"
toml_path = DATA_DIR / "EURUSD_1h.toml"
syminfo = SymInfo.load_toml(toml_path)

with OHLCVReader(ohlcv_path) as reader:
    # Step 3: Create the ScriptRunner
    runner = ScriptRunner(
        script_path=SCRIPT,
        ohlcv_iter=reader.read_from(reader.start_timestamp, reader.end_timestamp),
        syminfo=syminfo,
    )

    # Step 4: Iterate bar-by-bar and process indicator output
    print(f"Running Bollinger Bands on {syminfo.ticker} ({reader.size} bars)\n")
    print(f"{'Bar':>5}  {'Close':>10}  {'Basis':>10}  {'Upper':>10}  {'Lower':>10}")
    print("-" * 55)

    for i, (candle, plot_data) in enumerate(runner.run_iter()):
        basis = plot_data.get("Basis")
        upper = plot_data.get("Upper")
        lower = plot_data.get("Lower")

        # Indicator values are NaN during warmup (first `length` bars)
        if basis is not None and basis == basis:  # NaN check: NaN != NaN
            print(f"{i:>5}  {candle.close:>10.5f}  {basis:>10.5f}  {upper:>10.5f}  {lower:>10.5f}")

            # Example: detect price touching the lower band
            if candle.close <= lower:
                print(f"       ^^^ Price at lower band — potential buy signal")

        # Only print first 50 valid bars for this demo
        if i > 70:
            print(f"\n... ({reader.size - i - 1} more bars)")
            break
