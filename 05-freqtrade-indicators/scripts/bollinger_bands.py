"""
@pyne

Bollinger Bands indicator — compiled from TradingView's built-in Pine Script.
"""
from pynecore.lib import close, color, display, fill, input, na, plot, script, ta
from pynecore.types import Series


@script.indicator(shorttitle="BB", title="Bollinger Bands", overlay=True, timeframe="", timeframe_gaps=True)
def main(
    length=input.int(20, minval=1),
    maType=input.string("SMA", "Basis MA Type", options=("SMA", "EMA", "SMMA (RMA)", "WMA", "VWMA")),
    src: Series[float] = input(close, title="Source"),
    mult=input.float(2.0, minval=0.001, maxval=50, title="StdDev"),
    offset=input.int(0, "Offset", minval=-500, maxval=500, display=display.data_window)
):
    def ma(source, length, _type):
        __block_result__ = na
        match _type:
            case "SMA":
                __block_result__ = ta.sma(source, length)
            case "EMA":
                __block_result__ = ta.ema(source, length)
            case "SMMA (RMA)":
                __block_result__ = ta.rma(source, length)
            case "WMA":
                __block_result__ = ta.wma(source, length)
            case "VWMA":
                __block_result__ = ta.vwma(source, length)
        return __block_result__

    basis = ma(src, length, maType)
    dev = mult * ta.stdev(src, length)
    upper = basis + dev
    lower = basis - dev
    plot(basis, 'Basis', color=color.new('#2962FF'), offset=offset)
    p1 = plot(upper, 'Upper', color=color.new('#F23645'), offset=offset)
    p2 = plot(lower, 'Lower', color=color.new('#089981'), offset=offset)
    fill(p1, p2, title='Background', color=color.rgb(33, 150, 243, 95))


if __name__ == "__main__":
    from pynecore.standalone import run
    run(__file__)
