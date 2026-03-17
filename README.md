# PyneCore Examples

Practical examples for using [PyneCore](https://github.com/pynesys/pynecore) programmatically —
embedding indicators and strategies into your own Python applications.

Each example is a self-contained project. Just `cd` into a directory and run it.

## Examples

| #  | Directory                                                | Description                                         |
|----|----------------------------------------------------------|-----------------------------------------------------|
| 01 | [`01-standalone/`](01-standalone/)                       | Run a script on a CSV file — zero code, one command |
| 02 | [`02-programmatic/`](02-programmatic/)                   | ScriptRunner API — read outputs, override inputs    |
| 03 | [`03-custom-data/`](03-custom-data/)                     | Feed OHLCV from any source (API, DB, DataFrame)     |
| 04 | [`04-live-ccxt/`](04-live-ccxt/)                         | Live exchange data with CCXT (no API key needed)    |
| 05 | [`05-freqtrade-indicators/`](05-freqtrade-indicators/)   | FreqTrade + PyneCore indicators as data sources     |
| 06 | [`06-freqtrade-strategy/`](06-freqtrade-strategy/)       | FreqTrade + PyneCore strategy signals               |

## Quick Start

The fastest way to try PyneCore — no install, no setup:

```bash
cd 01-standalone
uv run bollinger_bands.py data/EURUSD_1h.csv
```

This fetches PyneCore automatically, runs Bollinger Bands on the sample data, and writes the results
to a CSV file.

> **Don't have `uv`?** Install it with `curl -LsSf https://astral.sh/uv/install.sh | sh` or see
> [uv docs](https://docs.astral.sh/uv/). Alternatively, install PyneCore with pip and run with
> Python directly — see each example's README for details.

## How It Works

PyneCore scripts are Python files with a `@pyne` marker. They use the same API as
[Pine Script](https://www.tradingview.com/pine-script-docs/) on TradingView — `ta.rsi()`,
`ta.sma()`, `strategy.entry()`, etc. — but run locally on your machine.

You can:
- **Compile Pine Script** to PyneCore using [PyneComp](https://pynesys.io)
- **Write scripts by hand** — see [PyneCore docs](https://pynecore.org/docs)

## License

[CC0 1.0 Universal](LICENSE) — copy, modify, and use in any project without attribution.
