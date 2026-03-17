# 03 — Custom Data Feed

Feed OHLCV data from **any source** into PyneCore — no CSV files, no file conversion. Just create
`OHLCV` objects and pass them to `ScriptRunner`.

## Run

```bash
uv run run.py
```

## What You'll Learn

- **Create OHLCV objects** — `OHLCV(timestamp, open, high, low, close, volume)`
  - `timestamp` is in **seconds** (Unix epoch)
- **Build SymInfo manually** — no TOML file needed; just set ticker, currency, mintick, etc.
- **Use any data source** — the `ohlcv_iter` parameter accepts any `Iterable[OHLCV]`

## Adapting to Your Data Source

Replace `generate_candles()` with your own data source:

```python
# From a REST API
def fetch_from_api():
    response = requests.get("https://api.exchange.com/ohlcv/BTCUSD/1h")
    for bar in response.json():
        yield OHLCV(
            timestamp=bar["time"],
            open=bar["o"], high=bar["h"], low=bar["l"], close=bar["c"],
            volume=bar["v"],
        )

# From a pandas DataFrame
def from_dataframe(df):
    for _, row in df.iterrows():
        yield OHLCV(
            timestamp=int(row["timestamp"].timestamp()),
            open=row["open"], high=row["high"], low=row["low"], close=row["close"],
            volume=row["volume"],
        )

# From a database
def from_database(cursor):
    cursor.execute("SELECT ts, o, h, l, c, vol FROM candles ORDER BY ts")
    for row in cursor:
        yield OHLCV(timestamp=row[0], open=row[1], high=row[2], low=row[3],
                     close=row[4], volume=row[5])
```
