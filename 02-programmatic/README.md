# 02 — Programmatic Usage

Use PyneCore's `ScriptRunner` API to run scripts from your own Python code. This is the foundation for
building trading bots, custom dashboards, backtesting pipelines, and integrations.

## Run

```bash
# Indicator — prints Bollinger Bands values bar-by-bar
uv run run_indicator.py

# Strategy — runs SMA Crossover with custom inputs and settings, prints trades
uv run run_strategy.py
```

## What You'll Learn

### `run_indicator.py` — Running an Indicator

1. **Convert CSV to OHLCV** — `DataConverter.convert_to_ohlcv()` creates binary data + symbol info
2. **Create ScriptRunner** — pass script path, OHLCV iterator, and symbol info
3. **Iterate with `run_iter()`** — yields `(candle, plot_data)` for each bar
4. **Read output** — `plot_data` is a dict with named values (e.g. `{"Basis": 1.136, "Upper": 1.139, ...}`)

### `run_strategy.py` — Running a Strategy with Trade Output

1. **Override inputs** — pass `inputs={"length": 15}` to change script parameters without editing the
   file. Keys are the `main()` parameter names, not the input titles; an unknown key raises `ValueError`.
2. **Override settings** — pass `settings={"default_qty_value": 10, ...}` to change the strategy's own
   settings (sizing, capital, commission, ...) for this run. Neither override is written back to the
   script's `.toml`.
3. **Capture trades** — strategies yield `(candle, plot_data, new_trades)` with closed trades
4. **Trade fields** — `entry_price`, `exit_price`, `profit`, `cum_profit`, `size`, and more
5. **Build custom stats** — calculate win rate, total P&L, or feed trades into your own analytics

## Key API

```python
from pynecore.core.script_runner import ScriptRunner
from pynecore.core.syminfo import SymInfo
from pynecore.core.ohlcv import OHLCVReader
from pynecore.core.data_converter import DataConverter

# Convert CSV once
DataConverter().convert_to_ohlcv(Path("data/EURUSD_1h.csv"))

# Load and run
syminfo = SymInfo.load_toml(Path("data/EURUSD_1h.toml"))
with OHLCVReader(Path("data/EURUSD_1h.ohlcv")) as reader:
    runner = ScriptRunner(
        script_path=Path("scripts/bollinger_bands.py"),
        ohlcv_iter=reader.read_from(reader.start_timestamp, reader.end_timestamp),
        syminfo=syminfo,
        inputs={"length": 20},        # optional: override script inputs (main() parameter names)
        plot_path=Path("output.csv"), # optional: save all output to CSV
    )
    for candle, plot_data in runner.run_iter():
        # Your logic here
        pass
```
