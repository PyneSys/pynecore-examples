# 05 — FreqTrade + PyneCore Indicators

Use **Pine Script indicators** as data sources inside your FreqTrade strategy. You write
the trading logic in Python — PyneCore handles the indicator math.

This is the most flexible integration: grab any indicator from TradingView, compile it with
[PyneComp](https://pynesys.io), and plug it into your FreqTrade bot.

## Standalone Demo (no FreqTrade needed)

```bash
uv run run.py
```

Generates 500 BTC/USDT candles, runs RSI + Bollinger Bands, and prints combined signals.

## Use in FreqTrade

1. Copy these files into your FreqTrade project:

   ```
   user_data/strategies/
   ├── strategy.py           # Your FreqTrade strategy
   ├── pynecore_bridge.py    # DataFrame ↔ PyneCore bridge
   └── scripts/
       ├── rsi.py
       └── bollinger_bands.py
   ```

2. Add PyneCore to your FreqTrade environment:

   ```bash
   pip install pynesys-pynecore
   ```

3. Run a backtest:

   ```bash
   freqtrade backtesting --strategy PyneIndicatorStrategy
   ```

## How It Works

```
FreqTrade DataFrame (pandas)
        │
        ▼
  pynecore_bridge.py
  ├── dataframe_to_ohlcv()   →  Convert rows to OHLCV objects
  ├── create_syminfo()        →  Build symbol metadata
  └── run_indicator()         →  Run script, return pd.Series
        │
        ▼
  ScriptRunner.run_iter()     →  Process each bar through the Pine Script
        │
        ▼
  plot_data dict              →  {"RSI": 45.2, "Upper": 43100.5, ...}
        │
        ▼
  Back to DataFrame columns   →  df["rsi"], df["bb_upper"], ...
```

## Adding Your Own Indicators

1. Compile a Pine Script indicator with PyneComp (or write one by hand)
2. Place the `.py` file in `scripts/`
3. Call `run_indicator()` in `populate_indicators()`:

   ```python
   macd_data = run_indicator(dataframe, SCRIPTS_DIR / "my_macd.py", pair=pair, timeframe=self.timeframe)
   dataframe["macd"] = macd_data.get("MACD")
   dataframe["signal"] = macd_data.get("Signal")
   ```

4. Use the new columns in `populate_entry_trend()` / `populate_exit_trend()`

## Performance Tip

FreqTrade calls `populate_indicators()` on every new candle with the full DataFrame. The simple
approach in this example re-runs PyneCore on all bars each time — which is fine for hourly
timeframes (~200 bars takes a few milliseconds).

For lower timeframes or many indicators, you can **cache results** in the strategy: store computed
indicator values keyed by bar timestamp, and only run PyneCore on new bars. The cached values
get returned instantly, and only the latest candle triggers actual computation. This makes the
integration essentially zero-cost after the initial warmup.
