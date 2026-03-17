"""
FreqTrade strategy that uses PyneCore strategy signals directly.

The Pine Script strategy (SMA Crossover) generates entry/exit decisions via
strategy.entry() and strategy.close(). This FreqTrade wrapper converts those
trade signals into enter_long / exit_long DataFrame columns.

Drop this file into FreqTrade's user_data/strategies/ directory.
Copy pynecore_bridge.py and the scripts/ folder alongside it.
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

from pynecore_bridge import run_strategy

SCRIPT = Path(__file__).parent / "scripts" / "sma_crossover.py"


class PyneStrategySignals(IStrategy):
    """
    FreqTrade strategy powered by Pine Script strategy signals.

    The SMA Crossover strategy generates long/short entries based on
    price crossing above/below a simple moving average. PyneCore executes
    the strategy logic and returns trade signals that FreqTrade acts on.
    """

    INTERFACE_VERSION = 3

    timeframe = "1h"
    startup_candle_count = 50

    minimal_roi = {"0": 100}  # Disable ROI — let Pine Script control exits
    stoploss = -0.10
    can_short = True

    def populate_indicators(
        self, dataframe: pd.DataFrame, metadata: dict
    ) -> pd.DataFrame:
        pair = metadata.get("pair", "BTC/USDT")

        _indicators, trades = run_strategy(
            dataframe,
            SCRIPT,
            pair=pair,
            timeframe=self.timeframe,
            inputs={"Length": 12, "Confirm bars": 1},
        )

        # Convert PyneCore trades into bar-level entry/exit signals
        dataframe["pyne_enter_long"] = 0
        dataframe["pyne_enter_short"] = 0
        dataframe["pyne_exit_long"] = 0
        dataframe["pyne_exit_short"] = 0

        for trade in trades:
            entry_idx = trade.entry_bar_index
            exit_idx = trade.exit_bar_index

            if entry_idx < len(dataframe):
                if trade.size > 0:
                    dataframe.iloc[entry_idx, dataframe.columns.get_loc("pyne_enter_long")] = 1
                else:
                    dataframe.iloc[entry_idx, dataframe.columns.get_loc("pyne_enter_short")] = 1

            if exit_idx < len(dataframe):
                if trade.size > 0:
                    dataframe.iloc[exit_idx, dataframe.columns.get_loc("pyne_exit_long")] = 1
                else:
                    dataframe.iloc[exit_idx, dataframe.columns.get_loc("pyne_exit_short")] = 1

        return dataframe

    def populate_entry_trend(
        self, dataframe: pd.DataFrame, metadata: dict
    ) -> pd.DataFrame:
        dataframe.loc[dataframe["pyne_enter_long"] == 1, "enter_long"] = 1
        dataframe.loc[dataframe["pyne_enter_short"] == 1, "enter_short"] = 1
        return dataframe

    def populate_exit_trend(
        self, dataframe: pd.DataFrame, metadata: dict
    ) -> pd.DataFrame:
        dataframe.loc[dataframe["pyne_exit_long"] == 1, "exit_long"] = 1
        dataframe.loc[dataframe["pyne_exit_short"] == 1, "exit_short"] = 1
        return dataframe
