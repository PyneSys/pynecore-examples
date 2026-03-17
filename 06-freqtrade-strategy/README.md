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
   pip install pynesys-pynecore
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
        ├── indicators  →  Plot data (SMA values, etc.)
        └── trades      →  List of closed trades with bar indices
              │
              ▼
  Convert trade.entry_bar_index → enter_long[i] = 1
  Convert trade.exit_bar_index  → exit_long[i] = 1
        │
        ▼
  FreqTrade executes the signals
```

## Swapping in Your Own Strategy

1. Compile your TradingView strategy with PyneComp (or write one by hand)
2. Place the `.py` file in `scripts/`
3. Update `SCRIPT` path in `strategy.py`
4. Adjust `inputs={}` to match your strategy's `input()` parameters

## Performance Tip

FreqTrade calls `populate_indicators()` on every new candle with the full DataFrame. The simple
approach in this example re-runs the entire strategy each time — fine for hourly timeframes, but
wasteful for lower ones.

For production use, **cache the trade signals** in the strategy: store the entry/exit bar indices
from previous runs, and only re-run PyneCore when new bars arrive. This makes the integration
essentially zero-cost after the initial warmup.

## Indicator vs Strategy — Which to Use?

| Approach                                         | Best for                                    |
|--------------------------------------------------|---------------------------------------------|
| [05-freqtrade-indicators](../05-freqtrade-indicators/) | Custom Python logic + Pine Script math      |
| **06-freqtrade-strategy** (this example)         | Running a TradingView strategy as-is        |
