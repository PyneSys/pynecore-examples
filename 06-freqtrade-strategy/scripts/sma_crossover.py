"""
@pyne

SMA Crossover strategy — compiled from TradingView's built-in Pine Script.
"""
from pynecore.lib import close, input, nz, script, strategy, ta
from pynecore.types import Series


@script.strategy("MovingAvg Cross", overlay=True)
def main(
    length=input(9, "Length"),
    confirmBars=input(1, "Confirm bars")
):
    price = close
    ma = ta.sma(price, length)
    bcond = price > ma
    bcount: Series[int] = 0
    bcount = nz(bcount[1]) + 1 if bcond else 0
    if bcount == confirmBars:
        strategy.entry('MACrossLE', strategy.long, comment='MACrossLE')
    scond = price < ma
    scount: Series[int] = 0
    scount = nz(scount[1]) + 1 if scond else 0
    if scount == confirmBars:
        strategy.entry('MACrossSE', strategy.short, comment='MACrossSE')


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
