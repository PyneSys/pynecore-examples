# 01 — Standalone Execution

The simplest way to use PyneCore: run a compiled script directly on a CSV file. No code to write — just
one command.

## Run

```bash
# With uv (recommended — no manual install needed)
uv run bollinger_bands.py data/EURUSD_1h.csv
uv run sma_crossover.py data/EURUSD_1h.csv

# Or with pip
pip install pynesys-pynecore[cli]
python bollinger_bands.py data/EURUSD_1h.csv
python sma_crossover.py data/EURUSD_1h.csv
```

## What Happens

1. The CSV is automatically converted to PyneCore's binary OHLCV format (in a temp directory)
2. The script runs bar-by-bar, just like on TradingView
3. Output CSV files are created next to the script:
   - `bollinger_bands_plot.csv` — indicator values for each bar
   - `sma_crossover_trades.csv` — executed trades (for strategies)
   - `sma_crossover_strat.csv` — strategy performance summary

## Scripts

| Script                                           | Type      | Description                          |
|--------------------------------------------------|-----------|--------------------------------------|
| [`bollinger_bands.py`](bollinger_bands.py)       | Indicator | Bollinger Bands (SMA/EMA/RMA/WMA)   |
| [`sma_crossover.py`](sma_crossover.py)           | Strategy  | SMA crossover with confirmation bars |

## Data

[`data/EURUSD_1h.csv`](data/EURUSD_1h.csv) — 1000 bars of EUR/USD hourly data (2022-01-02 to
2022-02-12).

## How Scripts Are Made

These scripts were compiled from Pine Script using [PyneComp](https://pynesys.io). You can also
write them by hand — see [PyneCore scripting docs](https://pynecore.org/docs).
