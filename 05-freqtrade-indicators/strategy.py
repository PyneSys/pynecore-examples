"""
FreqTrade strategy using PyneCore indicators as data sources.

Drop this file into FreqTrade's user_data/strategies/ directory.
Copy pynecore_bridge.py and the scripts/ folder alongside it.

The trading logic is written entirely in Python — PyneCore only provides
the indicator calculations (RSI, Bollinger Bands, etc.).
"""

from pathlib import Path

import pandas as pd

try:
    from freqtrade.strategy import IStrategy
except ImportError:
    raise ImportError(
        "FreqTrade is not installed. This file is meant to be used inside FreqTrade.\n"
        "For a standalone demo, run: uv run run.py"
    )

from pynecore_bridge import run_indicator

SCRIPTS_DIR = Path(__file__).parent / "scripts"


class PyneIndicatorStrategy(IStrategy):
    """
    FreqTrade strategy that uses PyneCore Pine Script indicators
    for calculations and Python for entry/exit logic.

    Indicators used:
      - RSI (14) — momentum / overbought / oversold
      - Bollinger Bands (20, 2.0) — volatility / price levels
    """

    INTERFACE_VERSION = 3

    timeframe = "1h"
    startup_candle_count = 50

    minimal_roi = {"0": 0.10, "60": 0.05, "120": 0.02}
    stoploss = -0.05
    can_short = False

    def populate_indicators(
        self, dataframe: pd.DataFrame, metadata: dict
    ) -> pd.DataFrame:
        pair = metadata.get("pair", "BTC/USDT")

        # Run RSI indicator
        rsi_data = run_indicator(
            dataframe,
            SCRIPTS_DIR / "rsi.py",
            pair=pair,
            timeframe=self.timeframe,
        )
        dataframe["rsi"] = rsi_data.get("RSI")

        # Run Bollinger Bands indicator
        bb_data = run_indicator(
            dataframe,
            SCRIPTS_DIR / "bollinger_bands.py",
            pair=pair,
            timeframe=self.timeframe,
        )
        dataframe["bb_upper"] = bb_data.get("Upper")
        dataframe["bb_basis"] = bb_data.get("Basis")
        dataframe["bb_lower"] = bb_data.get("Lower")

        return dataframe

    def populate_entry_trend(
        self, dataframe: pd.DataFrame, metadata: dict
    ) -> pd.DataFrame:
        dataframe.loc[
            (dataframe["rsi"] < 30)
            & (dataframe["close"] <= dataframe["bb_lower"] * 1.01),
            "enter_long",
        ] = 1
        return dataframe

    def populate_exit_trend(
        self, dataframe: pd.DataFrame, metadata: dict
    ) -> pd.DataFrame:
        dataframe.loc[
            (dataframe["rsi"] > 70)
            & (dataframe["close"] >= dataframe["bb_upper"] * 0.99),
            "exit_long",
        ] = 1
        return dataframe
