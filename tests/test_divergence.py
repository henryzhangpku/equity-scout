"""RSI divergence and pivots on hand-built series (every pivot and comparison worked out in comments)."""

import numpy as np

from scout import indicators as I


def test_pivots_strict_and_dated_at_the_pivot():
    #          0  1  2  3  4  5  6  7  8
    x = [1, 2, 3, 5, 3, 2, 1, 2, 3]
    hi, lo = I.pivots(x, k=3)
    # bar 3 (5) beats bars 0..2 and 4..6 -> pivot high; bar 6 (1) has only 2 bars after it -> not checkable
    assert list(np.nonzero(hi)[0]) == [3]
    assert not lo.any()


def test_ties_are_not_pivots():
    x = [1, 2, 3, 5, 5, 2, 1, 0, 0]
    hi, _ = I.pivots(x, k=3)
    assert not hi[3] and not hi[4]


def _two_peaks(p2, o1, o2):
    """Price peaks at bar 3 (10) and bar 10 (p2); oscillator values at those bars o1, o2."""
    price = [5, 6, 7, 10, 7, 6, 5, 6, 7, 8, p2, 8, 7, 6, 5]
    osc = [50.0] * len(price)
    osc[3], osc[10] = o1, o2
    return price, osc


def test_bearish_divergence_fires_on_the_confirmation_bar():
    # pivot highs at 3 and 10 (gap 7, inside 5..60); price 10 -> 12 higher high, RSI 80 -> 70 lower high
    price, osc = _two_peaks(12, 80, 70)
    bear, bull = I.divergence(price, osc, k=3)
    # the second pivot is only known 3 bars later: bar 13
    assert list(np.nonzero(bear)[0]) == [13]
    assert not bull.any()


def test_no_divergence_when_rsi_confirms_or_price_fails():
    price, osc = _two_peaks(12, 70, 80)            # RSI higher high too: confirmation, not divergence
    assert not I.divergence(price, osc)[0].any()
    price, osc = _two_peaks(9, 80, 70)             # price lower high: no divergence
    assert not I.divergence(price, osc)[0].any()


def test_gap_limits():
    price, osc = _two_peaks(12, 80, 70)
    assert not I.divergence(price, osc, min_gap=8)[0].any()     # gap 7 < 8
    assert not I.divergence(price, osc, max_gap=6)[0].any()     # gap 7 > 6


def test_bullish_divergence_is_the_mirror():
    price, osc = _two_peaks(12, 80, 70)
    neg = [-p for p in price]                      # troughs at 3 (-10) and 10 (-12): lower low
    o = [100 - v for v in osc]                     # RSI 20 -> 30: higher low
    bear, bull = I.divergence(neg, o)
    assert list(np.nonzero(bull)[0]) == [13]
    assert not bear.any()


def test_divergence_uses_nothing_after_the_signal_bar():
    price, osc = _two_peaks(12, 80, 70)
    full_bear, _ = I.divergence(price, osc)
    # truncate the series at the confirmation bar: the signal is already there
    cut_bear, _ = I.divergence(price[:14], osc[:14])
    assert cut_bear[13] and full_bear[13]
    # one bar earlier the second pivot is not yet confirmed
    assert not I.divergence(price[:13], osc[:13])[0].any()
