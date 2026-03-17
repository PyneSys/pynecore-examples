# 04 — Live Data with CCXT

Fetch live OHLCV data from a crypto exchange and run a PyneCore indicator on it in real time.
No API keys needed — uses public market data.

## Run

```bash
uv run run.py
```

This will:
1. Fetch 100 historical BTC/USDT 1h candles from Binance
2. Run RSI on the historical data (warmup)
3. Poll for new candles every 10 seconds and process them live

## Configuration

Edit the constants at the top of `run.py`:

```python
EXCHANGE = "binance"          # any CCXT-supported exchange
SYMBOL = "BTC/USDT"           # trading pair
TIMEFRAME = "1h"              # candle timeframe
HISTORY_BARS = 100            # historical bars for indicator warmup
LIVE_UPDATES = 5              # number of live poll cycles
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

- Replace polling with **websocket streaming** for real-time updates
- Add **multiple indicators** by creating more scripts
- Connect to a **trading bot** (see `05-freqtrade/` for a complete example)
