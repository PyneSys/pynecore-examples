# 04 — Live Data with CCXT

Fetch live OHLCV data from a crypto exchange and run a PyneCore indicator on it in real time.
No API keys needed — uses public market data.

## Run

```bash
uv run run.py
```

This will:
1. Fetch the last 100 closed BTC/USDT 1-minute candles from Binance
2. Run RSI on the historical data (warmup)
3. Poll every 10 seconds and process each newly closed candle, until 3 have arrived (about 3 minutes)

Only closed candles are fed to the script: the exchange also returns the candle that is still
forming, whose values change until it closes.

The runner works in live mode (`ScriptRunner(..., live=True)`). The generator yields the
history, then `LIVE_TRANSITION`, then the new candles, and each new candle's RSI is printed right
after the candle arrives. Without live mode the runner treats the feed as history: it reads one
bar ahead to know which bar is the last, so every result would come one candle late.

Requires PyneCore 6.10.7 or newer (`live=True`).

## Configuration

Edit the constants at the top of `run.py`:

```python
EXCHANGE = "binance"          # any CCXT-supported exchange
SYMBOL = "BTC/USDT"           # trading pair
TIMEFRAME = "1m"              # candle timeframe (CCXT notation)
PERIOD = "1"                  # the same timeframe as a Pine Script period ("60" = 1h, "D" = 1 day)
HISTORY_BARS = 100            # closed historical bars for indicator warmup
LIVE_BARS = 3                 # number of new closed bars to wait for
POLL_INTERVAL_SEC = 10        # seconds between polls
```

## Supported Exchanges

CCXT supports 100+ exchanges. Just change the `EXCHANGE` variable:

```python
EXCHANGE = "coinbase"         # Coinbase
EXCHANGE = "kraken"           # Kraken
EXCHANGE = "bybit"            # Bybit
EXCHANGE = "okx"              # OKX
```

## Next Steps

- Replace polling with **websocket streaming** for real-time updates: yield
  `OHLCV(..., is_closed=False)` for each price update of the forming candle and
  `is_closed=True` when it closes
- Add **multiple indicators** by creating more scripts
- Connect to a **trading bot** (see [`05-freqtrade-indicators/`](../05-freqtrade-indicators/) for a complete example)
