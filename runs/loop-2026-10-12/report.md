# Learning loop run: loop-2026-10-12

Proposer: **scripted**. Data: daily adjusted closes for 500 US companies, 2021-12-01 to 2026-10-08 (1218 sessions, sha256 2f9f3237eb38).
Split fixed before the first hypothesis: discovery = holding periods ending on or before 2024-12-31; out-of-sample = signals from 2025-01-01. Costs 10 bps per side. Budget K = 10 tries, Bonferroni: each test needs one-sided p < 0.0050.

Stopped: step budget of 10 used. Tried 10; promoted 0; out-of-sample opened for 0.

## Every attempt (discovery results; this is all the proposer saw)

| Step | Hypothesis | Rule | Events | Hit rate | Signal return | Universe | Excess after costs | t | p | Sharpe-like | Decision |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | rsi_overbought | short when RSI(14) > 70 (daily bars); hold 10 days | 26084 | 46.38% | -0.24% | +0.03% | -0.48% | -0.33 | 0.6292 | -0.21 | **reject** |
| 2 | rsi_oversold | long when RSI(14) < 30 (daily bars); hold 10 days | 15017 | 45.71% | +1.11% | +1.15% | -0.23% | -1.20 | 0.8856 | -0.76 | **reject** |
| 3 | rsi_divergence | long when bullish RSI divergence (price lower low, RSI higher low); short when bearish RSI divergence (price higher high, RSI lower high) (daily bars); hold 10 days | 5749 | 48.56% | +0.54% | +0.47% | -0.12% | -0.79 | 0.7843 | -0.48 | **reject** |
| 4 | overbought_macd_cross | short when RSI(14) > 70 within the last 5 bars and MACD crosses below its signal (daily bars); hold 10 days | 2360 | 47.50% | -0.02% | +0.19% | -0.41% | -0.16 | 0.5626 | -0.10 | **reject** |
| 5 | oversold_macd_cross | long when RSI(14) < 30 within the last 5 bars and MACD crosses above its signal (daily bars); hold 10 days | 1452 | 48.55% | +0.55% | +0.54% | -0.19% | -1.36 | 0.9123 | -0.86 | **reject** |
| 6 | divergence_macd_cross | long when bullish RSI divergence (price lower low, RSI higher low) within the last 5 bars and MACD crosses above its signal; short when bearish RSI divergence (price higher high, RSI lower high) within the last 5 bars and MACD crosses below its signal (daily bars); hold 10 days | 2389 | 47.68% | +0.54% | +0.52% | -0.18% | -1.08 | 0.8595 | -0.67 | **reject** |
| 7 | overbought_macd_state | short when RSI(14) > 70 and MACD histogram < 0 (daily bars); hold 10 days | 1710 | 47.60% | +0.02% | +0.05% | -0.23% | -1.04 | 0.8505 | -0.74 | **reject** |
| 8 | oversold_macd_state | long when RSI(14) < 30 and MACD histogram > 0 (daily bars); hold 10 days | 1504 | 44.22% | +0.61% | +0.51% | -0.10% | -0.30 | 0.6163 | -0.19 | **reject** |
| 9 | divergence_macd_state | long when bullish RSI divergence (price lower low, RSI higher low) and MACD histogram > 0; short when bearish RSI divergence (price higher high, RSI lower high) and MACD histogram < 0 (daily bars); hold 10 days | 3637 | 48.28% | +0.34% | +0.35% | -0.21% | -0.55 | 0.7091 | -0.33 | **reject** |
| 10 | overbought_macd_cross_refined | short when RSI(14) > 75 within the last 5 bars and MACD crosses below its signal (daily bars); hold 10 days | 919 | 48.97% | -0.14% | +0.13% | -0.47% | -1.26 | 0.8955 | -0.81 | **reject** |

Signal return and universe are signed by side (a short earns the negative of the return), per event, before costs; excess is after a round-trip cost.

## Reasons

1. rsi_overbought: discovery: mean excess after costs is not positive (-0.48%); out-of-sample not opened
2. rsi_oversold: discovery: mean excess after costs is not positive (-0.23%); out-of-sample not opened
3. rsi_divergence: discovery: mean excess after costs is not positive (-0.12%); out-of-sample not opened
4. overbought_macd_cross: discovery: mean excess after costs is not positive (-0.41%); out-of-sample not opened
5. oversold_macd_cross: discovery: mean excess after costs is not positive (-0.19%); out-of-sample not opened
6. divergence_macd_cross: discovery: mean excess after costs is not positive (-0.18%); out-of-sample not opened
7. overbought_macd_state: discovery: mean excess after costs is not positive (-0.23%); out-of-sample not opened
8. oversold_macd_state: discovery: mean excess after costs is not positive (-0.10%); out-of-sample not opened
9. divergence_macd_state: discovery: mean excess after costs is not positive (-0.21%); out-of-sample not opened
10. overbought_macd_cross_refined: discovery: mean excess after costs is not positive (-0.47%); out-of-sample not opened

## Out-of-sample (opened only for hypotheses that passed discovery)

None passed discovery, so the out-of-sample period was never opened. It stays sealed for the next idea.

## What the loop learned (discovery only)

* rsi_overbought: alone t = -0.33 on 26084 events, mean excess -0.48%; with a MACD cross t = -0.16 on 2360 events, mean excess -0.41%; with the MACD histogram sign t = -1.04 on 1710 events, mean excess -0.23%
* rsi_oversold: alone t = -1.20 on 15017 events, mean excess -0.23%; with a MACD cross t = -1.36 on 1452 events, mean excess -0.19%; with the MACD histogram sign t = -0.30 on 1504 events, mean excess -0.10%
* rsi_divergence: alone t = -0.79 on 5749 events, mean excess -0.12%; with a MACD cross t = -1.08 on 2389 events, mean excess -0.18%; with the MACD histogram sign t = -0.55 on 3637 events, mean excess -0.21%

## Verdict

Nothing survived. 10 hypotheses were tried against a bar corrected for 10 tries, and none cleared it in discovery and then out-of-sample. That is the loop doing its job: an idea that only looks good because many were tried is rejected and recorded, so it is not tried again.

Caveats: survivorship (companies listed on 2026-10-08 only); under five years of daily history (the data starts 2021-12-01); adjusted closes, no slippage beyond the stated cost; events overlap across names on the same day, which the block statistics only partly absorb.
