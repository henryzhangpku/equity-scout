# Learning loop run: loop-2026-10-12-llm

Proposer: **llm (deepseek/deepseek-v4-pro)**. Data: daily adjusted closes for 500 US companies, 2021-12-01 to 2026-10-08 (1218 sessions, sha256 2f9f3237eb38).
Split fixed before the first hypothesis: discovery = holding periods ending on or before 2024-12-31; out-of-sample = signals from 2025-01-01. Costs 10 bps per side. Budget K = 5 tries, Bonferroni: each test needs one-sided p < 0.0100.

Stopped: step budget of 5 used. Tried 5; promoted 0; out-of-sample opened for 0.

## Every attempt (discovery results; this is all the proposer saw)

| Step | Hypothesis | Rule | Events | Hit rate | Signal return | Universe | Excess after costs | t | p | Sharpe-like | Decision |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | rsi_macd_cross_mean_reversion | long when RSI(14) < 30 and MACD crosses above its signal within the last 3 bars; short when RSI(14) > 70 and MACD crosses below its signal within the last 3 bars (daily bars); hold 10 days | 1264 | 46.76% | +0.40% | +0.46% | -0.26% | -0.33 | 0.6284 | -0.22 | **reject** |
| 2 | macd_hist_momentum_rsi_filter | long when MACD histogram > 0 and RSI(14) > 50 and RSI(14) < 70; short when MACD histogram < 0 and RSI(14) < 50 and RSI(14) > 30 (daily bars); hold 10 days | 224674 | 47.97% | -0.09% | -0.05% | -0.25% | -3.37 | 0.9996 | -1.95 | **reject** |
| 3 | weekly_rsi_divergence_reversal | long when bullish RSI divergence (price lower low, RSI higher low) within the last 5 bars and RSI(14) < 45; short when bearish RSI divergence (price higher high, RSI lower high) within the last 5 bars and RSI(14) > 55 (weekly bars); hold 5 days | 2926 | 48.02% | +0.42% | +0.25% | -0.03% | -1.16 | 0.8762 | -0.72 | **reject** |
| 4 | daily_divergence_macd_cross | long when bullish RSI divergence (price lower low, RSI higher low) within the last 3 bars and MACD crosses above its signal; short when bearish RSI divergence (price higher high, RSI lower high) within the last 3 bars and MACD crosses below its signal (daily bars); hold 10 days | 1903 | 47.87% | +0.68% | +0.50% | -0.02% | -0.60 | 0.7265 | -0.35 | **reject** |
| 5 | deep_rsi_extreme_mean_reversion | long when RSI(14) < 25; short when RSI(14) > 75 (daily bars); hold 10 days | 15036 | 45.68% | +0.26% | +0.52% | -0.45% | -0.98 | 0.8365 | -0.57 | **reject** |

Signal return and universe are signed by side (a short earns the negative of the return), per event, before costs; excess is after a round-trip cost.

## Reasons

1. rsi_macd_cross_mean_reversion: discovery: mean excess after costs is not positive (-0.26%); out-of-sample not opened
2. macd_hist_momentum_rsi_filter: discovery: mean excess after costs is not positive (-0.25%); out-of-sample not opened
3. weekly_rsi_divergence_reversal: discovery: mean excess after costs is not positive (-0.03%); out-of-sample not opened
4. daily_divergence_macd_cross: discovery: mean excess after costs is not positive (-0.02%); out-of-sample not opened
5. deep_rsi_extreme_mean_reversion: discovery: mean excess after costs is not positive (-0.45%); out-of-sample not opened

## Out-of-sample (opened only for hypotheses that passed discovery)

None passed discovery, so the out-of-sample period was never opened. It stays sealed for the next idea.

## Verdict

Nothing survived. 5 hypotheses were tried against a bar corrected for 5 tries, and none cleared it in discovery and then out-of-sample. That is the loop doing its job: an idea that only looks good because many were tried is rejected and recorded, so it is not tried again.

Caveats: survivorship (companies listed on 2026-10-08 only); under five years of daily history (the data starts 2021-12-01); adjusted closes, no slippage beyond the stated cost; events overlap across names on the same day, which the block statistics only partly absorb.
