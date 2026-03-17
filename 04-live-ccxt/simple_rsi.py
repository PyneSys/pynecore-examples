# /// script
# requires-python = ">=3.11"
# dependencies = ["pynesys-pynecore[cli]"]
# ///

"""
@pyne

Simple RSI indicator — a minimal example for demonstrating custom data feeds.
"""
from pynecore.lib import close, input, plot, script, ta


@script.indicator(title="Simple RSI", overlay=False)
def main(
    length=input.int(14, "RSI Length", minval=1),
):
    rsi = ta.rsi(close, length)
    plot(rsi, "RSI")
    plot(70, "Overbought")
    plot(30, "Oversold")


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
