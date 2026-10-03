# 06 — FreqTrade + PyneCore Strategy Signals

Let a **Pine Script strategy** generate buy/sell signals — FreqTrade just executes them.

This pattern is ideal when you already have a working strategy on TradingView and want
to trade it live through FreqTrade without rewriting the logic in Python.

## Standalone Demo (no FreqTrade needed)

```bash
uv run run.py
```

Generates 500 bars, runs the SMA Crossover strategy, and prints every trade with P&L.

## Use in FreqTrade

1. Copy these files into your FreqTrade project:

   ```
   user_data/strategies/
   ├── strategy.py           # FreqTrade wrapper for PyneCore signals
   ├── pynecore_bridge.py    # DataFrame ↔ PyneCore bridge
   └── scripts/
       └── sma_crossover.py  # The Pine Script strategy
   ```

2. Add PyneCore to your FreqTrade environment:

   ```bash
   pip install "pynesys-pynecore>=6.10.6"
   ```

3. Run a backtest:

   ```bash
   freqtrade backtesting --strategy PyneStrategySignals
   ```

## How It Works

```
FreqTrade DataFrame (pandas)
        │
        ▼
  pynecore_bridge.py
  └── run_strategy()    →  Run Pine Script strategy on all bars
        │
        ├── indicators   →  Plot data (SMA values, etc.)
        ├── trades       →  Closed trades with bar indices
        └── open_trades  →  The position the strategy holds now
              │
              ▼
  Convert trade.entry_bar_index → enter_long[i] / enter_short[i] = 1
  Convert trade.exit_bar_index  → exit_long[i] / exit_short[i] = 1
        │
        ▼
  FreqTrade executes the signals
```

## Swapping in Your Own Strategy

1. Compile your TradingView strategy with PyneComp (or write one by hand)
2. Place the `.py` file in `scripts/`
3. Update `SCRIPT` path in `strategy.py`
4. Set `INPUTS` in `strategy.py` to your strategy's input values, keyed by the `main()` parameter
   names (not the input titles); an unknown key raises `ValueError`
5. Keep `"process_orders_on_close": True` in `SETTINGS`, so a trade's entry and exit bar is the bar
   that generated the signal, and size the entries there (`default_qty_type`,
   `default_qty_value`) instead of relying on Pine's 100%-of-equity default

## Performance Tip

FreqTrade calls `populate_indicators()` once per new candle (`process_only_new_candles`, on by
default) with the full DataFrame, and this example re-runs the whole strategy on it. Keep it that
way: the strategy's position, equity and every indicator it uses depend on all earlier bars, so
running only the new bars would produce different trades.

A full re-run is cheap. On a laptop a script takes a few milliseconds for 1,000 bars and a few tens
of milliseconds for 5,000 bars, far below a candle's duration even on `1m`.

## Indicator vs Strategy — Which to Use?

| Approach                                         | Best for                                    |
|--------------------------------------------------|---------------------------------------------|
| [05-freqtrade-indicators](../05-freqtrade-indicators/) | Custom Python logic + Pine Script math      |
| **06-freqtrade-strategy** (this example)         | Running a TradingView strategy as-is        |
