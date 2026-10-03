"""
FreqTrade strategy that uses PyneCore strategy signals directly.

The Pine Script strategy (SMA Crossover) generates entry/exit decisions via
strategy.entry() and strategy.close(). This FreqTrade wrapper converts those
trades into enter_long/short and exit_long/short DataFrame columns.

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

# The script's input values, keyed by its main() parameter names
INPUTS = {"length": 12, "confirmBars": 1}

# The strategy's own settings, overridden for this integration:
# - 10% of equity per entry instead of Pine's default 100%, which leaves no room for
#   adverse moves (margin calls)
# - process_orders_on_close: an order fills on the close of the bar that placed it, so a
#   trade's entry/exit bar IS the signal bar. Without it Pine fills at the NEXT bar's open,
#   and a signal on the newest candle would only show up one candle later.
SETTINGS = {
    "default_qty_type": "percent_of_equity",
    "default_qty_value": 10,
    "process_orders_on_close": True,
}


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

        _indicators, closed_trades, open_trades = run_strategy(
            dataframe,
            SCRIPT,
            pair=pair,
            timeframe=self.timeframe,
            inputs=INPUTS,
            settings=SETTINGS,
        )

        # Convert PyneCore trades into bar-level entry/exit signals. FreqTrade acts on a
        # signal at the next candle's open. The open trades matter most when trading live:
        # the position the strategy holds right now is not closed yet.
        dataframe["pyne_enter_long"] = 0
        dataframe["pyne_enter_short"] = 0
        dataframe["pyne_exit_long"] = 0
        dataframe["pyne_exit_short"] = 0

        def mark(bar_index: int, column: str) -> None:
            if bar_index < len(dataframe):
                dataframe.iloc[bar_index, dataframe.columns.get_loc(column)] = 1

        for trade in closed_trades + open_trades:
            mark(trade.entry_bar_index, "pyne_enter_long" if trade.size > 0 else "pyne_enter_short")
        for trade in closed_trades:
            mark(trade.exit_bar_index, "pyne_exit_long" if trade.size > 0 else "pyne_exit_short")

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
