"""
Bridge between FreqTrade's DataFrame world and PyneCore's OHLCV iterator world.

Provides helper functions to:
  - Convert a pandas DataFrame to PyneCore OHLCV objects
  - Build a SymInfo for crypto pairs
  - Run PyneCore indicator scripts on a DataFrame
  - Run PyneCore strategy scripts and capture trades
"""

from pathlib import Path
from typing import Any

import pandas as pd

from pynecore.core.script_runner import ScriptRunner
from pynecore.core.syminfo import SymInfo
from pynecore.types.ohlcv import OHLCV


# FreqTrade timeframe string → PyneCore period (minutes as string, or D/W/M)
TIMEFRAME_MAP = {
    "1m": "1", "3m": "3", "5m": "5", "15m": "15", "30m": "30",
    "1h": "60", "2h": "120", "4h": "240", "6h": "360", "8h": "480", "12h": "720",
    "1d": "D", "3d": "3D", "1w": "W", "1M": "M",
}


def dataframe_to_ohlcv(dataframe: pd.DataFrame) -> list[OHLCV]:
    """
    Convert a FreqTrade-style DataFrame to a list of PyneCore OHLCV objects.

    Expects columns: open, high, low, close, volume.
    Index should be a DatetimeIndex (timezone-aware or naive).

    :param dataframe: OHLCV DataFrame
    :return: List of OHLCV namedtuples
    """
    ohlcv_list = []
    for row in dataframe.itertuples():
        ts = int(row.Index.timestamp()) if hasattr(row.Index, "timestamp") else int(row.Index)
        ohlcv_list.append(OHLCV(
            timestamp=ts,
            open=float(row.open),
            high=float(row.high),
            low=float(row.low),
            close=float(row.close),
            volume=float(row.volume),
        ))
    return ohlcv_list


def create_syminfo(pair: str = "BTC/USDT", timeframe: str = "1h") -> SymInfo:
    """
    Create a SymInfo for a crypto trading pair.

    :param pair: Trading pair (e.g. "BTC/USDT", "ETH/BTC")
    :param timeframe: FreqTrade timeframe string (e.g. "1h", "4h", "1d")
    :return: Configured SymInfo
    """
    base, quote = pair.split("/") if "/" in pair else (pair[:-4], pair[-4:])

    return SymInfo(
        prefix="FREQTRADE",
        description=f"{base} / {quote}",
        ticker=pair.replace("/", ""),
        currency=quote,
        basecurrency=base,
        period=TIMEFRAME_MAP.get(timeframe, "60"),
        type="crypto",
        mintick=0.01,
        pricescale=100,
        minmove=1,
        pointvalue=1.0,
        timezone="UTC",
        volumetype="base",
        opening_hours=[],
        session_starts=[],
        session_ends=[],
    )


def run_indicator(
    dataframe: pd.DataFrame,
    script_path: Path,
    pair: str = "BTC/USDT",
    timeframe: str = "1h",
    inputs: dict[str, Any] | None = None,
) -> dict[str, pd.Series]:
    """
    Run a PyneCore indicator script on a FreqTrade DataFrame.

    Returns a dictionary of pandas Series — one per plot() call in the script.
    Keys are the plot titles (e.g. "RSI", "Basis", "Upper").

    :param dataframe: OHLCV DataFrame
    :param script_path: Path to a compiled PyneCore indicator script
    :param pair: Trading pair
    :param timeframe: FreqTrade timeframe string
    :param inputs: Optional dict to override script input() defaults
    :return: Dict mapping plot title → pd.Series of values
    """
    ohlcv_data = dataframe_to_ohlcv(dataframe)
    syminfo = create_syminfo(pair, timeframe)

    runner = ScriptRunner(
        script_path=script_path,
        ohlcv_iter=ohlcv_data,
        syminfo=syminfo,
        inputs=inputs,
    )

    results: dict[str, list] = {}
    for _ohlcv, plot_data in runner.run_iter():
        for key, value in plot_data.items():
            results.setdefault(key, []).append(value)

    return {
        key: pd.Series(values, index=dataframe.index[:len(values)])
        for key, values in results.items()
    }


def run_strategy(
    dataframe: pd.DataFrame,
    script_path: Path,
    pair: str = "BTC/USDT",
    timeframe: str = "1h",
    inputs: dict[str, Any] | None = None,
) -> tuple[dict[str, pd.Series], list]:
    """
    Run a PyneCore strategy script on a FreqTrade DataFrame.

    Returns indicator values AND closed trades. Strategies yield a 3-tuple
    (candle, plot_data, new_trades) from run_iter().

    :param dataframe: OHLCV DataFrame
    :param script_path: Path to a compiled PyneCore strategy script
    :param pair: Trading pair
    :param timeframe: FreqTrade timeframe string
    :param inputs: Optional dict to override script input() defaults
    :return: Tuple of (indicator_dict, list_of_closed_trades)
    """
    ohlcv_data = dataframe_to_ohlcv(dataframe)
    syminfo = create_syminfo(pair, timeframe)

    runner = ScriptRunner(
        script_path=script_path,
        ohlcv_iter=ohlcv_data,
        syminfo=syminfo,
        inputs=inputs,
    )

    results: dict[str, list] = {}
    all_trades: list = []

    for _ohlcv, plot_data, new_trades in runner.run_iter():
        for key, value in plot_data.items():
            results.setdefault(key, []).append(value)
        all_trades.extend(new_trades)

    indicators = {
        key: pd.Series(values, index=dataframe.index[:len(values)])
        for key, values in results.items()
    }
    return indicators, all_trades
