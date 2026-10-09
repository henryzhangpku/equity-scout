window.SCOUT_FIELDS = {"market_cap": {"kind": "usd", "desc": "price x latest shares outstanding (SEC cover page), as of the run date", "label": "Market cap"}, "ev": {"kind": "usd", "desc": "enterprise value = market cap + total debt - cash and short-term investments", "label": "Enterprise value"}, "close": {"kind": "usd", "desc": "last adjusted close", "label": "Price"}, "avg_dollar_volume_50d": {"kind": "usd", "desc": "mean of close x volume over the last 50 sessions", "label": "Avg daily $ volume (50 days)"}, "sma20": {"kind": "usd", "desc": "20-day simple moving average of close", "label": "20-day average"}, "sma50": {"kind": "usd", "desc": "50-day simple moving average of close", "label": "50-day average"}, "sma200": {"kind": "usd", "desc": "200-day simple moving average of close", "label": "200-day average"}, "pct_vs_sma20": {"kind": "ratio", "desc": "close / SMA20 - 1", "label": "Price vs 20-day average"}, "pct_vs_sma50": {"kind": "ratio", "desc": "close / SMA50 - 1", "label": "Price vs 50-day average"}, "pct_vs_sma200": {"kind": "ratio", "desc": "close / SMA200 - 1", "label": "Price vs 200-day average"}, "sma50_above_sma200": {"kind": "bool", "desc": "true when SMA50 > SMA200 (golden-cross structure)", "label": "50-day above 200-day average"}, "rsi14": {"kind": "number", "desc": "Wilder RSI(14), 0-100", "label": "RSI (14-day)"}, "macd": {"kind": "number", "desc": "MACD line, EMA12 - EMA26 of close", "label": "MACD"}, "macd_signal": {"kind": "number", "desc": "EMA9 of the MACD line", "label": "MACD signal"}, "macd_hist": {"kind": "number", "desc": "MACD - signal; > 0 means MACD above its signal", "label": "MACD minus signal"}, "volume_ratio_50d": {"kind": "number", "desc": "today's volume / mean volume of the prior 50 sessions", "label": "Volume vs 50-day average"}, "drawdown_52w": {"kind": "ratio", "desc": "close / 52-week (252-session) high close - 1; -0.20 = 20% below the high", "label": "From 52-week high"}, "mom_1m": {"kind": "ratio", "desc": "1-month price return (21 sessions)", "label": "1-month return"}, "mom_3m": {"kind": "ratio", "desc": "3-month price return (63 sessions)", "label": "3-month return"}, "mom_6m": {"kind": "ratio", "desc": "6-month price return (126 sessions)", "label": "6-month return"}, "mom_12m": {"kind": "ratio", "desc": "12-month price return (252 sessions)", "label": "12-month return"}, "rs_1m_vs_spy": {"kind": "ratio", "desc": "1-month return minus SPY (S&P 500) 1-month return (negative = lagging)", "label": "1-month return vs the S&P 500 (SPY)"}, "rs_3m_vs_spy": {"kind": "ratio", "desc": "3-month return minus SPY (S&P 500) 3-month return (negative = lagging)", "label": "3-month return vs the S&P 500 (SPY)"}, "rs_6m_vs_spy": {"kind": "ratio", "desc": "6-month return minus SPY (S&P 500) 6-month return (negative = lagging)", "label": "6-month return vs the S&P 500 (SPY)"}, "rs_12m_vs_spy": {"kind": "ratio", "desc": "12-month return minus SPY (S&P 500) 12-month return (negative = lagging)", "label": "12-month return vs the S&P 500 (SPY)"}, "rs_1m_vs_qqq": {"kind": "ratio", "desc": "1-month return minus QQQ (Nasdaq-100) 1-month return (negative = lagging)", "label": "1-month return vs the Nasdaq-100 (QQQ)"}, "rs_3m_vs_qqq": {"kind": "ratio", "desc": "3-month return minus QQQ (Nasdaq-100) 3-month return (negative = lagging)", "label": "3-month return vs the Nasdaq-100 (QQQ)"}, "rs_6m_vs_qqq": {"kind": "ratio", "desc": "6-month return minus QQQ (Nasdaq-100) 6-month return (negative = lagging)", "label": "6-month return vs the Nasdaq-100 (QQQ)"}, "rs_12m_vs_qqq": {"kind": "ratio", "desc": "12-month return minus QQQ (Nasdaq-100) 12-month return (negative = lagging)", "label": "12-month return vs the Nasdaq-100 (QQQ)"}, "rs_1m_vs_iwm": {"kind": "ratio", "desc": "1-month return minus IWM (Russell 2000) 1-month return (negative = lagging)", "label": "1-month return vs the Russell 2000 (IWM)"}, "rs_3m_vs_iwm": {"kind": "ratio", "desc": "3-month return minus IWM (Russell 2000) 3-month return (negative = lagging)", "label": "3-month return vs the Russell 2000 (IWM)"}, "rs_6m_vs_iwm": {"kind": "ratio", "desc": "6-month return minus IWM (Russell 2000) 6-month return (negative = lagging)", "label": "6-month return vs the Russell 2000 (IWM)"}, "rs_12m_vs_iwm": {"kind": "ratio", "desc": "12-month return minus IWM (Russell 2000) 12-month return (negative = lagging)", "label": "12-month return vs the Russell 2000 (IWM)"}, "rs_1m_vs_smh": {"kind": "ratio", "desc": "1-month return minus SMH (semiconductor ETF, MVIS US Listed Semiconductor 25) 1-month return (negative = lagging)", "label": "1-month return vs the chip index (SMH)"}, "rs_3m_vs_smh": {"kind": "ratio", "desc": "3-month return minus SMH (semiconductor ETF, MVIS US Listed Semiconductor 25) 3-month return (negative = lagging)", "label": "3-month return vs the chip index (SMH)"}, "rs_6m_vs_smh": {"kind": "ratio", "desc": "6-month return minus SMH (semiconductor ETF, MVIS US Listed Semiconductor 25) 6-month return (negative = lagging)", "label": "6-month return vs the chip index (SMH)"}, "rs_12m_vs_smh": {"kind": "ratio", "desc": "12-month return minus SMH (semiconductor ETF, MVIS US Listed Semiconductor 25) 12-month return (negative = lagging)", "label": "12-month return vs the chip index (SMH)"}, "rs_1m_vs_soxx": {"kind": "ratio", "desc": "1-month return minus SOXX (semiconductor ETF, NYSE Semiconductor Index) 1-month return (negative = lagging)", "label": "1-month return vs the chip index (SOXX)"}, "rs_3m_vs_soxx": {"kind": "ratio", "desc": "3-month return minus SOXX (semiconductor ETF, NYSE Semiconductor Index) 3-month return (negative = lagging)", "label": "3-month return vs the chip index (SOXX)"}, "rs_6m_vs_soxx": {"kind": "ratio", "desc": "6-month return minus SOXX (semiconductor ETF, NYSE Semiconductor Index) 6-month return (negative = lagging)", "label": "6-month return vs the chip index (SOXX)"}, "rs_12m_vs_soxx": {"kind": "ratio", "desc": "12-month return minus SOXX (semiconductor ETF, NYSE Semiconductor Index) 12-month return (negative = lagging)", "label": "12-month return vs the chip index (SOXX)"}, "rs_1m_vs_xlk": {"kind": "ratio", "desc": "1-month return minus XLK (technology) 1-month return (negative = lagging)", "label": "1-month return vs tech stocks (XLK)"}, "rs_3m_vs_xlk": {"kind": "ratio", "desc": "3-month return minus XLK (technology) 3-month return (negative = lagging)", "label": "3-month return vs tech stocks (XLK)"}, "rs_6m_vs_xlk": {"kind": "ratio", "desc": "6-month return minus XLK (technology) 6-month return (negative = lagging)", "label": "6-month return vs tech stocks (XLK)"}, "rs_12m_vs_xlk": {"kind": "ratio", "desc": "12-month return minus XLK (technology) 12-month return (negative = lagging)", "label": "12-month return vs tech stocks (XLK)"}, "rs_1m_vs_xlf": {"kind": "ratio", "desc": "1-month return minus XLF (financials) 1-month return (negative = lagging)", "label": "1-month return vs financials (XLF)"}, "rs_3m_vs_xlf": {"kind": "ratio", "desc": "3-month return minus XLF (financials) 3-month return (negative = lagging)", "label": "3-month return vs financials (XLF)"}, "rs_6m_vs_xlf": {"kind": "ratio", "desc": "6-month return minus XLF (financials) 6-month return (negative = lagging)", "label": "6-month return vs financials (XLF)"}, "rs_12m_vs_xlf": {"kind": "ratio", "desc": "12-month return minus XLF (financials) 12-month return (negative = lagging)", "label": "12-month return vs financials (XLF)"}, "rs_1m_vs_xle": {"kind": "ratio", "desc": "1-month return minus XLE (energy) 1-month return (negative = lagging)", "label": "1-month return vs energy stocks (XLE)"}, "rs_3m_vs_xle": {"kind": "ratio", "desc": "3-month return minus XLE (energy) 3-month return (negative = lagging)", "label": "3-month return vs energy stocks (XLE)"}, "rs_6m_vs_xle": {"kind": "ratio", "desc": "6-month return minus XLE (energy) 6-month return (negative = lagging)", "label": "6-month return vs energy stocks (XLE)"}, "rs_12m_vs_xle": {"kind": "ratio", "desc": "12-month return minus XLE (energy) 12-month return (negative = lagging)", "label": "12-month return vs energy stocks (XLE)"}, "rs_1m_vs_xlv": {"kind": "ratio", "desc": "1-month return minus XLV (health care) 1-month return (negative = lagging)", "label": "1-month return vs health care (XLV)"}, "rs_3m_vs_xlv": {"kind": "ratio", "desc": "3-month return minus XLV (health care) 3-month return (negative = lagging)", "label": "3-month return vs health care (XLV)"}, "rs_6m_vs_xlv": {"kind": "ratio", "desc": "6-month return minus XLV (health care) 6-month return (negative = lagging)", "label": "6-month return vs health care (XLV)"}, "rs_12m_vs_xlv": {"kind": "ratio", "desc": "12-month return minus XLV (health care) 12-month return (negative = lagging)", "label": "12-month return vs health care (XLV)"}, "rs_1m_vs_xli": {"kind": "ratio", "desc": "1-month return minus XLI (industrials) 1-month return (negative = lagging)", "label": "1-month return vs industrials (XLI)"}, "rs_3m_vs_xli": {"kind": "ratio", "desc": "3-month return minus XLI (industrials) 3-month return (negative = lagging)", "label": "3-month return vs industrials (XLI)"}, "rs_6m_vs_xli": {"kind": "ratio", "desc": "6-month return minus XLI (industrials) 6-month return (negative = lagging)", "label": "6-month return vs industrials (XLI)"}, "rs_12m_vs_xli": {"kind": "ratio", "desc": "12-month return minus XLI (industrials) 12-month return (negative = lagging)", "label": "12-month return vs industrials (XLI)"}, "rs_1m_vs_xlu": {"kind": "ratio", "desc": "1-month return minus XLU (utilities) 1-month return (negative = lagging)", "label": "1-month return vs utilities (XLU)"}, "rs_3m_vs_xlu": {"kind": "ratio", "desc": "3-month return minus XLU (utilities) 3-month return (negative = lagging)", "label": "3-month return vs utilities (XLU)"}, "rs_6m_vs_xlu": {"kind": "ratio", "desc": "6-month return minus XLU (utilities) 6-month return (negative = lagging)", "label": "6-month return vs utilities (XLU)"}, "rs_12m_vs_xlu": {"kind": "ratio", "desc": "12-month return minus XLU (utilities) 12-month return (negative = lagging)", "label": "12-month return vs utilities (XLU)"}, "rs_1m_vs_xly": {"kind": "ratio", "desc": "1-month return minus XLY (consumer discretionary) 1-month return (negative = lagging)", "label": "1-month return vs consumer discretionary (XLY)"}, "rs_3m_vs_xly": {"kind": "ratio", "desc": "3-month return minus XLY (consumer discretionary) 3-month return (negative = lagging)", "label": "3-month return vs consumer discretionary (XLY)"}, "rs_6m_vs_xly": {"kind": "ratio", "desc": "6-month return minus XLY (consumer discretionary) 6-month return (negative = lagging)", "label": "6-month return vs consumer discretionary (XLY)"}, "rs_12m_vs_xly": {"kind": "ratio", "desc": "12-month return minus XLY (consumer discretionary) 12-month return (negative = lagging)", "label": "12-month return vs consumer discretionary (XLY)"}, "rs_1m_vs_xlp": {"kind": "ratio", "desc": "1-month return minus XLP (consumer staples) 1-month return (negative = lagging)", "label": "1-month return vs consumer staples (XLP)"}, "rs_3m_vs_xlp": {"kind": "ratio", "desc": "3-month return minus XLP (consumer staples) 3-month return (negative = lagging)", "label": "3-month return vs consumer staples (XLP)"}, "rs_6m_vs_xlp": {"kind": "ratio", "desc": "6-month return minus XLP (consumer staples) 6-month return (negative = lagging)", "label": "6-month return vs consumer staples (XLP)"}, "rs_12m_vs_xlp": {"kind": "ratio", "desc": "12-month return minus XLP (consumer staples) 12-month return (negative = lagging)", "label": "12-month return vs consumer staples (XLP)"}, "rs_1m_vs_xlb": {"kind": "ratio", "desc": "1-month return minus XLB (materials) 1-month return (negative = lagging)", "label": "1-month return vs materials (XLB)"}, "rs_3m_vs_xlb": {"kind": "ratio", "desc": "3-month return minus XLB (materials) 3-month return (negative = lagging)", "label": "3-month return vs materials (XLB)"}, "rs_6m_vs_xlb": {"kind": "ratio", "desc": "6-month return minus XLB (materials) 6-month return (negative = lagging)", "label": "6-month return vs materials (XLB)"}, "rs_12m_vs_xlb": {"kind": "ratio", "desc": "12-month return minus XLB (materials) 12-month return (negative = lagging)", "label": "12-month return vs materials (XLB)"}, "rs_1m_vs_xlre": {"kind": "ratio", "desc": "1-month return minus XLRE (real estate) 1-month return (negative = lagging)", "label": "1-month return vs real estate (XLRE)"}, "rs_3m_vs_xlre": {"kind": "ratio", "desc": "3-month return minus XLRE (real estate) 3-month return (negative = lagging)", "label": "3-month return vs real estate (XLRE)"}, "rs_6m_vs_xlre": {"kind": "ratio", "desc": "6-month return minus XLRE (real estate) 6-month return (negative = lagging)", "label": "6-month return vs real estate (XLRE)"}, "rs_12m_vs_xlre": {"kind": "ratio", "desc": "12-month return minus XLRE (real estate) 12-month return (negative = lagging)", "label": "12-month return vs real estate (XLRE)"}, "rs_1m_vs_xlc": {"kind": "ratio", "desc": "1-month return minus XLC (communication services) 1-month return (negative = lagging)", "label": "1-month return vs communication services (XLC)"}, "rs_3m_vs_xlc": {"kind": "ratio", "desc": "3-month return minus XLC (communication services) 3-month return (negative = lagging)", "label": "3-month return vs communication services (XLC)"}, "rs_6m_vs_xlc": {"kind": "ratio", "desc": "6-month return minus XLC (communication services) 6-month return (negative = lagging)", "label": "6-month return vs communication services (XLC)"}, "rs_12m_vs_xlc": {"kind": "ratio", "desc": "12-month return minus XLC (communication services) 12-month return (negative = lagging)", "label": "12-month return vs communication services (XLC)"}, "revenue_ttm": {"kind": "usd", "desc": "trailing-twelve-month revenue (sum of last 4 fiscal quarters)", "label": "Revenue, last 12 months"}, "revenue_growth_yoy": {"kind": "ratio", "desc": "TTM revenue vs TTM revenue one year earlier - 1", "label": "Revenue growth (year over year)"}, "revenue_growth_q_yoy": {"kind": "ratio", "desc": "latest fiscal quarter revenue vs same quarter a year earlier - 1", "label": "Revenue growth, latest quarter (year over year)"}, "revenue_growth_accel": {"kind": "ratio", "desc": "latest quarter YoY growth minus prior quarter YoY growth; > 0 means growth is accelerating", "label": "Revenue growth acceleration"}, "gross_margin": {"kind": "ratio", "desc": "TTM gross profit / TTM revenue", "label": "Gross margin"}, "operating_margin": {"kind": "ratio", "desc": "TTM operating income / TTM revenue", "label": "Operating margin"}, "net_margin": {"kind": "ratio", "desc": "TTM net income / TTM revenue", "label": "Net margin"}, "net_income_ttm": {"kind": "usd", "desc": "TTM net income; > 0 means profitable on a GAAP basis", "label": "Net income, last 12 months"}, "fcf_ttm": {"kind": "usd", "desc": "TTM free cash flow = operating cash flow - capital expenditure", "label": "Free cash flow, last 12 months"}, "fcf_margin": {"kind": "ratio", "desc": "TTM FCF / TTM revenue", "label": "Free cash flow margin"}, "fcf_yield": {"kind": "ratio", "desc": "TTM FCF / market cap", "label": "Free cash flow yield"}, "net_debt": {"kind": "usd", "desc": "total debt - cash and short-term investments (negative = net cash)", "label": "Net debt"}, "ev_to_sales": {"kind": "number", "desc": "EV / TTM revenue", "label": "EV / sales"}, "short_pct_shares_out": {"kind": "ratio", "desc": "FINRA short interest / shares outstanding (not float: float is not in free data)", "label": "Short interest (% of shares)"}, "days_to_cover": {"kind": "days", "desc": "FINRA days to cover (short shares / average daily volume)", "label": "Days to cover (short interest)"}};
window.SCOUT_TRACKING = {
 "generated_at": "2026-10-08T22:54:25+00:00",
 "chain_ok": true,
 "chain_problems": [],
 "n_entries": 3,
 "label": "since run date; days of history, not evidence",
 "marks": [
  {
   "run_id": "a-midcap-pullback",
   "as_of": "2026-10-08",
   "marked_to": "2026-10-08",
   "trading_days": 0,
   "basket_return": 0.0,
   "benchmarks": {
    "SPY": 0.0,
    "SMH": 0.0
   },
   "basket_vs": {
    "SPY": 0.0,
    "SMH": 0.0
   },
   "picks": [
    {
     "symbol": "VICR",
     "rank": 1,
     "entry_close": 262.32,
     "return": 0.0
    },
    {
     "symbol": "SITM",
     "rank": 2,
     "entry_close": 645.06,
     "return": 0.0
    },
    {
     "symbol": "STRL",
     "rank": 3,
     "entry_close": 518.41,
     "return": 0.0
    },
    {
     "symbol": "SANM",
     "rank": 4,
     "entry_close": 210.48,
     "return": 0.0
    },
    {
     "symbol": "KLIC",
     "rank": 5,
     "entry_close": 90.92,
     "return": 0.0
    }
   ]
  },
  {
   "run_id": "b-ai-infra-laggards",
   "as_of": "2026-10-08",
   "marked_to": "2026-10-08",
   "trading_days": 0,
   "basket_return": 0.0,
   "benchmarks": {
    "SPY": 0.0,
    "SMH": 0.0
   },
   "basket_vs": {
    "SPY": 0.0,
    "SMH": 0.0
   },
   "picks": [
    {
     "symbol": "AVGO",
     "rank": 1,
     "entry_close": 360.14,
     "return": 0.0
    },
    {
     "symbol": "AAOI",
     "rank": 2,
     "entry_close": 105.9,
     "return": 0.0
    },
    {
     "symbol": "AMAT",
     "rank": 3,
     "entry_close": 509.57,
     "return": 0.0
    },
    {
     "symbol": "COHR",
     "rank": 4,
     "entry_close": 302.35,
     "return": 0.0
    },
    {
     "symbol": "AMKR",
     "rank": 5,
     "entry_close": 51.0,
     "return": 0.0
    }
   ]
  },
  {
   "run_id": "c-oversold-volume",
   "as_of": "2026-10-08",
   "marked_to": "2026-10-08",
   "trading_days": 0,
   "basket_return": 0.0,
   "benchmarks": {
    "SPY": 0.0,
    "SMH": 0.0
   },
   "basket_vs": {
    "SPY": 0.0,
    "SMH": 0.0
   },
   "picks": [
    {
     "symbol": "BX",
     "rank": 1,
     "entry_close": 112.68,
     "return": 0.0
    },
    {
     "symbol": "SBUX",
     "rank": 2,
     "entry_close": 93.21,
     "return": 0.0
    }
   ]
  }
 ]
};
window.SCOUT_BENCH = {"spy": "the S&P 500 (SPY)", "qqq": "the Nasdaq-100 (QQQ)", "iwm": "the Russell 2000 (IWM)", "smh": "the chip index (SMH)", "soxx": "the chip index (SOXX)", "xlk": "tech stocks (XLK)", "xlf": "financials (XLF)", "xle": "energy stocks (XLE)", "xlv": "health care (XLV)", "xli": "industrials (XLI)", "xlu": "utilities (XLU)", "xly": "consumer discretionary (XLY)", "xlp": "consumer staples (XLP)", "xlb": "materials (XLB)", "xlre": "real estate (XLRE)", "xlc": "communication services (XLC)"};
window.SCOUT_CHIPS = [{"id": "chip-consumer-brands", "label": "Quality consumer brands down 30%+ with strong free cash flow", "observation": "Quality consumer brands down 30% from their highs that still generate strong free cash flow", "spec": {"version": 1, "observation": "Quality consumer brands down 30% from their highs that still generate strong free cash flow", "universe": {"industry_groups": ["Food & Beverage", "Household & Personal Products", "Apparel & Luxury", "Restaurants", "Tobacco"]}, "conditions": [{"field": "drawdown_52w", "op": "<=", "value": -0.3, "why": "down 30% from their highs"}, {"field": "fcf_margin", "op": ">", "value": 0.1, "why": "still generate strong free cash flow"}], "rank": [{"field": "fcf_margin", "direction": "desc", "weight": 1}], "top_n": 5, "unmapped": [{"text": "Quality consumer brands", "reason": "Brand strength/quality is not directly measurable; approximated by consumer industry groups and a strong free cash flow margin."}], "notes": "Mapped 'consumer brands' to the listed consumer industry groups (Food & Beverage, Household & Personal Products, Apparel & Luxury, Restaurants, Tobacco). 'Down 30% from highs' is enforced as drawdown_52w <= -0.30; 'strong free cash flow' is interpreted as TTM FCF margin > 10% and ranked by that margin."}, "generated": "2026-10-09", "as_of": "2026-10-08", "model": "deepseek-v4-pro"}, {"id": "chip-quality-drawdown", "label": "Profitable names over $2B, down 30%+ and still growing", "observation": "Profitable companies worth over 2 billion dollars, down 30% or more from their highs, still growing revenue and generating free cash flow", "spec": {"version": 1, "observation": "Profitable companies worth over 2 billion dollars, down 30% or more from their highs, still growing revenue and generating free cash flow", "universe": {"market_cap_min": 2000000000}, "conditions": [{"field": "net_income_ttm", "op": ">", "value": 0, "why": "Profitable companies"}, {"field": "drawdown_52w", "op": "<=", "value": -0.3, "why": "down 30% or more from their highs"}, {"field": "revenue_growth_yoy", "op": ">", "value": 0, "why": "still growing revenue"}, {"field": "fcf_ttm", "op": ">", "value": 0, "why": "generating free cash flow"}], "rank": [{"field": "drawdown_52w", "direction": "asc", "weight": 1}], "top_n": 5, "unmapped": [], "notes": "Interpreted 'worth over 2 billion dollars' as market capitalization greater than $2B. 'Profitable' as positive trailing twelve-month net income. 'Down 30% or more from their highs' as current close at least 30% below its 52-week high. 'Growing revenue' as positive year-over-year TTM revenue growth. 'Generating free cash flow' as positive trailing twelve-month free cash flow. Ranked by drawdown_52w ascending to surface the most beaten-down stocks first, as the observation emphasizes the drawdown."}, "generated": "2026-10-09", "as_of": "2026-10-08", "model": "deepseek-v4-pro"}, {"id": "chip-ai-laggards", "label": "AI suppliers lagging the chip index while revenue accelerates", "observation": "AI suppliers lagging the chip index while revenue accelerates", "spec": {"version": 1, "observation": "AI suppliers lagging the chip index while revenue accelerates", "universe": {"themes": ["ai_semis", "ai_networking", "ai_power"]}, "conditions": [{"field": "rs_3m_vs_smh", "op": "<", "value": 0, "why": "lagging the chip index"}, {"field": "revenue_growth_accel", "op": ">", "value": 0, "why": "revenue accelerates"}], "rank": [{"field": "revenue_growth_accel", "direction": "desc", "weight": 1}], "top_n": 5, "unmapped": [], "notes": "Interpreted AI suppliers as the ai_semis, ai_networking, and ai_power theme baskets. Used SMH as the chip index and a 3-month relative return below zero for lagging; revenue acceleration is latest quarter YoY growth minus prior quarter YoY growth."}, "generated": "2026-10-09", "as_of": "2026-10-08", "model": "deepseek-v4-pro"}, {"id": "chip-oversold-volume", "label": "Oversold large caps on heavy volume", "observation": "Oversold large caps on heavy volume", "spec": {"version": 1, "observation": "Oversold large caps on heavy volume", "universe": {"market_cap_min": 10000000000}, "conditions": [{"field": "rsi14", "op": "<", "value": 30, "why": "oversold"}, {"field": "volume_ratio_50d", "op": ">", "value": 2.0, "why": "heavy volume"}], "rank": [{"field": "rsi14", "direction": "asc", "weight": 1}], "top_n": 5, "unmapped": [], "notes": "Interpreted oversold as RSI(14) below 30, heavy volume as volume at least twice the 50-day average, and large cap as market cap above $10B. Thresholds are defaults since exact levels were not specified."}, "generated": "2026-10-09", "as_of": "2026-10-08", "model": "deepseek-v4-pro"}, {"id": "chip-cash-rich-lows", "label": "Cash-rich small caps down 40%+ from their highs", "observation": "Small caps between 300 million and 2 billion dollars with more cash than debt, down 40% or more from their highs, still generating free cash flow", "spec": {"version": 1, "observation": "Small caps between 300 million and 2 billion dollars with more cash than debt, down 40% or more from their highs, still generating free cash flow", "universe": {"market_cap_min": 300000000, "market_cap_max": 2000000000}, "conditions": [{"field": "net_debt", "op": "<", "value": 0, "why": "more cash than debt"}, {"field": "drawdown_52w", "op": "<=", "value": -0.4, "why": "down 40% or more from their highs"}, {"field": "fcf_ttm", "op": ">", "value": 0, "why": "still generating free cash flow"}], "rank": [{"field": "fcf_ttm", "direction": "desc", "weight": 1}], "top_n": 5, "unmapped": [], "notes": "Interpreted 'down from their highs' as the drawdown from the 52-week high close, since all-time high data is not available. Net debt less than zero captures more cash than debt. Ranked by absolute free cash flow to emphasize the positive cash flow requirement."}, "generated": "2026-10-09", "as_of": "2026-10-08", "model": "deepseek-v4-pro"}, {"id": "chip-short-squeeze-setup", "label": "Heavily shorted, profitable, back above the 50-day average", "observation": "Profitable companies with heavy short interest that are moving back above their 50-day average", "spec": {"version": 1, "observation": "Profitable companies with heavy short interest that are moving back above their 50-day average", "universe": {}, "conditions": [{"field": "net_income_ttm", "op": ">", "value": 0, "why": "Profitable companies"}, {"field": "short_pct_shares_out", "op": ">", "value": 0.2, "why": "heavy short interest"}, {"field": "close", "op": ">", "ref": "sma50", "why": "moving back above their 50-day average"}], "rank": [{"field": "short_pct_shares_out", "direction": "desc", "weight": 1}], "top_n": 5, "unmapped": [{"text": "moving back above their 50-day average", "reason": "Current close above SMA50 is used; the crossover from below is not directly observable with available fields."}, {"text": "heavy short interest", "reason": "No objective threshold in the observation; used short interest > 20% of shares outstanding as a proxy, note float data is unavailable."}], "notes": "Interpreted profitable as positive TTM net income and moving back above 50-day average as close > SMA50. Heavy short interest is proxied by short interest > 20% of shares outstanding because float is not available."}, "generated": "2026-10-09", "as_of": "2026-10-08", "model": "deepseek-v4-pro"}, {"id": "chip-growth-momentum", "label": "Fast growers over $2B beating the S&P 500", "observation": "Companies worth over 2 billion dollars growing revenue 30% or more, with price above the 200-day average and beating the S&P 500 over 3 months", "spec": {"version": 1, "observation": "Companies worth over 2 billion dollars growing revenue 30% or more, with price above the 200-day average and beating the S&P 500 over 3 months", "universe": {"market_cap_min": 2000000000}, "conditions": [{"field": "revenue_growth_yoy", "op": ">=", "value": 0.3, "why": "growing revenue 30% or more"}, {"field": "close", "op": ">", "ref": "sma200", "why": "price above the 200-day average"}, {"field": "rs_3m_vs_spy", "op": ">", "value": 0, "why": "beating the S&P 500 over 3 months"}], "rank": [{"field": "revenue_growth_yoy", "direction": "desc", "weight": 1}], "top_n": 5, "unmapped": [], "notes": "Revenue growth is interpreted as trailing twelve months revenue versus the prior year. After applying the required filters, companies are ranked by revenue growth with higher growth ranked better."}, "generated": "2026-10-09", "as_of": "2026-10-08", "model": "deepseek-v4-pro"}];
window.SCOUT_RUNS = [
 {
  "id": "a-midcap-pullback",
  "as_of": "2026-10-08",
  "generated_at": "2026-10-08T22:53:50+00:00",
  "llm": {
   "provider": "deepseek",
   "model": "deepseek-v4-pro"
  },
  "data": {
   "as_of": "2026-10-08",
   "last_price_date": "2026-10-08",
   "universe_rule": "tradable US-listed (NYSE/Nasdaq/AMEX/Arca/BATS) operating companies with an SEC CIK and a 10-K/10-Q/20-F/40-F in the last 18 months; close >= $1; 50-day avg dollar volume >= $1,000,000; one listing per CIK",
   "n_companies": 3827,
   "short_interest_settlement": "2026-09-15",
   "benchmark_closes": {
    "IWM": 277.57,
    "QQQ": 747.58,
    "SMH": 607.27,
    "SOXX": 563.28,
    "SPY": 773.93,
    "XLB": 49.27,
    "XLC": 112.07,
    "XLE": 65.24,
    "XLF": 54.23,
    "XLI": 168.4,
    "XLK": 197.78,
    "XLP": 83.42,
    "XLRE": 40.85,
    "XLU": 41.07,
    "XLV": 168.16,
    "XLY": 111.71
   },
   "files": {
    "prices.csv.gz": {
     "sha256": "2fb70ee43a9d30a4174c2353a1eca23798fb267cd09557d74d1af3cc6146d0e1",
     "bytes": 50692072
    },
    "features.csv.gz": {
     "sha256": "cf63f29b2cc08badaf287c158d7e85c689a249e386a9f0f9c0b85029e0510c87",
     "bytes": 3541921
    }
   }
  },
  "observation": "Profitable mid-caps (2–20B) that have pulled back 20%+ from their 52-week high but are still growing revenue over 10% and generating free cash flow, with price back above the 50-day average.",
  "spec": {
   "version": 1,
   "observation": "Profitable mid-caps (2–20B) that have pulled back 20%+ from their 52-week high but are still growing revenue over 10% and generating free cash flow, with price back above the 50-day average.",
   "universe": {
    "market_cap_min": 2000000000,
    "market_cap_max": 20000000000
   },
   "conditions": [
    {
     "field": "net_income_ttm",
     "op": ">",
     "value": 0,
     "why": "Profitable"
    },
    {
     "field": "drawdown_52w",
     "op": "<=",
     "value": -0.2,
     "why": "pulled back 20%+ from their 52-week high"
    },
    {
     "field": "revenue_growth_yoy",
     "op": ">",
     "value": 0.1,
     "why": "still growing revenue over 10%"
    },
    {
     "field": "fcf_ttm",
     "op": ">",
     "value": 0,
     "why": "generating free cash flow"
    },
    {
     "field": "close",
     "op": ">",
     "ref": "sma50",
     "why": "price back above the 50-day average"
    }
   ],
   "rank": [
    {
     "field": "revenue_growth_yoy",
     "direction": "desc",
     "weight": 1
    }
   ],
   "top_n": 5,
   "unmapped": [],
   "notes": "Interpreted mid-caps as market cap between $2B and $20B, revenue growth as TTM year-over-year revenue growth, and profitable as positive TTM net income. Since no ranking was specified, ranked by revenue growth to surface faster growers."
  },
  "attempts": 2,
  "funnel": [
   {
    "step": "universe (liquid US common stocks with SEC filings)",
    "kind": "start",
    "n_in": 3827,
    "n_pass": 3827,
    "n_fail": 0,
    "n_missing": 0
   },
   {
    "step": "market_cap >= $2.00B",
    "kind": "universe",
    "n_in": 3827,
    "n_pass": 1902,
    "n_fail": 1712,
    "n_missing": 213
   },
   {
    "step": "market_cap <= $20.00B",
    "kind": "universe",
    "n_in": 1902,
    "n_pass": 1318,
    "n_fail": 584,
    "n_missing": 0
   },
   {
    "step": "net_income_ttm > 0",
    "kind": "condition",
    "n_in": 1318,
    "n_pass": 756,
    "n_fail": 209,
    "n_missing": 353
   },
   {
    "step": "drawdown_52w <= -20.0%",
    "kind": "condition",
    "n_in": 756,
    "n_pass": 343,
    "n_fail": 409,
    "n_missing": 4
   },
   {
    "step": "revenue_growth_yoy > +10.0%",
    "kind": "condition",
    "n_in": 343,
    "n_pass": 174,
    "n_fail": 168,
    "n_missing": 1
   },
   {
    "step": "fcf_ttm > 0",
    "kind": "condition",
    "n_in": 174,
    "n_pass": 131,
    "n_fail": 20,
    "n_missing": 23
   },
   {
    "step": "close > sma50",
    "kind": "condition",
    "n_in": 131,
    "n_pass": 23,
    "n_fail": 108,
    "n_missing": 0
   }
  ],
  "columns": [
   "rank",
   "symbol",
   "name",
   "sector",
   "score",
   "market_cap",
   "net_income_ttm",
   "drawdown_52w",
   "revenue_growth_yoy",
   "fcf_ttm",
   "close",
   "sma50"
  ],
  "ranked": [
   {
    "rank": 1,
    "symbol": "VICR",
    "name": "VICOR CORP",
    "sector": "Information Technology",
    "score": 1.0,
    "market_cap": 11927690400.0,
    "net_income_ttm": 136681000.0,
    "drawdown_52w": -0.3092843225025014,
    "revenue_growth_yoy": 0.9611869301158866,
    "fcf_ttm": 87323000.0,
    "close": 262.32,
    "sma50": 226.75980000000004
   },
   {
    "rank": 2,
    "symbol": "SITM",
    "name": "SITIME Corp",
    "sector": "Information Technology",
    "score": 0.9565217391304348,
    "market_cap": 19397622482.16,
    "net_income_ttm": 14095000.0,
    "drawdown_52w": -0.2844433598083152,
    "revenue_growth_yoy": 0.8302812410755154,
    "fcf_ttm": 84488000.0,
    "close": 645.06,
    "sma50": 624.3683
   },
   {
    "rank": 3,
    "symbol": "STRL",
    "name": "STERLING INFRASTRUCTURE, INC.",
    "sector": "Industrials",
    "score": 0.9130434782608695,
    "market_cap": 15857393616.38,
    "net_income_ttm": 431480000.0,
    "drawdown_52w": -0.4783243101817377,
    "revenue_growth_yoy": 0.6082789871426026,
    "fcf_ttm": 482002000.0,
    "close": 518.41,
    "sma50": 517.6052
   },
   {
    "rank": 4,
    "symbol": "SANM",
    "name": "SANMINA CORP",
    "sector": "Information Technology",
    "score": 0.8695652173913043,
    "market_cap": 11281171490.88,
    "net_income_ttm": 308127000.0,
    "drawdown_52w": -0.2555178268251274,
    "revenue_growth_yoy": 0.5856115197288774,
    "fcf_ttm": 594148000.0,
    "close": 210.48,
    "sma50": 204.57440000000005
   },
   {
    "rank": 5,
    "symbol": "KLIC",
    "name": "KULICKE & SOFFA INDUSTRIES INC",
    "sector": "Information Technology",
    "score": 0.8260869565217391,
    "market_cap": 4757763135.8,
    "net_income_ttm": 115739000.0,
    "drawdown_52w": -0.3187982318123923,
    "revenue_growth_yoy": 0.4444395462740294,
    "fcf_ttm": 41129000.0,
    "close": 90.92,
    "sma50": 88.12619999999998
   },
   {
    "rank": 6,
    "symbol": "FN",
    "name": "Fabrinet",
    "sector": "Information Technology",
    "score": 0.782608695652174,
    "market_cap": 17463404273.12,
    "net_income_ttm": 473027000.0,
    "drawdown_52w": -0.3471539378675633,
    "revenue_growth_yoy": 0.3573130034068108,
    "fcf_ttm": 4222000.0,
    "close": 487.33,
    "sma50": 450.31700000000006
   },
   {
    "rank": 7,
    "symbol": "ELF",
    "name": "e.l.f. Beauty, Inc.",
    "sector": "Consumer Staples",
    "score": 0.7391304347826086,
    "market_cap": 6252487256.16,
    "net_income_ttm": 59606000.0,
    "drawdown_52w": -0.2695939891087061,
    "revenue_growth_yoy": 0.3122829594445548,
    "fcf_ttm": 280158000.0,
    "close": 105.96,
    "sma50": 98.747
   },
   {
    "rank": 8,
    "symbol": "MOD",
    "name": "MODINE MANUFACTURING CO",
    "sector": "Consumer Discretionary",
    "score": 0.6956521739130435,
    "market_cap": 9660670458.12,
    "net_income_ttm": 144200000.0,
    "drawdown_52w": -0.3562555299946912,
    "revenue_growth_yoy": 0.2946867321867321,
    "fcf_ttm": 100200000.0,
    "close": 181.89,
    "sma50": 176.907
   },
   {
    "rank": 9,
    "symbol": "KVYO",
    "name": "Klaviyo, Inc.",
    "sector": "Information Technology",
    "score": 0.6521739130434783,
    "market_cap": 5215686231.42,
    "net_income_ttm": 6791000.0,
    "drawdown_52w": -0.4717378232110643,
    "revenue_growth_yoy": 0.2888642387975537,
    "fcf_ttm": 253115000.0,
    "close": 17.57,
    "sma50": 17.499200000000002
   },
   {
    "rank": 10,
    "symbol": "HUBS",
    "name": "HUBSPOT INC",
    "sector": "Information Technology",
    "score": 0.6086956521739131,
    "market_cap": 11560980039.84,
    "net_income_ttm": 146854000.0,
    "drawdown_52w": -0.5312386267135751,
    "revenue_growth_yoy": 0.2110666027131551,
    "fcf_ttm": 797496000.0,
    "close": 231.84,
    "sma50": 230.144
   },
   {
    "rank": 11,
    "symbol": "WK",
    "name": "WORKIVA INC",
    "sector": "Information Technology",
    "score": 0.5652173913043478,
    "market_cap": 4100032456.94,
    "net_income_ttm": 47040000.0,
    "drawdown_52w": -0.2102668524273926,
    "revenue_growth_yoy": 0.1966846638751787,
    "fcf_ttm": 200524000.0,
    "close": 73.69,
    "sma50": 71.0876
   },
   {
    "rank": 12,
    "symbol": "WAY",
    "name": "Waystar Holding Corp.",
    "sector": "Information Technology",
    "score": 0.5217391304347826,
    "market_cap": 5077498055.68,
    "net_income_ttm": 134797000.0,
    "drawdown_52w": -0.331650681474003,
    "revenue_growth_yoy": 0.192260875326188,
    "fcf_ttm": 246260000.0,
    "close": 26.48,
    "sma50": 24.8484
   },
   {
    "rank": 13,
    "symbol": "RMBS",
    "name": "RAMBUS INC",
    "sector": "Information Technology",
    "score": 0.4782608695652174,
    "market_cap": 11729616810.49,
    "net_income_ttm": 230010000.0,
    "drawdown_52w": -0.3644087659674205,
    "revenue_growth_yoy": 0.1911707137394556,
    "fcf_ttm": 335209000.0,
    "close": 108.47,
    "sma50": 95.1518
   },
   {
    "rank": 14,
    "symbol": "DIOD",
    "name": "DIODES INC /DEL/",
    "sector": "Information Technology",
    "score": 0.43478260869565216,
    "market_cap": 4432016089.2,
    "net_income_ttm": 86090000.0,
    "drawdown_52w": -0.2160312805474096,
    "revenue_growth_yoy": 0.1780223707971884,
    "fcf_ttm": 142510000.0,
    "close": 96.24,
    "sma50": 94.3391
   },
   {
    "rank": 15,
    "symbol": "MYRG",
    "name": "MYR GROUP INC.",
    "sector": "Industrials",
    "score": 0.391304347826087,
    "market_cap": 4839078592.5,
    "net_income_ttm": 165293000.0,
    "drawdown_52w": -0.379781693372977,
    "revenue_growth_yoy": 0.1605744045903232,
    "fcf_ttm": 193363000.0,
    "close": 310.81,
    "sma50": 305.4861
   }
  ],
  "sector_breakdown": [
   {
    "sector": "Information Technology",
    "n": 17
   },
   {
    "sector": "Consumer Staples",
    "n": 2
   },
   {
    "sector": "Industrials",
    "n": 2
   },
   {
    "sector": "Consumer Discretionary",
    "n": 1
   },
   {
    "sector": "Health Care",
    "n": 1
   }
  ],
  "n_ranked": 23,
  "top_n": 5,
  "explanations": [
   {
    "symbol": "VICR",
    "verdict": "not enough evidence",
    "thesis": [],
    "bear_case": [
     {
      "claim": "A news report says Vicor shows overbought RSI readings above 70, signaling potential momentum warnings for investors, which may explain near-term downside risk despite positive fundamentals.",
      "quote": "Three industrial stocks—RXO, ACVA and VICR—show overbought RSI readings above 70, signaling potential momentum warnings for investors.",
      "doc_id": "VICR-news-2026-10-06-62188513",
      "ok": true,
      "reason": "",
      "url": "https://www.benzinga.com/trading-ideas/short-ideas/26/10/62188513/top-3-industrials-stocks-you-may-want-to-dump-in-october",
      "source_kind": "news"
     },
     {
      "claim": "Gross margin as a percentage of net revenues decreased to 58.0% in the second quarter of 2026 from 65.3% a year ago, indicating margin pressure that could weigh on profitability.",
      "quote": "Gross margin, as a percentage of net revenues and patent litigation settlement, decreased to 58.0% for the second quarter of 2026, compared to 65.3% for the second quarter of 2025.",
      "doc_id": "VICR-10Q-2026-07-29-mdna",
      "ok": true,
      "reason": "",
      "url": "https://www.sec.gov/Archives/edgar/data/751978/000119312526322462/vicr-20260630.htm",
      "source_kind": "mdna"
     }
    ],
    "stripped": [],
    "documents": [
     {
      "doc_id": "VICR-8K-2026-07-21-ex99",
      "kind": "earnings_release",
      "title": "VICR 8-K earnings release (Exhibit 99.1), filed 2026-07-21",
      "url": "https://www.sec.gov/Archives/edgar/data/751978/000119312526309538/d115827dex991.htm",
      "filed": "2026-07-21",
      "chars_total": 10583,
      "chars_shown": 10583
     },
     {
      "doc_id": "VICR-10Q-2026-07-29-mdna",
      "kind": "mdna",
      "title": "VICR 10-Q for period 2026-06-30, MD&A, filed 2026-07-29",
      "url": "https://www.sec.gov/Archives/edgar/data/751978/000119312526322462/vicr-20260630.htm",
      "filed": "2026-07-29",
      "chars_total": 38092,
      "chars_shown": 38092
     },
     {
      "doc_id": "VICR-news-2026-10-06-62188513",
      "kind": "news",
      "title": "Benzinga: Top 3 Industrials Stocks You May Want To Dump In October (2026-10-06)",
      "url": "https://www.benzinga.com/trading-ideas/short-ideas/26/10/62188513/top-3-industrials-stocks-you-may-want-to-dump-in-october",
      "filed": "2026-10-06",
      "chars_total": 191,
      "chars_shown": 191
     },
     {
      "doc_id": "VICR-news-2026-10-01-62099302",
      "kind": "news",
      "title": "Benzinga: Vicor Stock Soars 11% On Another Outlook Hike (2026-10-01)",
      "url": "https://www.benzinga.com/markets/guidance/26/10/62099302/vicor-stock-soars-11-on-another-outlook-hike",
      "filed": "2026-10-01",
      "chars_total": 184,
      "chars_shown": 184
     },
     {
      "doc_id": "VICR-news-2026-10-01-62099280",
      "kind": "news",
      "title": "Benzinga: Needham Maintains Buy on Vicor, Raises Price Target to $350 (2026-10-01)",
      "url": "https://www.benzinga.com/news/26/10/62099280/needham-maintains-buy-vicor-raises-price-target-350",
      "filed": "2026-10-01",
      "chars_total": 59,
      "chars_shown": 59
     },
     {
      "doc_id": "VICR-news-2026-10-01-62097267",
      "kind": "news",
      "title": "Benzinga: Acuity, Accenture and 3 Stocks to Watch Heading Into Thursday (2026-10-01)",
      "url": "https://www.benzinga.com/markets/equities/26/10/62097267/acuity-accenture-and-3-stocks-to-watch-heading-into-thursday",
      "filed": "2026-10-01",
      "chars_total": 191,
      "chars_shown": 191
     },
     {
      "doc_id": "VICR-news-2026-09-30-62093653",
      "kind": "news",
      "title": "Benzinga: Vicor Q3  Revenue expected to be more than $186.358M vs $165.450M Est (2026-09-30)",
      "url": "https://www.benzinga.com/news/26/09/62093653/vicor-q3-revenue-expected-be-more-186-358m-vs-165-450m-est",
      "filed": "2026-09-30",
      "chars_total": 69,
      "chars_shown": 69
     },
     {
      "doc_id": "VICR-news-2026-09-30-62092805",
      "kind": "news",
      "title": "Benzinga: Vicor Raises Q3 Sequential Revenue Growth Guidance To Above 30% From Above 20% On Higher Vertical Power Delivery Royalties (2026-09-30)",
      "url": "https://www.benzinga.com/news/26/09/62092805/vicor-raises-q3-sequential-revenue-growth-guidance-above-30-above-20-higher-vertical-power-delivery-",
      "filed": "2026-09-30",
      "chars_total": 122,
      "chars_shown": 122
     },
     {
      "doc_id": "VICR-news-2026-09-23-61944188",
      "kind": "news",
      "title": "Benzinga: Top 3 Industrials Stocks That May Fall Off A Cliff This Quarter (2026-09-23)",
      "url": "https://www.benzinga.com/trading-ideas/short-ideas/26/09/61944188/top-3-industrials-stocks-that-may-fall-off-a-cliff-this-quarter-2",
      "filed": "2026-09-23",
      "chars_total": 176,
      "chars_shown": 176
     },
     {
      "doc_id": "VICR-news-2026-09-22-61929528",
      "kind": "news",
      "title": "Benzinga: Roth Capital Reiterates Buy on Vicor, Maintains $375 Price Target (2026-09-22)",
      "url": "https://www.benzinga.com/news/26/09/61929528/roth-capital-reiterates-buy-vicor-maintains-375-price-target",
      "filed": "2026-09-22",
      "chars_total": 65,
      "chars_shown": 65
     },
     {
      "doc_id": "VICR-news-2026-09-22-61915445",
      "kind": "news",
      "title": "Benzinga: Needham Reiterates Buy on Vicor, Maintains $320 Price Target (2026-09-22)",
      "url": "https://www.benzinga.com/news/26/09/61915445/needham-reiterates-buy-vicor-maintains-320-price-target",
      "filed": "2026-09-22",
      "chars_total": 60,
      "chars_shown": 60
     },
     {
      "doc_id": "VICR-news-2026-09-22-61915359",
      "kind": "news",
      "title": "Benzinga: Market-Moving News for September 22nd (2026-09-22)",
      "url": "https://www.benzinga.com/trading-ideas/movers/26/09/61915359/market-moving-news-september-22nd",
      "filed": "2026-09-22",
      "chars_total": 37,
      "chars_shown": 37
     },
     {
      "doc_id": "VICR-news-2026-09-22-61913202",
      "kind": "news",
      "title": "Benzinga: AutoZone, Vicor And 3 Stocks To Watch Heading Into Tuesday (2026-09-22)",
      "url": "https://www.benzinga.com/trading-ideas/long-ideas/26/09/61913202/autozone-vicor-and-3-stocks-to-watch-heading-into-tuesday",
      "filed": "2026-09-22",
      "chars_total": 182,
      "chars_shown": 182
     },
     {
      "doc_id": "VICR-news-2026-09-21-61909562",
      "kind": "news",
      "title": "Benzinga: Vicor Stock Rises After Stronger Q3 Guidance (2026-09-21)",
      "url": "https://www.benzinga.com/trading-ideas/movers/26/09/61909562/vicor-stock-rises-after-stronger-q3-guidance",
      "filed": "2026-09-21",
      "chars_total": 184,
      "chars_shown": 184
     }
    ],
    "model_status": "model said evidence: thin"
   },
   {
    "symbol": "SITM",
    "verdict": "explained",
    "thesis": [
     {
      "claim": "Revenue increased 127% year over year in the second quarter of 2026, driven by AI and datacenter demand.",
      "quote": "Revenue increased by $87.9 million, or 127%, for the three months ended June 30, 2026 compared to the same period in the prior year primarily driven by demand for our products in the AI and datacenter applications.",
      "doc_id": "SITM-10Q-2026-08-06-mdna",
      "ok": true,
      "reason": "",
      "url": "https://www.sec.gov/Archives/edgar/data/1451809/000145180926000060/sitm-20260630.htm",
      "source_kind": "mdna"
     },
     {
      "claim": "Management highlighted strong revenue growth and a gross margin of 67.1%.",
      "quote": "revenue increasing 127% year over year to $157.4 million and gross margin of 67.1%",
      "doc_id": "SITM-8K-2026-08-05-ex99",
      "ok": true,
      "reason": "",
      "url": "https://www.sec.gov/Archives/edgar/data/1451809/000145180926000059/sitm-q226x8kxexx991.htm",
      "source_kind": "earnings_release"
     },
     {
      "claim": "On July 1, SiTime completed the acquisition of Renesas' Timing Business, adding over 550 clocking products.",
      "quote": "On July 1, we completed the acquisition of Renesas' Timing Business, adding over 550 clocking products to our portfolio.",
      "doc_id": "SITM-8K-2026-08-05-ex99",
      "ok": true,
      "reason": "",
      "url": "https://www.sec.gov/Archives/edgar/data/1451809/000145180926000059/sitm-q226x8kxexx991.htm",
      "source_kind": "earnings_release"
     }
    ],
    "bear_case": [
     {
      "claim": "Acquisition-related costs surged 355% year over year, including $6.5 million of one-time costs for the Renesas deal, weighing on GAAP results.",
      "quote": "Acquisition related costs increased by $6.6 million, or 355%, for the three months ended June 30, 2026, primarily due to one-time costs of $6.5 million incurred towards the acquisition of Renesas' timing business.",
      "doc_id": "SITM-10Q-2026-08-06-mdna",
      "ok": true,
      "reason": "",
      "url": "https://www.sec.gov/Archives/edgar/data/1451809/000145180926000060/sitm-20260630.htm",
      "source_kind": "mdna"
     },
     {
      "claim": "Customer concentration is high, with the top three distributors accounting for approximately 66% of revenue in the latest quarter.",
      "quote": "Our top three customers by revenue, which are distributors, together accounted for approximately 66% of our revenue for the three months ended June 30, 2026 and 2025, and 66% and 64% of our revenues for the six months ended June 30, 2026 and 2025, respectively.",
      "doc_id": "SITM-10Q-2026-08-06-mdna",
      "ok": true,
      "reason": "",
      "url": "https://www.sec.gov/Archives/edgar/data/1451809/000145180926000060/sitm-20260630.htm",
      "source_kind": "mdna"
     },
     {
      "claim": "The Renesas acquisition was partly funded by issuing 3,558,691 shares of common stock, increasing share count and potential dilution.",
      "quote": "Additionally, the Company issued 3,558,691 shares of the Company’s common stock towards this acquisition.",
      "doc_id": "SITM-10Q-2026-08-06-mdna",
      "ok": true,
      "reason": "",
      "url": "https://www.sec.gov/Archives/edgar/data/1451809/000145180926000060/sitm-20260630.htm",
      "source_kind": "mdna"
     }
    ],
    "stripped": [],
    "documents": [
     {
      "doc_id": "SITM-8K-2026-08-05-ex99",
      "kind": "earnings_release",
      "title": "SITM 8-K earnings release (Exhibit 99.1), filed 2026-08-05",
      "url": "https://www.sec.gov/Archives/edgar/data/1451809/000145180926000059/sitm-q226x8kxexx991.htm",
      "filed": "2026-08-05",
      "chars_total": 17397,
      "chars_shown": 17397
     },
     {
      "doc_id": "SITM-10Q-2026-08-06-mdna",
      "kind": "mdna",
      "title": "SITM 10-Q for period 2026-06-30, MD&A, filed 2026-08-06",
      "url": "https://www.sec.gov/Archives/edgar/data/1451809/000145180926000060/sitm-20260630.htm",
      "filed": "2026-08-06",
      "chars_total": 37521,
      "chars_shown": 37521
     },
     {
      "doc_id": "SITM-news-2026-09-28-62037351",
      "kind": "news",
      "title": "Benzinga: If You Invested $1000 In SiTime Stock 5 Years Ago, You Would Have This Much Today (2026-09-28)",
      "url": "https://www.benzinga.com/news/26/09/62037351/if-you-invested-1000-sitime-stock-5-years-ago-you-would-have-much-today",
      "filed": "2026-09-28",
      "chars_total": 296,
      "chars_shown": 296
     },
     {
      "doc_id": "SITM-news-2026-09-23-61940261",
      "kind": "news",
      "title": "Benzinga: Seaport Global Initiates Coverage On SiTime with Neutral Rating (2026-09-23)",
      "url": "https://www.benzinga.com/news/26/09/61940261/seaport-global-initiates-coverage-sitime-neutral-rating",
      "filed": "2026-09-23",
      "chars_total": 63,
      "chars_shown": 63
     },
     {
      "doc_id": "SITM-news-2026-09-17-61849157",
      "kind": "news",
      "title": "Benzinga: Morgan Stanley Initiates Coverage On SiTime with Overweight Rating, Announces Price Target of $730 (2026-09-17)",
      "url": "https://www.benzinga.com/news/26/09/61849157/morgan-stanley-initiates-coverage-sitime-overweight-rating-announces-price-target-730",
      "filed": "2026-09-17",
      "chars_total": 98,
      "chars_shown": 98
     }
    ],
    "model_status": "model said evidence: sufficient"
   },
   {
    "symbol": "STRL",
    "verdict": "explained",
    "thesis": [
     {
      "claim": "Second quarter revenues increased 90% to $1.17 billion, with acquisitions contributing $250.8 million.",
      "quote": "Revenues of $1.17 billion increased by 90%. Acquisitions(1) contributed $250.8 million of revenue in the quarter.",
      "doc_id": "STRL-8K-2026-08-03-ex99",
      "ok": true,
      "reason": "",
      "url": "https://www.sec.gov/Archives/edgar/data/874238/000087423826000100/a20260803ex991earningsrele.htm",
      "source_kind": "earnings_release"
     },
     {
      "claim": "Backlog at June 30, 2026 was $4.33 billion, up 116% from the prior year period, and organic backlog increased 50% year-over-year.",
      "quote": "Backlog at June 30, 2026 was $4.33 billion, up 116% from the prior year period. Backlog increased 50% year-over-year on an organic basis.",
      "doc_id": "STRL-8K-2026-08-03-ex99",
      "ok": true,
      "reason": "",
      "url": "https://www.sec.gov/Archives/edgar/data/874238/000087423826000100/a20260803ex991earningsrele.htm",
      "source_kind": "earnings_release"
     },
     {
      "claim": "Mission-critical projects represented 92% of E-Infrastructure backlog at quarter end, indicating strong demand in data centers and semiconductor facilities.",
      "quote": "Mission-critical projects—including data centers, manufacturing, and semiconductor facilities—represented 92% of E-Infrastructure backlog at quarter end.",
      "doc_id": "STRL-8K-2026-08-03-ex99",
      "ok": true,
      "reason": "",
      "url": "https://www.sec.gov/Archives/edgar/data/874238/000087423826000100/a20260803ex991earningsrele.htm",
      "source_kind": "earnings_release"
     }
    ],
    "bear_case": [
     {
      "claim": "Building Solutions revenue declined 1% and adjusted operating income decreased 11%, and management expects housing market conditions to remain challenging through 2026.",
      "quote": "In Building Solutions, revenue declined 1%, reflecting relatively flat levels of homebuilder activity, while adjusted operating income decreased 11%. We expect market conditions to remain challenging through 2026 as housing affordability pressures continue to affect prospective homebuyers",
      "doc_id": "STRL-8K-2026-08-03-ex99",
      "ok": true,
      "reason": "",
      "url": "https://www.sec.gov/Archives/edgar/data/874238/000087423826000100/a20260803ex991earningsrele.htm",
      "source_kind": "earnings_release"
     },
     {
      "claim": "Transportation Solutions revenue decreased $40.1 million, or 20%, in the second quarter of 2026 compared to the prior year period.",
      "quote": "Revenues were $156.7 million for the second quarter of 2026, a decrease of $40.1 million, or 20%, compared to the second quarter of 2025.",
      "doc_id": "STRL-10Q-2026-08-04-mdna",
      "ok": true,
      "reason": "",
      "url": "https://www.sec.gov/Archives/edgar/data/874238/000087423826000103/strl-20260630.htm",
      "source_kind": "mdna"
     }
    ],
    "stripped": [],
    "documents": [
     {
      "doc_id": "STRL-8K-2026-08-03-ex99",
      "kind": "earnings_release",
      "title": "STRL 8-K earnings release (Exhibit 99.1), filed 2026-08-03",
      "url": "https://www.sec.gov/Archives/edgar/data/874238/000087423826000100/a20260803ex991earningsrele.htm",
      "filed": "2026-08-03",
      "chars_total": 27989,
      "chars_shown": 24000
     },
     {
      "doc_id": "STRL-10Q-2026-08-04-mdna",
      "kind": "mdna",
      "title": "STRL 10-Q for period 2026-06-30, MD&A, filed 2026-08-04",
      "url": "https://www.sec.gov/Archives/edgar/data/874238/000087423826000103/strl-20260630.htm",
      "filed": "2026-08-04",
      "chars_total": 32527,
      "chars_shown": 32527
     },
     {
      "doc_id": "STRL-news-2026-10-08-62254345",
      "kind": "news",
      "title": "Benzinga: Stifel Maintains Buy on Sterling Infrastructure, Lowers Price Target to $742 (2026-10-08)",
      "url": "https://www.benzinga.com/news/26/10/62254345/stifel-maintains-buy-sterling-infrastructure-lowers-price-target-742",
      "filed": "2026-10-08",
      "chars_total": 76,
      "chars_shown": 76
     },
     {
      "doc_id": "STRL-news-2026-09-30-62073161",
      "kind": "news",
      "title": "Benzinga: Cantor Fitzgerald Reiterates Overweight on Sterling Infrastructure, Maintains $742 Price Target (2026-09-30)",
      "url": "https://www.benzinga.com/news/26/09/62073161/cantor-fitzgerald-reiterates-overweight-sterling-infrastructure-maintains-742-price-target",
      "filed": "2026-09-30",
      "chars_total": 95,
      "chars_shown": 95
     },
     {
      "doc_id": "STRL-news-2026-09-28-62023821",
      "kind": "news",
      "title": "Benzinga: Here's How Much $1000 Invested In Sterling Infrastructure 20 Years Ago Would Be Worth Today (2026-09-28)",
      "url": "https://www.benzinga.com/news/26/09/62023821/here-s-how-much-1000-invested-sterling-infrastructure-20-years-ago-would-be-worth-today",
      "filed": "2026-09-28",
      "chars_total": 306,
      "chars_shown": 306
     },
     {
      "doc_id": "STRL-news-2026-09-08-61651775",
      "kind": "news",
      "title": "Benzinga: Raoul Pal Says There’s ‘Almost No Way’ AI Data Centers Don’t Trigger a Supercycle — 3 Stocks Positioned to Benefit (2026-09-08)",
      "url": "https://www.benzinga.com/markets/tech/26/09/61651775/raoul-pal-says-data-centers-are-only-30-percent-built-and-calls-it-an-inevitable-supercycle",
      "filed": "2026-09-08",
      "chars_total": 228,
      "chars_shown": 228
     }
    ],
    "model_status": "model said evidence: sufficient"
   },
   {
    "symbol": "SANM",
    "verdict": "explained",
    "thesis": [
     {
      "claim": "The drawdown may reflect investor concern about integration risk from the ZT Systems acquisition, which the company's own filings identify as a key risk.",
      "quote": "the risk that the integration of and expected benefits from the ZT Systems acquisition may not be realized or may take longer to realize than anticipated;",
      "doc_id": "SANM-8K-2026-07-27-ex99",
      "ok": true,
      "reason": "",
      "url": "https://www.sec.gov/Archives/edgar/data/897723/000089772326000036/sanmina_exx991xjune272026.htm",
      "source_kind": "earnings_release"
     },
     {
      "claim": "Interest expense surged due to acquisition-related borrowing, which could undermine earnings quality despite revenue growth.",
      "quote": "Interest expense was $32 million and $5 million for the three months ended June 27, 2026 and June 28, 2025, respectively and $89 million and $15 million for the nine months ended June 27, 2026 and June 28, 2025, respectively.",
      "doc_id": "SANM-10Q-2026-07-27-mdna",
      "ok": true,
      "reason": "",
      "url": "https://www.sec.gov/Archives/edgar/data/897723/000089772326000037/sanm-20260627.htm",
      "source_kind": "mdna"
     },
     {
      "claim": "High customer concentration, with one customer representing 10% or more of quarterly sales, may raise concerns about revenue sustainability.",
      "quote": "One customer represented 10% or more of our net sales for the three months ended June 27, 2026 and two customers represented 10% or more of our net sales for the nine months ended June 27, 2026.",
      "doc_id": "SANM-10Q-2026-07-27-mdna",
      "ok": true,
      "reason": "",
      "url": "https://www.sec.gov/Archives/edgar/data/897723/000089772326000037/sanm-20260627.htm",
      "source_kind": "mdna"
     }
    ],
    "bear_case": [
     {
      "claim": "The ZT Systems acquisition entails up to $450 million in contingent cash consideration and a recognized $183 million liability, adding future cash obligations that could pressure valuation.",
      "quote": "The seller is also entitled to up to $450 million in contingent cash consideration upon the achievement of certain gross profit and revenue metrics during the three-year period following the Closing Date. Additionally, we recognized $183 million fair value of contingent cash consideration liability as of June 27, 2026.",
      "doc_id": "SANM-10Q-2026-07-27-mdna",
      "ok": true,
      "reason": "",
      "url": "https://www.sec.gov/Archives/edgar/data/897723/000089772326000037/sanm-20260627.htm",
      "source_kind": "mdna"
     },
     {
      "claim": "The company incurred $21 million in acquisition, integration and other expenses in the quarter, reducing GAAP profitability and indicating ongoing integration costs.",
      "quote": "Acquisition, integration and others were $21 million and $137 million for the three and nine months ended June 27, 2026 respectively, and were related to the ZT Acquisition.",
      "doc_id": "SANM-10Q-2026-07-27-mdna",
      "ok": true,
      "reason": "",
      "url": "https://www.sec.gov/Archives/edgar/data/897723/000089772326000037/sanm-20260627.htm",
      "source_kind": "mdna"
     }
    ],
    "stripped": [
     {
      "claim": "Outside the acquired business, CPS gross margin declined to 12.8% from 14.7% due to manufacturing inefficiencies, signaling operational headwinds.",
      "quote": "CPS gross margin decreased to 12.8% from 14.7% for the three months ended June 27, 2026 and June 28, 2025. The decrease in gross margin is primarily due to manufacturing inefficiencies.",
      "doc_id": "SANM-10Q-2026-07-27-mdna",
      "ok": false,
      "reason": "quote not found verbatim in the cited document",
      "url": "https://www.sec.gov/Archives/edgar/data/897723/000089772326000037/sanm-20260627.htm",
      "source_kind": "mdna"
     }
    ],
    "documents": [
     {
      "doc_id": "SANM-8K-2026-07-27-ex99",
      "kind": "earnings_release",
      "title": "SANM 8-K earnings release (Exhibit 99.1), filed 2026-07-27",
      "url": "https://www.sec.gov/Archives/edgar/data/897723/000089772326000036/sanmina_exx991xjune272026.htm",
      "filed": "2026-07-27",
      "chars_total": 18541,
      "chars_shown": 18541
     },
     {
      "doc_id": "SANM-10Q-2026-07-27-mdna",
      "kind": "mdna",
      "title": "SANM 10-Q for period 2026-06-27, MD&A, filed 2026-07-27",
      "url": "https://www.sec.gov/Archives/edgar/data/897723/000089772326000037/sanm-20260627.htm",
      "filed": "2026-07-27",
      "chars_total": 35334,
      "chars_shown": 35334
     },
     {
      "doc_id": "SANM-news-2026-10-06-62206336",
      "kind": "news",
      "title": "Benzinga: Here’s How Much You Would Have Made Owning Sanmina Stock In The Last 5 Years (2026-10-06)",
      "url": "https://www.benzinga.com/news/26/10/62206336/here-s-how-much-you-would-have-made-owning-sanmina-stock-last-5-years",
      "filed": "2026-10-06",
      "chars_total": 293,
      "chars_shown": 293
     },
     {
      "doc_id": "SANM-news-2026-09-18-61883541",
      "kind": "news",
      "title": "Benzinga: $1000 Invested In Sanmina 20 Years Ago Would Be Worth This Much Today (2026-09-18)",
      "url": "https://www.benzinga.com/news/26/09/61883541/1000-invested-sanmina-20-years-ago-would-be-worth-much-today",
      "filed": "2026-09-18",
      "chars_total": 286,
      "chars_shown": 286
     },
     {
      "doc_id": "SANM-news-2026-09-15-61794483",
      "kind": "news",
      "title": "Benzinga: Here’s How Much You Would Have Made Owning Sanmina Stock In The Last 20 Years (2026-09-15)",
      "url": "https://www.benzinga.com/news/26/09/61794483/here-s-how-much-you-would-have-made-owning-sanmina-stock-last-20-years",
      "filed": "2026-09-15",
      "chars_total": 294,
      "chars_shown": 294
     }
    ],
    "model_status": "model said evidence: sufficient"
   },
   {
    "symbol": "KLIC",
    "verdict": "explained",
    "thesis": [
     {
      "claim": "The company reported third quarter net revenue of $330.4 million and net income of $57.4 million, indicating strong recent fundamentals.",
      "quote": "The Company reported third quarter net revenue of $330.4 million, net income of $57.4 million, representing EPS of $1.07 per fully diluted share, and non-GAAP net income of $64.2 million, representing non-GAAP EPS of $1.20 per fully diluted share.",
      "doc_id": "KLIC-8K-2026-08-05-ex99",
      "ok": true,
      "reason": "",
      "url": "https://www.sec.gov/Archives/edgar/data/56978/000005697826000030/ex991liveq32026.htm",
      "source_kind": "earnings_release"
     },
     {
      "claim": "Management stated that demand conditions continue to improve across all end markets.",
      "quote": "We see strong sequential growth in the third quarter and demand conditions continue to improve across all end markets.",
      "doc_id": "KLIC-8K-2026-08-05-ex99",
      "ok": true,
      "reason": "",
      "url": "https://www.sec.gov/Archives/edgar/data/56978/000005697826000030/ex991liveq32026.htm",
      "source_kind": "earnings_release"
     },
     {
      "claim": "The company guides fourth quarter net revenue to approximately $375 million with GAAP diluted EPS of approximately $1.29.",
      "quote": "K&S currently expects net revenue in the fourth quarter of fiscal 2026 ending October 3, 2026 to be approximately $375 million +/- $20 million, GAAP diluted EPS to be approximately $1.29 +/- 10%, and non-GAAP diluted EPS to be approximately $1.42 +/- 10%.",
      "doc_id": "KLIC-8K-2026-08-05-ex99",
      "ok": true,
      "reason": "",
      "url": "https://www.sec.gov/Archives/edgar/data/56978/000005697826000030/ex991liveq32026.htm",
      "source_kind": "earnings_release"
     },
     {
      "claim": "The company anticipates its expanded Advanced Solutions production facility will be completed within the second half of fiscal 2027.",
      "quote": "Kulicke & Soffa anticipates its expanded Advanced Solutions production facility will be completed, as scheduled, within the second half of fiscal 2027.",
      "doc_id": "KLIC-8K-2026-08-05-ex99",
      "ok": true,
      "reason": "",
      "url": "https://www.sec.gov/Archives/edgar/data/56978/000005697826000030/ex991liveq32026.htm",
      "source_kind": "earnings_release"
     }
    ],
    "bear_case": [
     {
      "claim": "The filings warn of persistent macroeconomic headwinds and falling customer sentiment, potentially explaining price weakness despite strong results.",
      "quote": "the persistent macroeconomic headwinds on our business, actual or potential inflationary pressures, interest rate and risk premium adjustments, falling customer sentiment, or economic recession caused directly or indirectly by geopolitical tensions,",
      "doc_id": "KLIC-8K-2026-08-05-ex99",
      "ok": true,
      "reason": "",
      "url": "https://www.sec.gov/Archives/edgar/data/56978/000005697826000030/ex991liveq32026.htm",
      "source_kind": "earnings_release"
     },
     {
      "claim": "The filings also warn of failures or delays in completing the cessation of its Electronics Assembly equipment business.",
      "quote": "failures or delays in completing the Company's cessation of its Electronics Assembly equipment business",
      "doc_id": "KLIC-8K-2026-08-05-ex99",
      "ok": true,
      "reason": "",
      "url": "https://www.sec.gov/Archives/edgar/data/56978/000005697826000030/ex991liveq32026.htm",
      "source_kind": "earnings_release"
     },
     {
      "claim": "The filings warn that the company's ability to develop, manufacture and gain market acceptance of new products is a risk.",
      "quote": "our ability to develop, manufacture and gain market acceptance of new products",
      "doc_id": "KLIC-8K-2026-08-05-ex99",
      "ok": true,
      "reason": "",
      "url": "https://www.sec.gov/Archives/edgar/data/56978/000005697826000030/ex991liveq32026.htm",
      "source_kind": "earnings_release"
     }
    ],
    "stripped": [],
    "documents": [
     {
      "doc_id": "KLIC-8K-2026-08-05-ex99",
      "kind": "earnings_release",
      "title": "KLIC 8-K earnings release (Exhibit 99.1), filed 2026-08-05",
      "url": "https://www.sec.gov/Archives/edgar/data/56978/000005697826000030/ex991liveq32026.htm",
      "filed": "2026-08-05",
      "chars_total": 16377,
      "chars_shown": 16377
     },
     {
      "doc_id": "KLIC-10Q-2026-08-06-mdna",
      "kind": "mdna",
      "title": "KLIC 10-Q for period 2026-07-04, MD&A, filed 2026-08-06",
      "url": "https://www.sec.gov/Archives/edgar/data/56978/000005697826000032/klic-20260704.htm",
      "filed": "2026-08-06",
      "chars_total": 96,
      "chars_shown": 96
     },
     {
      "doc_id": "KLIC-news-2026-10-05-62156461",
      "kind": "news",
      "title": "Benzinga: Kulicke & Soffa Indus Q3 2026 Earnings Call: Complete Transcript (2026-10-05)",
      "url": "https://www.benzinga.com/news/26/10/62156461/kulicke-soffa-indus-q3-2026-earnings-call-complete-transcript",
      "filed": "2026-10-05",
      "chars_total": 280,
      "chars_shown": 280
     }
    ],
    "model_status": "model said evidence: sufficient"
   }
  ],
  "limits": [
   "Prices: Alpaca SIP daily bars, split and dividend adjusted; no intraday data used.",
   "Fundamentals: SEC XBRL companyfacts, US-GAAP filers only. Foreign private issuers (IFRS, 20-F/40-F) and companies without standard tags drop out as 'missing', they are not guessed.",
   "Market cap uses the latest cover-page share count; for multi-class issuers it can understate.",
   "Industry groups are SEC SIC codes, a coarse proxy for a theme (no GICS/BICS in free data).",
   "Short interest: FINRA consolidated short interest (twice monthly, non-commercial use); % is of shares outstanding, not float.",
   "Earnings-call transcripts are licensed content and were not used; explanations rely on the 8-K earnings release, 10-Q/10-K MD&A, and news headlines and summaries (Alpaca / Benzinga), never full articles.",
   "No consensus estimates, revisions, ownership or borrow-cost data: those need a licensed source."
  ]
 },
 {
  "id": "b-ai-infra-laggards",
  "as_of": "2026-10-08",
  "generated_at": "2026-10-08T22:53:53+00:00",
  "llm": {
   "provider": "deepseek",
   "model": "deepseek-v4-pro"
  },
  "data": {
   "as_of": "2026-10-08",
   "last_price_date": "2026-10-08",
   "universe_rule": "tradable US-listed (NYSE/Nasdaq/AMEX/Arca/BATS) operating companies with an SEC CIK and a 10-K/10-Q/20-F/40-F in the last 18 months; close >= $1; 50-day avg dollar volume >= $1,000,000; one listing per CIK",
   "n_companies": 3827,
   "short_interest_settlement": "2026-09-15",
   "benchmark_closes": {
    "IWM": 277.57,
    "QQQ": 747.58,
    "SMH": 607.27,
    "SOXX": 563.28,
    "SPY": 773.93,
    "XLB": 49.27,
    "XLC": 112.07,
    "XLE": 65.24,
    "XLF": 54.23,
    "XLI": 168.4,
    "XLK": 197.78,
    "XLP": 83.42,
    "XLRE": 40.85,
    "XLU": 41.07,
    "XLV": 168.16,
    "XLY": 111.71
   },
   "files": {
    "prices.csv.gz": {
     "sha256": "2fb70ee43a9d30a4174c2353a1eca23798fb267cd09557d74d1af3cc6146d0e1",
     "bytes": 50692072
    },
    "features.csv.gz": {
     "sha256": "cf63f29b2cc08badaf287c158d7e85c689a249e386a9f0f9c0b85029e0510c87",
     "bytes": 3541921
    }
   }
  },
  "observation": "AI-infrastructure suppliers (semis, networking, power, data-center REITs and neoclouds) whose shares lag the semiconductor index over 3 months while revenue growth is accelerating.",
  "spec": {
   "version": 1,
   "observation": "AI-infrastructure suppliers (semis, networking, power, data-center REITs and neoclouds) whose shares lag the semiconductor index over 3 months while revenue growth is accelerating.",
   "universe": {
    "themes": [
     "ai_semis",
     "ai_networking",
     "ai_power",
     "data_center_reits",
     "neoclouds"
    ]
   },
   "conditions": [
    {
     "field": "rs_3m_vs_soxx",
     "op": "<",
     "value": 0,
     "why": "shares lag the semiconductor index over 3 months"
    },
    {
     "field": "revenue_growth_accel",
     "op": ">",
     "value": 0,
     "why": "revenue growth is accelerating"
    }
   ],
   "rank": [
    {
     "field": "revenue_growth_accel",
     "direction": "desc",
     "weight": 1
    }
   ],
   "top_n": 5,
   "unmapped": [],
   "notes": "SOXX is used as the semiconductor index. The AI-infrastructure supplier universe is defined by the listed curated theme baskets, which include the named segments. No explicit ranking was requested, so results are ranked by revenue growth acceleration to surface the most accelerating names among the filtered set."
  },
  "attempts": 1,
  "funnel": [
   {
    "step": "universe (liquid US common stocks with SEC filings)",
    "kind": "start",
    "n_in": 3827,
    "n_pass": 3827,
    "n_fail": 0,
    "n_missing": 0
   },
   {
    "step": "theme in ['ai_semis', 'ai_networking', 'ai_power', 'data_center_reits', 'neoclouds']",
    "kind": "universe",
    "n_in": 3827,
    "n_pass": 38,
    "n_fail": 3789,
    "n_missing": 0
   },
   {
    "step": "rs_3m_vs_soxx < +0.0%",
    "kind": "condition",
    "n_in": 38,
    "n_pass": 20,
    "n_fail": 18,
    "n_missing": 0
   },
   {
    "step": "revenue_growth_accel > +0.0%",
    "kind": "condition",
    "n_in": 20,
    "n_pass": 13,
    "n_fail": 6,
    "n_missing": 1
   }
  ],
  "columns": [
   "rank",
   "symbol",
   "name",
   "sector",
   "score",
   "market_cap",
   "rs_3m_vs_soxx",
   "revenue_growth_accel"
  ],
  "ranked": [
   {
    "rank": 1,
    "symbol": "AVGO",
    "name": "Broadcom Inc.",
    "sector": "Information Technology",
    "score": 1.0,
    "market_cap": 1719175059581.1,
    "rs_3m_vs_soxx": -0.0675036907772798,
    "revenue_growth_accel": 0.3762635045900164
   },
   {
    "rank": 2,
    "symbol": "AAOI",
    "name": "APPLIED OPTOELECTRONICS, INC.",
    "sector": "Information Technology",
    "score": 0.9230769230769231,
    "market_cap": 8955882198.300001,
    "rs_3m_vs_soxx": -0.0864788864108246,
    "revenue_growth_accel": 0.3506149971483103
   },
   {
    "rank": 3,
    "symbol": "AMAT",
    "name": "APPLIED MATERIALS INC /DE",
    "sector": "Information Technology",
    "score": 0.8461538461538461,
    "market_cap": 404393449029.51,
    "rs_3m_vs_soxx": -0.1229089208380119,
    "revenue_growth_accel": 0.1342036331932983
   },
   {
    "rank": 4,
    "symbol": "COHR",
    "name": "COHERENT CORP.",
    "sector": "Information Technology",
    "score": 0.7692307692307693,
    "market_cap": 59209879578.100006,
    "rs_3m_vs_soxx": -0.0378264720123197,
    "revenue_growth_accel": 0.1319774968411167
   },
   {
    "rank": 5,
    "symbol": "AMKR",
    "name": "AMKOR TECHNOLOGY, INC.",
    "sector": "Information Technology",
    "score": 0.6923076923076923,
    "market_cap": 12641498418.0,
    "rs_3m_vs_soxx": -0.244517853911289,
    "revenue_growth_accel": 0.1158300713073985
   },
   {
    "rank": 6,
    "symbol": "ALAB",
    "name": "Astera Labs, Inc.",
    "sector": "Information Technology",
    "score": 0.6153846153846154,
    "market_cap": 60208005343.200005,
    "rs_3m_vs_soxx": -0.1291917980042427,
    "revenue_growth_accel": 0.110547573054933
   },
   {
    "rank": 7,
    "symbol": "EQIX",
    "name": "EQUINIX INC",
    "sector": "Real Estate",
    "score": 0.5384615384615384,
    "market_cap": 99772862015.76,
    "rs_3m_vs_soxx": -0.0030694904360442,
    "revenue_growth_accel": 0.065136863495099
   },
   {
    "rank": 8,
    "symbol": "LRCX",
    "name": "LAM RESEARCH CORP",
    "sector": "Information Technology",
    "score": 0.46153846153846156,
    "market_cap": 401160999390.0,
    "rs_3m_vs_soxx": -0.0534914892425522,
    "revenue_growth_accel": 0.0623317116572177
   },
   {
    "rank": 9,
    "symbol": "CSCO",
    "name": "CISCO SYSTEMS, INC.",
    "sector": "Information Technology",
    "score": 0.38461538461538464,
    "market_cap": 452963805838.97,
    "rs_3m_vs_soxx": -0.0188062749225083,
    "revenue_growth_accel": 0.0561805876362047
   },
   {
    "rank": 10,
    "symbol": "GEV",
    "name": "GE Vernova Inc.",
    "sector": "Industrials",
    "score": 0.3076923076923077,
    "market_cap": 266160464172.35,
    "rs_3m_vs_soxx": -0.0540514291156384,
    "revenue_growth_accel": 0.0560224664944655
   },
   {
    "rank": 11,
    "symbol": "KLAC",
    "name": "KLA CORP",
    "sector": "Information Technology",
    "score": 0.23076923076923078,
    "market_cap": 257023883151.76,
    "rs_3m_vs_soxx": -0.1189233157651805,
    "revenue_growth_accel": 0.0371452001798928
   },
   {
    "rank": 12,
    "symbol": "POWL",
    "name": "POWELL INDUSTRIES INC",
    "sector": "Industrials",
    "score": 0.15384615384615385,
    "market_cap": 6895591388.280001,
    "rs_3m_vs_soxx": -0.1540650054806537,
    "revenue_growth_accel": 0.0244163914680586
   },
   {
    "rank": 13,
    "symbol": "CRWV",
    "name": "CoreWeave, Inc.",
    "sector": "Information Technology",
    "score": 0.07692307692307693,
    "market_cap": 44950580000.0,
    "rs_3m_vs_soxx": -0.0517008255493682,
    "revenue_growth_accel": 0.0084978457112514
   }
  ],
  "sector_breakdown": [
   {
    "sector": "Information Technology",
    "n": 10
   },
   {
    "sector": "Industrials",
    "n": 2
   },
   {
    "sector": "Real Estate",
    "n": 1
   }
  ],
  "n_ranked": 13,
  "top_n": 5,
  "explanations": [
   {
    "symbol": "AVGO",
    "verdict": "explained",
    "thesis": [
     {
      "claim": "Broadcom reported third-quarter revenue of $29.6 billion, up 86 percent from the prior year period, indicating strong fundamental growth despite the stock's underperformance.",
      "quote": "Revenue of $29.6 billion for the third quarter, up 86 percent from the prior year period",
      "doc_id": "AVGO-8K-2026-09-02-ex99",
      "ok": true,
      "reason": "",
      "url": "https://www.sec.gov/Archives/edgar/data/1730168/000173016826000076/avgo-08022026x8kxex99.htm",
      "source_kind": "earnings_release"
     },
     {
      "claim": "Broadcom's AI semiconductor revenue grew 221% year-over-year to $16.7 billion in the third quarter, driving the reported revenue acceleration.",
      "quote": "Q3 AI semiconductor revenue of $16.7 billion grew 221% year-over-year, and 54% quarter-over-quarter",
      "doc_id": "AVGO-8K-2026-09-02-ex99",
      "ok": true,
      "reason": "",
      "url": "https://www.sec.gov/Archives/edgar/data/1730168/000173016826000076/avgo-08022026x8kxex99.htm",
      "source_kind": "earnings_release"
     },
     {
      "claim": "The company states that deploying AI infrastructure to meet demand requires customers to access significant capital, a financing dependency that may explain investor caution.",
      "quote": "deploying AI infrastructure to meet this demand requires our customers to access significant capital",
      "doc_id": "AVGO-10Q-2026-09-10-mdna",
      "ok": true,
      "reason": "",
      "url": "https://www.sec.gov/Archives/edgar/data/1730168/000173016826000080/avgo-20260802.htm",
      "source_kind": "mdna"
     },
     {
      "claim": "A news report says OpenAI's annualized revenue was about $20 billion below earlier reports, as AI stocks fell, which could explain sector-wide price pressure on Broadcom.",
      "quote": "New figures put OpenAI’s annualized revenue near $50 billion, about $20 billion below earlier reports, as AI stocks fell.",
      "doc_id": "AVGO-news-2026-10-08-62257221",
      "ok": true,
      "reason": "",
      "url": "https://www.benzinga.com/markets/prediction-markets/26/10/62257221/openai-revenue-run-rate-ai-stocks",
      "source_kind": "news"
     }
    ],
    "bear_case": [
     {
      "claim": "Broadcom's revenue is highly concentrated, with a single distributor customer accounting for 50% of net revenue in the fiscal quarter.",
      "quote": "Direct sales to one semiconductor solutions customer, which is a distributor, accounted for 50% and 46% of our net revenue for the fiscal quarter and three fiscal quarters ended August 2, 2026, respectively",
      "doc_id": "AVGO-10Q-2026-09-10-mdna",
      "ok": true,
      "reason": "",
      "url": "https://www.sec.gov/Archives/edgar/data/1730168/000173016826000080/avgo-20260802.htm",
      "source_kind": "mdna"
     },
     {
      "claim": "Broadcom's AI XPV platform exposes the company to a maximum backstop liability of approximately $29 billion if the customer defaults.",
      "quote": "Our maximum potential liability under the Backstop upon the deployment of all AI racks, on an undiscounted basis, was approximately $29 billion.",
      "doc_id": "AVGO-10Q-2026-09-10-mdna",
      "ok": true,
      "reason": "",
      "url": "https://www.sec.gov/Archives/edgar/data/1730168/000173016826000080/avgo-20260802.htm",
      "source_kind": "mdna"
     },
     {
      "claim": "A news report says Broadcom is among companies seeking blockbuster debt deals to pay for AI chips, increasing financial leverage risk.",
      "quote": "'Oracle, Broadcom and SpaceX Seek Blockbuster Debt Deals To Pay for AI Chips'- WSJ Exclusive",
      "doc_id": "AVGO-news-2026-10-07-62234456",
      "ok": true,
      "reason": "",
      "url": "https://www.benzinga.com/news/26/10/62234456/oracle-broadcom-and-spacex-seek-blockbuster-debt-deals-to-pay-for-ai-chips-wsj-exclusive",
      "source_kind": "news"
     }
    ],
    "stripped": [],
    "documents": [
     {
      "doc_id": "AVGO-8K-2026-09-02-ex99",
      "kind": "earnings_release",
      "title": "AVGO 8-K earnings release (Exhibit 99.1), filed 2026-09-02",
      "url": "https://www.sec.gov/Archives/edgar/data/1730168/000173016826000076/avgo-08022026x8kxex99.htm",
      "filed": "2026-09-02",
      "chars_total": 23341,
      "chars_shown": 23341
     },
     {
      "doc_id": "AVGO-10Q-2026-09-10-mdna",
      "kind": "mdna",
      "title": "AVGO 10-Q for period 2026-08-02, MD&A, filed 2026-09-10",
      "url": "https://www.sec.gov/Archives/edgar/data/1730168/000173016826000080/avgo-20260802.htm",
      "filed": "2026-09-10",
      "chars_total": 32120,
      "chars_shown": 32120
     },
     {
      "doc_id": "AVGO-news-2026-10-08-62257221",
      "kind": "news",
      "title": "Benzinga: OpenAI Revenue $20B Below Previous Reports, ORCL, NVDA Tumble (2026-10-08)",
      "url": "https://www.benzinga.com/markets/prediction-markets/26/10/62257221/openai-revenue-run-rate-ai-stocks",
      "filed": "2026-10-08",
      "chars_total": 183,
      "chars_shown": 183
     },
     {
      "doc_id": "AVGO-news-2026-10-08-62254694",
      "kind": "news",
      "title": "Benzinga: EXCLUSIVE: TSMC Plans Up to $64 Billion in Capex and Still Isn’t ‘Building Enough,’ Says Applied Materials Veteran (2026-10-08)",
      "url": "https://www.benzinga.com/markets/prediction-markets/26/10/62254694/tsmc-capex-64-billion-building-enough",
      "filed": "2026-10-08",
      "chars_total": 238,
      "chars_shown": 238
     },
     {
      "doc_id": "AVGO-news-2026-10-07-62234456",
      "kind": "news",
      "title": "Benzinga: 'Oracle, Broadcom and SpaceX Seek Blockbuster Debt Deals To Pay for AI Chips'- WSJ Exclusive (2026-10-07)",
      "url": "https://www.benzinga.com/news/26/10/62234456/oracle-broadcom-and-spacex-seek-blockbuster-debt-deals-to-pay-for-ai-chips-wsj-exclusive",
      "filed": "2026-10-07",
      "chars_total": 92,
      "chars_shown": 92
     },
     {
      "doc_id": "AVGO-news-2026-10-07-62235453",
      "kind": "news",
      "title": "Benzinga: $100 Invested In Broadcom 15 Years Ago Would Be Worth This Much Today (2026-10-07)",
      "url": "https://www.benzinga.com/news/26/10/62235453/100-invested-broadcom-15-years-ago-would-be-worth-much-today",
      "filed": "2026-10-07",
      "chars_total": 289,
      "chars_shown": 289
     },
     {
      "doc_id": "AVGO-news-2026-10-07-62228208",
      "kind": "news",
      "title": "Benzinga: Marvell Stock Is Up 230% This Year: Bank of America Sees a Further 40% Upside (2026-10-07)",
      "url": "https://www.benzinga.com/markets/tech/26/10/62228208/marvell-stock-investor-day-up-230-percent-2026-bofa-40-percent-upside",
      "filed": "2026-10-07",
      "chars_total": 193,
      "chars_shown": 193
     },
     {
      "doc_id": "AVGO-news-2026-10-07-62215731",
      "kind": "news",
      "title": "Benzinga: What's Going On With Broadcom Stock Wednesday? (2026-10-07)",
      "url": "https://www.benzinga.com/markets/tech/26/10/62215731/whats-going-on-with-broadcom-stock-wednesday-7",
      "filed": "2026-10-07",
      "chars_total": 179,
      "chars_shown": 179
     },
     {
      "doc_id": "AVGO-news-2026-10-06-62200140",
      "kind": "news",
      "title": "Benzinga: Challenging Nvidia's Dominance: Broadcom Pairs Custom TPU Chips with $60 Billion Debt Package (2026-10-06)",
      "url": "https://www.benzinga.com/markets/tech/26/10/62200140/challenging-nvidias-dominance-broadcom-pairs-custom-tpu-chips-with-60-billion-debt-package",
      "filed": "2026-10-06",
      "chars_total": 227,
      "chars_shown": 227
     },
     {
      "doc_id": "AVGO-news-2026-10-06-62198664",
      "kind": "news",
      "title": "Benzinga: Jim Cramer Sees Marvell Sending a Bigger Signal to Broadcom (2026-10-06)",
      "url": "https://www.benzinga.com/markets/tech/26/10/62198664/jim-cramer-sees-marvell-sending-a-bigger-signal-to-broadcom",
      "filed": "2026-10-06",
      "chars_total": 198,
      "chars_shown": 198
     },
     {
      "doc_id": "AVGO-news-2026-10-05-62178697",
      "kind": "news",
      "title": "Benzinga: 'Wall Street banks launch record $60B chip deal for Broadcom and Anthropic'- Financial Times (2026-10-05)",
      "url": "https://www.benzinga.com/news/26/10/62178697/wall-street-banks-launch-record-60b-chip-deal-broadcom-and-anthropic-financial-times",
      "filed": "2026-10-05",
      "chars_total": 92,
      "chars_shown": 92
     },
     {
      "doc_id": "AVGO-news-2026-10-05-62174172",
      "kind": "news",
      "title": "Benzinga: Nvidia, Broadcom May Be Surprisingly Safe From a 32-GW Hole in the AI Boom, Morgan Stanley Says (2026-10-05)",
      "url": "https://www.benzinga.com/markets/prediction-markets/26/10/62174172/nvidia-broadcom-ai-power-shortage",
      "filed": "2026-10-05",
      "chars_total": 219,
      "chars_shown": 219
     },
     {
      "doc_id": "AVGO-news-2026-10-04-62152166",
      "kind": "news",
      "title": "Benzinga: LinkedIn Cofounder Defends Massive AI Infrastructure Spending, Says AI Capital Is 'the Only Reason We’re Not in a Recession' (2026-10-04)",
      "url": "https://www.benzinga.com/markets/economic-data/26/10/62152166/linkedin-cofounder-defends-massive-ai-infrastructure-spending-says-ai-capital-is-the-only-reason-were-not-in-a-recession",
      "filed": "2026-10-04",
      "chars_total": 264,
      "chars_shown": 264
     },
     {
      "doc_id": "AVGO-news-2026-10-02-62143884",
      "kind": "news",
      "title": "Benzinga: Taiwan Semiconductor Stock Rises on Broadcom's $60 Billion Chip Deal (2026-10-02)",
      "url": "https://www.benzinga.com/trading-ideas/movers/26/10/62143884/taiwan-semiconductor-stock-rises-on-broadcoms-60-billion-chip-deal",
      "filed": "2026-10-02",
      "chars_total": 209,
      "chars_shown": 209
     }
    ],
    "model_status": "model said evidence: sufficient"
   },
   {
    "symbol": "AAOI",
    "verdict": "explained",
    "thesis": [
     {
      "claim": "Although revenue increased sharply year over year, GAAP net loss widened to $22.8 million from $9.1 million, which may explain why the stock underperformed despite strong sales growth.",
      "quote": "GAAP net loss was $22.8 million, or $0.28 per basic share, compared with net loss of $9.1 million, or $0.16 per basic share in the second quarter of 2025, and a net loss of $14.3 million, or $0.19 per basic share in the first quarter of 2026.",
      "doc_id": "AAOI-8K-2026-08-06-ex99",
      "ok": true,
      "reason": "",
      "url": "https://www.sec.gov/Archives/edgar/data/1158114/000168316826006055/aaoi_ex9901.htm",
      "source_kind": "earnings_release"
     },
     {
      "claim": "The company's gross margin declined to 27.7% from 30.3% a year earlier, indicating that revenue growth is coming at the cost of profitability, a potential reason for investor skepticism.",
      "quote": "GAAP gross margin was 27.7%, compared with 30.3% in the second quarter of 2025 and 29.1% in the first quarter of 2026.",
      "doc_id": "AAOI-8K-2026-08-06-ex99",
      "ok": true,
      "reason": "",
      "url": "https://www.sec.gov/Archives/edgar/data/1158114/000168316826006055/aaoi_ex9901.htm",
      "source_kind": "earnings_release"
     },
     {
      "claim": "The company issued a large number of shares through at-the-market offerings, which may have pressured the stock price despite strong fundamentals.",
      "quote": "On April 2, 2026, the Company completed the First ATM Offering and sold approximately 4.8 million shares at a weighted average price of $103.51 per share, providing proceeds of approximately $490 million, net of expenses and underwriting discounts and commissions.",
      "doc_id": "AAOI-10Q-2026-08-06-mdna",
      "ok": true,
      "reason": "",
      "url": "https://www.sec.gov/Archives/edgar/data/1158114/000143774926026278/aaoi20260630_10q.htm",
      "source_kind": "mdna"
     },
     {
      "claim": "A news report says the stock slid alongside the broader fiber optic connectivity sector, suggesting sector-wide pressure rather than company-specific bad news.",
      "quote": "Applied Optoelectronics shares fall Monday afternoon, sliding alongside the broader fiber optic connectivity sector.",
      "doc_id": "AAOI-news-2026-09-28-62035697",
      "ok": true,
      "reason": "",
      "url": "https://www.benzinga.com/trading-ideas/movers/26/09/62035697/applied-optoelectronics-stock-slides-monday-whats-happening",
      "source_kind": "news"
     }
    ],
    "bear_case": [
     {
      "claim": "Net cash used in operating activities was $73.8 million in the first half of 2026, meaning the company is still consuming cash despite rapid revenue growth.",
      "quote": "Net cash used in operating activities was $73.8 million during the six months ended June 30, 2026 as compared to $116.4 million during the six months ended June 30, 2025, a decrease of 36.6%.",
      "doc_id": "AAOI-10Q-2026-08-06-mdna",
      "ok": true,
      "reason": "",
      "url": "https://www.sec.gov/Archives/edgar/data/1158114/000143774926026278/aaoi20260630_10q.htm",
      "source_kind": "mdna"
     },
     {
      "claim": "The company's GAAP net loss widened to $22.8 million from $9.1 million a year earlier, indicating profitability remains elusive.",
      "quote": "GAAP net loss was $22.8 million, or $0.28 per basic share, compared with net loss of $9.1 million, or $0.16 per basic share in the second quarter of 2025, and a net loss of $14.3 million, or $0.19 per basic share in the first quarter of 2026.",
      "doc_id": "AAOI-8K-2026-08-06-ex99",
      "ok": true,
      "reason": "",
      "url": "https://www.sec.gov/Archives/edgar/data/1158114/000168316826006055/aaoi_ex9901.htm",
      "source_kind": "earnings_release"
     },
     {
      "claim": "Revenues from a single customer, Digicomm, represented approximately 42.8% of consolidated revenues, exposing the company to significant customer concentration risk.",
      "quote": "For the six months ended June 30, 2026, revenues from Digicomm were approximately $147.0 million, representing approximately 42.8% of consolidated revenues.",
      "doc_id": "AAOI-10Q-2026-08-06-mdna",
      "ok": true,
      "reason": "",
      "url": "https://www.sec.gov/Archives/edgar/data/1158114/000143774926026278/aaoi20260630_10q.htm",
      "source_kind": "mdna"
     }
    ],
    "stripped": [],
    "documents": [
     {
      "doc_id": "AAOI-8K-2026-08-06-ex99",
      "kind": "earnings_release",
      "title": "AAOI 8-K earnings release (Exhibit 99.1), filed 2026-08-06",
      "url": "https://www.sec.gov/Archives/edgar/data/1158114/000168316826006055/aaoi_ex9901.htm",
      "filed": "2026-08-06",
      "chars_total": 18597,
      "chars_shown": 18597
     },
     {
      "doc_id": "AAOI-10Q-2026-08-06-mdna",
      "kind": "mdna",
      "title": "AAOI 10-Q for period 2026-06-30, MD&A, filed 2026-08-06",
      "url": "https://www.sec.gov/Archives/edgar/data/1158114/000143774926026278/aaoi20260630_10q.htm",
      "filed": "2026-08-06",
      "chars_total": 45805,
      "chars_shown": 40000
     },
     {
      "doc_id": "AAOI-news-2026-10-06-62194091",
      "kind": "news",
      "title": "Benzinga: Applied Optoelectronics Stock Rises on Possible Continued Momentum as It Completes Share Sale (2026-10-06)",
      "url": "https://www.benzinga.com/trading-ideas/movers/26/10/62194091/applied-optoelectronics-stock-rises-on-possible-continued-momentum-as-it-completes-share-sale",
      "filed": "2026-10-06",
      "chars_total": 232,
      "chars_shown": 232
     },
     {
      "doc_id": "AAOI-news-2026-09-28-62035697",
      "kind": "news",
      "title": "Benzinga: Applied Optoelectronics Stock Slides Monday: What's Happening? (2026-09-28)",
      "url": "https://www.benzinga.com/trading-ideas/movers/26/09/62035697/applied-optoelectronics-stock-slides-monday-whats-happening",
      "filed": "2026-09-28",
      "chars_total": 179,
      "chars_shown": 179
     },
     {
      "doc_id": "AAOI-news-2026-09-08-61666003",
      "kind": "news",
      "title": "Benzinga: Why Is Applied Optoelectronics Stock Surging Tuesday? (2026-09-08)",
      "url": "https://www.benzinga.com/trading-ideas/movers/26/09/61666003/why-is-applied-optoelectronics-stock-surging-tuesday",
      "filed": "2026-09-08",
      "chars_total": 178,
      "chars_shown": 178
     }
    ],
    "model_status": "model said evidence: sufficient"
   },
   {
    "symbol": "AMAT",
    "verdict": "explained",
    "thesis": [
     {
      "claim": "Applied reported record revenue of $9.12 billion, up 25 percent year over year, while its stock underperformed peers, suggesting a dislocation driven by non-operating concerns.",
      "quote": "Record revenue $9.12 billion, up 25 percent year over year",
      "doc_id": "AMAT-8K-2026-08-13-ex99",
      "ok": true,
      "reason": "",
      "url": "https://www.sec.gov/Archives/edgar/data/6951/000162828026056699/exhibit991q32026earningsre.htm",
      "source_kind": "earnings_release"
     },
     {
      "claim": "The company's own forward-looking risk disclosure cites export-license and trade-policy uncertainties that may explain the stock's relative underperformance despite accelerating revenue.",
      "quote": "global trade issues, changes in trade and export regulations, license requirements, and their interpretation, and our ability to obtain licenses or authorizations on a timely basis, if at all",
      "doc_id": "AMAT-8K-2026-08-13-ex99",
      "ok": true,
      "reason": "",
      "url": "https://www.sec.gov/Archives/edgar/data/6951/000162828026056699/exhibit991q32026earningsre.htm",
      "source_kind": "earnings_release"
     },
     {
      "claim": "A news report says Morgan Stanley maintained an Equal-Weight rating and lowered its price target to $563, indicating analyst caution despite the strong earnings release.",
      "quote": "Morgan Stanley Maintains Equal-Weight on Applied Materials, Lowers Price Target to $563",
      "doc_id": "AMAT-news-2026-09-28-62019127",
      "ok": true,
      "reason": "",
      "url": "https://www.benzinga.com/news/26/09/62019127/morgan-stanley-maintains-equal-weight-applied-materials-lowers-price-target-563",
      "source_kind": "news"
     }
    ],
    "bear_case": [
     {
      "claim": "U.S. export controls have already limited Applied's ability to sell certain products and services to customers in China, and further updates could reduce its revenue in that key market.",
      "quote": "The United States government has implemented export regulations for U.S. semiconductor technology sold or provided to customers in China, which have limited our ability to provide certain products and services to customers in China, over the past several years.",
      "doc_id": "AMAT-10Q-2026-08-20-mdna",
      "ok": true,
      "reason": "",
      "url": "https://www.sec.gov/Archives/edgar/data/6951/000162828026058235/amat-20260726.htm",
      "source_kind": "mdna"
     },
     {
      "claim": "The company's forward-looking risk factors include the concentrated nature of its customer base, which may make investors discount robust current growth.",
      "quote": "the concentrated nature of our customer base",
      "doc_id": "AMAT-8K-2026-08-13-ex99",
      "ok": true,
      "reason": "",
      "url": "https://www.sec.gov/Archives/edgar/data/6951/000162828026056699/exhibit991q32026earningsre.htm",
      "source_kind": "earnings_release"
     }
    ],
    "stripped": [],
    "documents": [
     {
      "doc_id": "AMAT-8K-2026-08-13-ex99",
      "kind": "earnings_release",
      "title": "AMAT 8-K earnings release (Exhibit 99.1), filed 2026-08-13",
      "url": "https://www.sec.gov/Archives/edgar/data/6951/000162828026056699/exhibit991q32026earningsre.htm",
      "filed": "2026-08-13",
      "chars_total": 29178,
      "chars_shown": 24000
     },
     {
      "doc_id": "AMAT-10Q-2026-08-20-mdna",
      "kind": "mdna",
      "title": "AMAT 10-Q for period 2026-07-26, MD&A, filed 2026-08-20",
      "url": "https://www.sec.gov/Archives/edgar/data/6951/000162828026058235/amat-20260726.htm",
      "filed": "2026-08-20",
      "chars_total": 37677,
      "chars_shown": 37677
     },
     {
      "doc_id": "AMAT-news-2026-10-08-62254694",
      "kind": "news",
      "title": "Benzinga: EXCLUSIVE: TSMC Plans Up to $64 Billion in Capex and Still Isn’t ‘Building Enough,’ Says Applied Materials Veteran (2026-10-08)",
      "url": "https://www.benzinga.com/markets/prediction-markets/26/10/62254694/tsmc-capex-64-billion-building-enough",
      "filed": "2026-10-08",
      "chars_total": 238,
      "chars_shown": 238
     },
     {
      "doc_id": "AMAT-news-2026-10-08-62249820",
      "kind": "news",
      "title": "Benzinga: New Jersey Rep. Josh Gottheimer Sold Up to $30K Worth of Applied Materials Stock (2026-10-08)",
      "url": "https://www.benzinga.com/government/26/10/62249820/new-jersey-rep-josh-gottheimer-sold-30k-worth-applied-materials-stock",
      "filed": "2026-10-08",
      "chars_total": 294,
      "chars_shown": 294
     },
     {
      "doc_id": "AMAT-news-2026-10-06-62194124",
      "kind": "news",
      "title": "Benzinga: Here’s How Much You Would Have Made Owning Applied Materials Stock In The Last 20 Years (2026-10-06)",
      "url": "https://www.benzinga.com/news/26/10/62194124/here-s-how-much-you-would-have-made-owning-applied-materials-stock-last-20-years",
      "filed": "2026-10-06",
      "chars_total": 305,
      "chars_shown": 305
     },
     {
      "doc_id": "AMAT-news-2026-10-06-62189088",
      "kind": "news",
      "title": "Benzinga: Applied Materials, Intel Partnering Over Development Of Chipmaking Innovations For Transistors, Interconnects, Packing Technologies (2026-10-06)",
      "url": "https://www.benzinga.com/news/26/10/62189088/applied-materials-intel-partnering-over-development-chipmaking-innovations-transistors-interconnects",
      "filed": "2026-10-06",
      "chars_total": 131,
      "chars_shown": 131
     },
     {
      "doc_id": "AMAT-news-2026-10-01-62105025",
      "kind": "news",
      "title": "Benzinga: Applied Materials, BE Semiconductor Industries Announce BE Joins EPIC Center As Innovation Partner (2026-10-01)",
      "url": "https://www.benzinga.com/news/26/10/62105025/applied-materials-be-semiconductor-industries-announce-be-joins-epic-center-innovation-partner",
      "filed": "2026-10-01",
      "chars_total": 98,
      "chars_shown": 98
     },
     {
      "doc_id": "AMAT-news-2026-09-30-62076294",
      "kind": "news",
      "title": "Benzinga: What's Going On With Applied Materials Stock Wednesday? (2026-09-30)",
      "url": "https://www.benzinga.com/markets/tech/26/09/62076294/whats-going-on-with-applied-materials-stock-tuesday",
      "filed": "2026-09-30",
      "chars_total": 174,
      "chars_shown": 174
     },
     {
      "doc_id": "AMAT-news-2026-09-29-62065311",
      "kind": "news",
      "title": "Benzinga: Applied Materials Says Kioxia Joins Its EPIC Center As Partner To Develop Next-Generation AI Memory Technologies (2026-09-29)",
      "url": "https://www.benzinga.com/quote/AMAT",
      "filed": "2026-09-29",
      "chars_total": 112,
      "chars_shown": 112
     },
     {
      "doc_id": "AMAT-news-2026-09-28-62019127",
      "kind": "news",
      "title": "Benzinga: Morgan Stanley Maintains Equal-Weight on Applied Materials, Lowers Price Target to $563 (2026-09-28)",
      "url": "https://www.benzinga.com/news/26/09/62019127/morgan-stanley-maintains-equal-weight-applied-materials-lowers-price-target-563",
      "filed": "2026-09-28",
      "chars_total": 87,
      "chars_shown": 87
     },
     {
      "doc_id": "AMAT-news-2026-09-23-61950302",
      "kind": "news",
      "title": "Benzinga: $100 Invested In Applied Materials 20 Years Ago Would Be Worth This Much Today (2026-09-23)",
      "url": "https://www.benzinga.com/news/26/09/61950302/100-invested-applied-materials-20-years-ago-would-be-worth-much-today",
      "filed": "2026-09-23",
      "chars_total": 296,
      "chars_shown": 296
     },
     {
      "doc_id": "AMAT-news-2026-09-18-61869553",
      "kind": "news",
      "title": "Benzinga: What's Going On With Applied Materials Stock Friday? (2026-09-18)",
      "url": "https://www.benzinga.com/markets/tech/26/09/61869553/whats-going-on-with-applied-materials-stock-friday",
      "filed": "2026-09-18",
      "chars_total": 184,
      "chars_shown": 184
     },
     {
      "doc_id": "AMAT-news-2026-09-17-61834041",
      "kind": "news",
      "title": "Benzinga: Applied Materials To Invest $5B In India Over Next Decade To Deepen Semiconductor R&D (2026-09-17)",
      "url": "https://www.benzinga.com/news/26/09/61834041/applied-materials-invest-5b-india-over-next-decade-deepen-semiconductor-r-d",
      "filed": "2026-09-17",
      "chars_total": 85,
      "chars_shown": 85
     }
    ],
    "model_status": "model said evidence: sufficient"
   },
   {
    "symbol": "COHR",
    "verdict": "explained",
    "thesis": [
     {
      "claim": "Coherent reported fiscal Q4 revenue of $2.05B, up 34% year over year and 42% on a pro forma basis, showing accelerating growth that contrasts with its three-month relative underperformance.",
      "quote": "Q4 REVENUE OF $2.05B, INCREASED 34% Y/Y AND 42% Y/Y ON A PRO FORMA BASIS",
      "doc_id": "COHR-8K-2026-08-12-ex99",
      "ok": true,
      "reason": "",
      "url": "https://www.sec.gov/Archives/edgar/data/820318/000119312526346860/d128030dex991.htm",
      "source_kind": "earnings_release"
     },
     {
      "claim": "The company attributes revenue acceleration to AI datacenter demand, as hyperscale investments have boosted demand for its datacenter transceivers.",
      "quote": "The increasing investments by hyperscale and other cloud providers in AI datacenter infrastructures have significantly boosted demand for our datacenter transceivers.",
      "doc_id": "COHR-10K-2026-08-14-mdna",
      "ok": true,
      "reason": "",
      "url": "https://www.sec.gov/Archives/edgar/data/820318/000082031826000020/iivi-20260630.htm",
      "source_kind": "mdna"
     },
     {
      "claim": "The company is investing in manufacturing capacity for its Datacenter and Communications markets, which may pressure near-term free cash flow despite the revenue acceleration.",
      "quote": "We are investing in manufacturing capacity for the Datacenter and Communications markets, including expanding our indium phosphide capacity in Sherman, Texas, to address our increased customer demand and industry-wide shortage.",
      "doc_id": "COHR-10K-2026-08-14-mdna",
      "ok": true,
      "reason": "",
      "url": "https://www.sec.gov/Archives/edgar/data/820318/000082031826000020/iivi-20260630.htm",
      "source_kind": "mdna"
     }
    ],
    "bear_case": [
     {
      "claim": "Goodwill in the Lasers reporting unit is sensitive, with estimated fair value exceeding carrying value by only about 8%, leaving little cushion for a possible impairment charge.",
      "quote": "For the Lasers reporting unit, as of April 1, 2026, the estimated fair value exceeded the carrying value by approximately 8%.",
      "doc_id": "COHR-10K-2026-08-14-mdna",
      "ok": true,
      "reason": "",
      "url": "https://www.sec.gov/Archives/edgar/data/820318/000082031826000020/iivi-20260630.htm",
      "source_kind": "mdna"
     },
     {
      "claim": "The company's own risk disclosures state that its stock price may not trade in line with industrial technology leaders, which could explain the relative underperformance.",
      "quote": "the risks that the Company’s stock price will not trade in line with industrial technology leaders",
      "doc_id": "COHR-8K-2026-08-12-ex99",
      "ok": true,
      "reason": "",
      "url": "https://www.sec.gov/Archives/edgar/data/820318/000119312526346860/d128030dex991.htm",
      "source_kind": "earnings_release"
     }
    ],
    "stripped": [],
    "documents": [
     {
      "doc_id": "COHR-8K-2026-08-12-ex99",
      "kind": "earnings_release",
      "title": "COHR 8-K earnings release (Exhibit 99.1), filed 2026-08-12",
      "url": "https://www.sec.gov/Archives/edgar/data/820318/000119312526346860/d128030dex991.htm",
      "filed": "2026-08-12",
      "chars_total": 31267,
      "chars_shown": 24000
     },
     {
      "doc_id": "COHR-10K-2026-08-14-mdna",
      "kind": "mdna",
      "title": "COHR 10-K for period 2026-06-30, MD&A, filed 2026-08-14",
      "url": "https://www.sec.gov/Archives/edgar/data/820318/000082031826000020/iivi-20260630.htm",
      "filed": "2026-08-14",
      "chars_total": 51178,
      "chars_shown": 40000
     },
     {
      "doc_id": "COHR-news-2026-10-02-62125706",
      "kind": "news",
      "title": "Benzinga: Nike, Corteva, Mattel, Accenture and Coherent: Why These 5 Stocks Are on Investors' Radars Today (2026-10-02)",
      "url": "https://www.benzinga.com/news/26/10/62125706/nike-corteva-mattel-accenture-and-coherent-why-these-5-stocks-are-on-investors-radars-today",
      "filed": "2026-10-02",
      "chars_total": 185,
      "chars_shown": 185
     },
     {
      "doc_id": "COHR-news-2026-10-01-62117250",
      "kind": "news",
      "title": "Benzinga: Lumentum, Coherent Rip Higher As Washington Targets Chinese Optical Transceivers (2026-10-01)",
      "url": "https://www.benzinga.com/trading-ideas/movers/26/10/62117250/lumentum-coherent-rip-higher-as-washington-targets-chinese-optical-transceivers",
      "filed": "2026-10-01",
      "chars_total": 202,
      "chars_shown": 202
     },
     {
      "doc_id": "COHR-news-2026-09-30-62073486",
      "kind": "news",
      "title": "Benzinga: Bernstein Initiates Coverage On Coherent with Outperform Rating, Announces Price Target of $350 (2026-09-30)",
      "url": "https://www.benzinga.com/news/26/09/62073486/bernstein-initiates-coverage-coherent-outperform-rating-announces-price-target-350",
      "filed": "2026-09-30",
      "chars_total": 95,
      "chars_shown": 95
     },
     {
      "doc_id": "COHR-news-2026-09-29-62068212",
      "kind": "news",
      "title": "Benzinga: If You Invested $1000 In Coherent Stock 20 Years Ago, You Would Have This Much Today (2026-09-29)",
      "url": "https://www.benzinga.com/news/26/09/62068212/if-you-invested-1000-coherent-stock-20-years-ago-you-would-have-much-today",
      "filed": "2026-09-29",
      "chars_total": 300,
      "chars_shown": 300
     },
     {
      "doc_id": "COHR-news-2026-09-26-62010472",
      "kind": "news",
      "title": "Benzinga: Bipartisan Lawmakers Seek to Bar a Chinese AI Data Center Component From Sensitive US Government Systems: ‘We Shouldn’t Rely on China’ (2026-09-26)",
      "url": "https://www.benzinga.com/markets/tech/26/09/62010472/bipartisan-lawmakers-seek-to-bar-a-chinese-ai-data-center-component-from-sensitive-us-government-systems-we-shouldnt-rely-on-china",
      "filed": "2026-09-26",
      "chars_total": 259,
      "chars_shown": 259
     },
     {
      "doc_id": "COHR-news-2026-09-21-61888036",
      "kind": "news",
      "title": "Benzinga: CUbIQ And Coherent Announce Successful Proof-Of-Concept QKD Demonstrator, A Major Milestone Toward Deploying Physical-Layer Security In Existing AI Infrastructure (2026-09-21)",
      "url": "https://www.benzinga.com/quote/COHR",
      "filed": "2026-09-21",
      "chars_total": 162,
      "chars_shown": 162
     },
     {
      "doc_id": "COHR-news-2026-09-17-61856234",
      "kind": "news",
      "title": "Benzinga: Coherent Expands Pluggable Optical Line System Portfolio, With Full C-Band, High-Power Variable-Gain Amplifier Optical Line System In Compact QSFP Form Factor (2026-09-17)",
      "url": "https://www.benzinga.com/news/26/09/61856234/coherent-expands-pluggable-optical-line-system-portfolio-full-c-band-high-power-variable-gain-amplif",
      "filed": "2026-09-17",
      "chars_total": 158,
      "chars_shown": 158
     },
     {
      "doc_id": "COHR-news-2026-09-08-61673353",
      "kind": "news",
      "title": "Benzinga: $100 Invested In Coherent 15 Years Ago Would Be Worth This Much Today (2026-09-08)",
      "url": "https://www.benzinga.com/news/26/09/61673353/100-invested-coherent-15-years-ago-would-be-worth-much-today",
      "filed": "2026-09-08",
      "chars_total": 286,
      "chars_shown": 286
     }
    ],
    "model_status": "model said evidence: sufficient"
   },
   {
    "symbol": "AMKR",
    "verdict": "explained",
    "thesis": [
     {
      "claim": "Capital expenditures tripled to $688.4 million in the first half of 2026 from $226.1 million a year earlier, reflecting an aggressive buildout that may worry investors.",
      "quote": "Our capital expenditures totaled $688.4 million for the six months ended June 30, 2026 compared to $226.1 million for the six months ended June 30, 2025.",
      "doc_id": "AMKR-10Q-2026-07-28-mdna",
      "ok": true,
      "reason": "",
      "url": "https://www.sec.gov/Archives/edgar/data/1047127/000104712726000046/amkr-20260630.htm",
      "source_kind": "mdna"
     },
     {
      "claim": "The company's own risk disclosures concede that the convertible notes may dilute shareholders or depress the stock price, which could explain the price decline.",
      "quote": "terms of our convertible notes could delay or prevent an otherwise beneficial takeover of us, may dilute the ownership interest of existing stockholders or may otherwise adversely affect the price of our common stock",
      "doc_id": "AMKR-8K-2026-07-27-ex99",
      "ok": true,
      "reason": "",
      "url": "https://www.sec.gov/Archives/edgar/data/1047127/000104712726000043/amkr6302026erex-991.htm",
      "source_kind": "earnings_release"
     },
     {
      "claim": "A news report says the Arizona campus expansion will raise the project's planned investment to about $12 billion, adding to concerns about capital intensity.",
      "quote": "Amkor Technology Reveals Phase 2 Of Arizona Advanced Packaging And Test Campus; The Expansion Increases The Project’s Planned Investment To ~$12B",
      "doc_id": "AMKR-news-2026-09-08-61674271",
      "ok": true,
      "reason": "",
      "url": "https://www.benzinga.com/news/26/09/61674271/amkor-technology-reveals-phase-2-arizona-advanced-packaging-and-test-campus-expansion-increases-proj",
      "source_kind": "news"
     }
    ],
    "bear_case": [
     {
      "claim": "The company is exposed to a cyclical semiconductor industry, and any downturn could hurt revenue and margins.",
      "quote": "dependence on the cyclical and volatile semiconductor industry and vulnerability to industry downturns and declines in global economic and financial conditions",
      "doc_id": "AMKR-8K-2026-07-27-ex99",
      "ok": true,
      "reason": "",
      "url": "https://www.sec.gov/Archives/edgar/data/1047127/000104712726000043/amkr6302026erex-991.htm",
      "source_kind": "earnings_release"
     },
     {
      "claim": "Heavy investments in equipment and facilities may not pay off if customer demand fails to materialize as expected.",
      "quote": "We make substantial investments in equipment and facilities to support the demand of our customers, which may materially and adversely affect our business if the demand of our customers does not develop as we expect or is adversely affected.",
      "doc_id": "AMKR-10Q-2026-07-28-mdna",
      "ok": true,
      "reason": "",
      "url": "https://www.sec.gov/Archives/edgar/data/1047127/000104712726000046/amkr-20260630.htm",
      "source_kind": "mdna"
     },
     {
      "claim": "Concentration in a few key customers or end markets, such as mobile and automotive, increases earnings risk.",
      "quote": "dependence on key customers or concentration of customers in certain end markets, such as mobile communications and automotive",
      "doc_id": "AMKR-8K-2026-07-27-ex99",
      "ok": true,
      "reason": "",
      "url": "https://www.sec.gov/Archives/edgar/data/1047127/000104712726000043/amkr6302026erex-991.htm",
      "source_kind": "earnings_release"
     }
    ],
    "stripped": [
     {
      "claim": "The company's free cash flow turned negative at -$269.9 million in the first half of 2026 despite record revenue, as high capital spending consumed cash.",
      "quote": "Free cash flow $ (269,860) $ 63,080",
      "doc_id": "AMKR-10Q-2026-07-28-mdna",
      "ok": false,
      "reason": "claim states numbers not in its quote: ['2026', '269.9']",
      "url": "https://www.sec.gov/Archives/edgar/data/1047127/000104712726000046/amkr-20260630.htm",
      "source_kind": "mdna"
     }
    ],
    "documents": [
     {
      "doc_id": "AMKR-8K-2026-07-27-ex99",
      "kind": "earnings_release",
      "title": "AMKR 8-K earnings release (Exhibit 99.1), filed 2026-07-27",
      "url": "https://www.sec.gov/Archives/edgar/data/1047127/000104712726000043/amkr6302026erex-991.htm",
      "filed": "2026-07-27",
      "chars_total": 17529,
      "chars_shown": 17529
     },
     {
      "doc_id": "AMKR-10Q-2026-07-28-mdna",
      "kind": "mdna",
      "title": "AMKR 10-Q for period 2026-06-30, MD&A, filed 2026-07-28",
      "url": "https://www.sec.gov/Archives/edgar/data/1047127/000104712726000046/amkr-20260630.htm",
      "filed": "2026-07-28",
      "chars_total": 32600,
      "chars_shown": 32600
     },
     {
      "doc_id": "AMKR-news-2026-09-30-62074203",
      "kind": "news",
      "title": "Benzinga: AI’s Semiconductor Boom Has a Clear Center of Gravity: Taiwan Semiconductor (2026-09-30)",
      "url": "https://www.benzinga.com/markets/tech/26/09/62074203/ais-semiconductor-boom-has-a-clear-center-of-gravity-taiwan-semiconductor",
      "filed": "2026-09-30",
      "chars_total": 201,
      "chars_shown": 201
     },
     {
      "doc_id": "AMKR-news-2026-09-08-61674271",
      "kind": "news",
      "title": "Benzinga: Amkor Technology Reveals Phase 2 Of Arizona Advanced Packaging And Test Campus; The Expansion Increases The Project’s Planned Investment To ~$12B (2026-09-08)",
      "url": "https://www.benzinga.com/news/26/09/61674271/amkor-technology-reveals-phase-2-arizona-advanced-packaging-and-test-campus-expansion-increases-proj",
      "filed": "2026-09-08",
      "chars_total": 145,
      "chars_shown": 145
     }
    ],
    "model_status": "model said evidence: sufficient"
   }
  ],
  "limits": [
   "Prices: Alpaca SIP daily bars, split and dividend adjusted; no intraday data used.",
   "Fundamentals: SEC XBRL companyfacts, US-GAAP filers only. Foreign private issuers (IFRS, 20-F/40-F) and companies without standard tags drop out as 'missing', they are not guessed.",
   "Market cap uses the latest cover-page share count; for multi-class issuers it can understate.",
   "Industry groups are SEC SIC codes, a coarse proxy for a theme (no GICS/BICS in free data).",
   "Short interest: FINRA consolidated short interest (twice monthly, non-commercial use); % is of shares outstanding, not float.",
   "Earnings-call transcripts are licensed content and were not used; explanations rely on the 8-K earnings release, 10-Q/10-K MD&A, and news headlines and summaries (Alpaca / Benzinga), never full articles.",
   "No consensus estimates, revisions, ownership or borrow-cost data: those need a licensed source."
  ]
 },
 {
  "id": "c-oversold-volume",
  "as_of": "2026-10-08",
  "generated_at": "2026-10-08T22:53:56+00:00",
  "llm": {
   "provider": "deepseek",
   "model": "deepseek-v4-pro"
  },
  "data": {
   "as_of": "2026-10-08",
   "last_price_date": "2026-10-08",
   "universe_rule": "tradable US-listed (NYSE/Nasdaq/AMEX/Arca/BATS) operating companies with an SEC CIK and a 10-K/10-Q/20-F/40-F in the last 18 months; close >= $1; 50-day avg dollar volume >= $1,000,000; one listing per CIK",
   "n_companies": 3827,
   "short_interest_settlement": "2026-09-15",
   "benchmark_closes": {
    "IWM": 277.57,
    "QQQ": 747.58,
    "SMH": 607.27,
    "SOXX": 563.28,
    "SPY": 773.93,
    "XLB": 49.27,
    "XLC": 112.07,
    "XLE": 65.24,
    "XLF": 54.23,
    "XLI": 168.4,
    "XLK": 197.78,
    "XLP": 83.42,
    "XLRE": 40.85,
    "XLU": 41.07,
    "XLV": 168.16,
    "XLY": 111.71
   },
   "files": {
    "prices.csv.gz": {
     "sha256": "2fb70ee43a9d30a4174c2353a1eca23798fb267cd09557d74d1af3cc6146d0e1",
     "bytes": 50692072
    },
    "features.csv.gz": {
     "sha256": "cf63f29b2cc08badaf287c158d7e85c689a249e386a9f0f9c0b85029e0510c87",
     "bytes": 3541921
    }
   }
  },
  "observation": "Large caps above $10B being sold hard: RSI(14) below 35 on volume at least 1.5x the 50-day average, yet still in a long-term uptrend with the 50-day above the 200-day, positive free cash flow, short interest under 5% of shares, and no recent analyst downgrades. Most oversold first.",
  "spec": {
   "version": 1,
   "observation": "Large caps above $10B being sold hard: RSI(14) below 35 on volume at least 1.5x the 50-day average, yet still in a long-term uptrend with the 50-day above the 200-day, positive free cash flow, short interest under 5% of shares, and no recent analyst downgrades. Most oversold first.",
   "universe": {
    "market_cap_min": 10000000000
   },
   "conditions": [
    {
     "field": "rsi14",
     "op": "<",
     "value": 35,
     "why": "RSI(14) below 35"
    },
    {
     "field": "volume_ratio_50d",
     "op": ">=",
     "value": 1.5,
     "why": "volume at least 1.5x the 50-day average"
    },
    {
     "field": "sma50_above_sma200",
     "op": "==",
     "value": true,
     "why": "still in a long-term uptrend with the 50-day above the 200-day"
    },
    {
     "field": "fcf_ttm",
     "op": ">",
     "value": 0,
     "why": "positive free cash flow"
    },
    {
     "field": "short_pct_shares_out",
     "op": "<",
     "value": 0.05,
     "why": "short interest under 5% of shares"
    }
   ],
   "rank": [
    {
     "field": "rsi14",
     "direction": "asc",
     "weight": 1
    }
   ],
   "top_n": 5,
   "unmapped": [
    {
     "text": "no recent analyst downgrades",
     "reason": "No field is available for analyst ratings, revisions, or downgrades."
    }
   ],
   "notes": "Large caps are interpreted as market capitalization above $10 billion. The analyst downgrade requirement cannot be measured by the available fields and is listed as unmapped."
  },
  "attempts": 1,
  "funnel": [
   {
    "step": "universe (liquid US common stocks with SEC filings)",
    "kind": "start",
    "n_in": 3827,
    "n_pass": 3827,
    "n_fail": 0,
    "n_missing": 0
   },
   {
    "step": "market_cap >= $10.00B",
    "kind": "universe",
    "n_in": 3827,
    "n_pass": 872,
    "n_fail": 2742,
    "n_missing": 213
   },
   {
    "step": "rsi14 < 35",
    "kind": "condition",
    "n_in": 872,
    "n_pass": 86,
    "n_fail": 786,
    "n_missing": 0
   },
   {
    "step": "volume_ratio_50d >= 1.5",
    "kind": "condition",
    "n_in": 86,
    "n_pass": 29,
    "n_fail": 57,
    "n_missing": 0
   },
   {
    "step": "sma50_above_sma200 == true",
    "kind": "condition",
    "n_in": 29,
    "n_pass": 14,
    "n_fail": 15,
    "n_missing": 0
   },
   {
    "step": "fcf_ttm > 0",
    "kind": "condition",
    "n_in": 14,
    "n_pass": 3,
    "n_fail": 0,
    "n_missing": 11
   },
   {
    "step": "short_pct_shares_out < +5.0%",
    "kind": "condition",
    "n_in": 3,
    "n_pass": 2,
    "n_fail": 1,
    "n_missing": 0
   }
  ],
  "columns": [
   "rank",
   "symbol",
   "name",
   "sector",
   "score",
   "market_cap",
   "rsi14",
   "volume_ratio_50d",
   "sma50_above_sma200",
   "fcf_ttm",
   "short_pct_shares_out"
  ],
  "ranked": [
   {
    "rank": 1,
    "symbol": "BX",
    "name": "Blackstone Inc.",
    "sector": "Financials",
    "score": 1.0,
    "market_cap": 84580437845.52,
    "rsi14": 31.255072641815676,
    "volume_ratio_50d": 1.5327124358641686,
    "sma50_above_sma200": true,
    "fcf_ttm": 5486239000.0,
    "short_pct_shares_out": 0.0261906837825306
   },
   {
    "rank": 2,
    "symbol": "SBUX",
    "name": "STARBUCKS CORP",
    "sector": "Consumer Discretionary",
    "score": 0.5,
    "market_cap": 106259400000.0,
    "rsi14": 34.44323201509681,
    "volume_ratio_50d": 4.243504440806213,
    "sma50_above_sma200": true,
    "fcf_ttm": 3642100000.0,
    "short_pct_shares_out": 0.0349853938596491
   }
  ],
  "sector_breakdown": [
   {
    "sector": "Consumer Discretionary",
    "n": 1
   },
   {
    "sector": "Financials",
    "n": 1
   }
  ],
  "n_ranked": 2,
  "top_n": 5,
  "explanations": [
   {
    "symbol": "BX",
    "verdict": "explained",
    "thesis": [
     {
      "claim": "Blackstone's own earnings release reports an outstanding second quarter with strong earnings growth and nearly $70 billion of inflows, which conflicts with the stock's oversold technical signals.",
      "quote": "Blackstone delivered an outstanding second quarter, highlighted by strong growth in earnings and nearly $70 billion of inflows.",
      "doc_id": "BX-8K-2026-07-23-ex99",
      "ok": true,
      "reason": "",
      "url": "https://www.sec.gov/Archives/edgar/data/1393818/000119312526313250/d153439dex991.htm",
      "source_kind": "earnings_release"
     },
     {
      "claim": "The MD&A states that U.S. capital markets activity expanded considerably, which would normally support fee-related earnings and contradicts the price decline.",
      "quote": "U.S. capital markets activity levels expanded considerably following an active first quarter.",
      "doc_id": "BX-10Q-2026-08-07-mdna",
      "ok": true,
      "reason": "",
      "url": "https://www.sec.gov/Archives/edgar/data/1393818/000119312526340208/d158269d10q.htm",
      "source_kind": "mdna"
     },
     {
      "claim": "A news report says Barclays maintained an Equal-Weight rating and lowered its price target to $124, which may have contributed to selling pressure despite strong fundamentals.",
      "quote": "Barclays Maintains Equal-Weight on Blackstone, Lowers Price Target to $124",
      "doc_id": "BX-news-2026-10-08-62250415",
      "ok": true,
      "reason": "",
      "url": "https://www.benzinga.com/news/26/10/62250415/barclays-maintains-equal-weight-blackstone-lowers-price-target-124",
      "source_kind": "news"
     }
    ],
    "bear_case": [
     {
      "claim": "The company's MD&A notes that the ten-year Treasury yield has risen to 4.72% as of July 31, 2026, which could pressure valuations for rate-sensitive alternative asset managers.",
      "quote": "The ten-year U.S. Treasury yield increased 15 basis points in the second quarter of 2026 to 4.47% and has since risen to 4.72% as of July 31, 2026.",
      "doc_id": "BX-10Q-2026-08-07-mdna",
      "ok": true,
      "reason": "",
      "url": "https://www.sec.gov/Archives/edgar/data/1393818/000119312526340208/d158269d10q.htm",
      "source_kind": "mdna"
     },
     {
      "claim": "A news report says Blue Owl investors sought to pull 39% from a tech credit fund, signaling redemption pressures in private credit that could spill over to investor sentiment on Blackstone's credit business.",
      "quote": "Blue Owl Investors Seek to Pull 39% From $5B Tech Credit Fund",
      "doc_id": "BX-news-2026-10-02-62146487",
      "ok": true,
      "reason": "",
      "url": "https://www.benzinga.com/markets/private-markets/26/10/62146487/blue-owl-investors-seek-to-pull-39-from-5b-tech-credit-fund",
      "source_kind": "news"
     }
    ],
    "stripped": [],
    "documents": [
     {
      "doc_id": "BX-8K-2026-07-23-ex99",
      "kind": "earnings_release",
      "title": "BX 8-K earnings release (Exhibit 99.1), filed 2026-07-23",
      "url": "https://www.sec.gov/Archives/edgar/data/1393818/000119312526313250/d153439dex991.htm",
      "filed": "2026-07-23",
      "chars_total": 110398,
      "chars_shown": 24000
     },
     {
      "doc_id": "BX-10Q-2026-08-07-mdna",
      "kind": "mdna",
      "title": "BX 10-Q for period 2026-06-30, MD&A, filed 2026-08-07",
      "url": "https://www.sec.gov/Archives/edgar/data/1393818/000119312526340208/d158269d10q.htm",
      "filed": "2026-08-07",
      "chars_total": 225787,
      "chars_shown": 40000
     },
     {
      "doc_id": "BX-news-2026-10-08-62250415",
      "kind": "news",
      "title": "Benzinga: Barclays Maintains Equal-Weight on Blackstone, Lowers Price Target to $124 (2026-10-08)",
      "url": "https://www.benzinga.com/news/26/10/62250415/barclays-maintains-equal-weight-blackstone-lowers-price-target-124",
      "filed": "2026-10-08",
      "chars_total": 74,
      "chars_shown": 74
     },
     {
      "doc_id": "BX-news-2026-10-07-62234456",
      "kind": "news",
      "title": "Benzinga: 'Oracle, Broadcom and SpaceX Seek Blockbuster Debt Deals To Pay for AI Chips'- WSJ Exclusive (2026-10-07)",
      "url": "https://www.benzinga.com/news/26/10/62234456/oracle-broadcom-and-spacex-seek-blockbuster-debt-deals-to-pay-for-ai-chips-wsj-exclusive",
      "filed": "2026-10-07",
      "chars_total": 92,
      "chars_shown": 92
     },
     {
      "doc_id": "BX-news-2026-10-06-62203335",
      "kind": "news",
      "title": "Benzinga: 'Waymo Boosts Private Debt Deal to $5 Billion in Push for Growth' - Bloomberg (2026-10-06)",
      "url": "https://www.benzinga.com/news/26/10/62203335/waymo-boosts-private-debt-deal-5-billion-push-growth-bloomberg",
      "filed": "2026-10-06",
      "chars_total": 77,
      "chars_shown": 77
     },
     {
      "doc_id": "BX-news-2026-10-06-62202325",
      "kind": "news",
      "title": "Benzinga: KKR Private Credit Fund Edges Past Redemption Limit (2026-10-06)",
      "url": "https://www.benzinga.com/markets/private-markets/26/10/62202325/kkr-private-credit-fund-edges-past-redemption-limit",
      "filed": "2026-10-06",
      "chars_total": 174,
      "chars_shown": 174
     },
     {
      "doc_id": "BX-news-2026-10-02-62146487",
      "kind": "news",
      "title": "Benzinga: Blue Owl Investors Seek to Pull 39% From $5B Tech Credit Fund (2026-10-02)",
      "url": "https://www.benzinga.com/markets/private-markets/26/10/62146487/blue-owl-investors-seek-to-pull-39-from-5b-tech-credit-fund",
      "filed": "2026-10-02",
      "chars_total": 174,
      "chars_shown": 174
     },
     {
      "doc_id": "BX-news-2026-10-02-62138835",
      "kind": "news",
      "title": "Benzinga: Here’s How Much You Would Have Made Owning Blackstone Stock In The Last 10 Years (2026-10-02)",
      "url": "https://www.benzinga.com/news/26/10/62138835/here-s-how-much-you-would-have-made-owning-blackstone-stock-last-10-years",
      "filed": "2026-10-02",
      "chars_total": 299,
      "chars_shown": 299
     },
     {
      "doc_id": "BX-news-2026-10-02-62138407",
      "kind": "news",
      "title": "Benzinga: Blackstone Pours $1 Billion Into New Defense Tech Firm (2026-10-02)",
      "url": "https://www.benzinga.com/m-a/26/10/62138407/blackstone-pours-1-billion-into-new-defense-tech-firm",
      "filed": "2026-10-02",
      "chars_total": 194,
      "chars_shown": 194
     },
     {
      "doc_id": "BX-news-2026-10-02-62134848",
      "kind": "news",
      "title": "Benzinga: 'KKR, Blackstone Are Among Suitors for Windshield Repairer Cary' - Bloomberg (2026-10-02)",
      "url": "https://www.benzinga.com/news/26/10/62134848/kkr-blackstone-are-among-suitors-windshield-repairer-cary-bloomberg",
      "filed": "2026-10-02",
      "chars_total": 76,
      "chars_shown": 76
     },
     {
      "doc_id": "BX-news-2026-10-02-62131557",
      "kind": "news",
      "title": "Benzinga: Wells Fargo Initiates Coverage On Blackstone with Equal-Weight Rating, Announces Price Target of $122 (2026-10-02)",
      "url": "https://www.benzinga.com/news/26/10/62131557/wells-fargo-initiates-coverage-blackstone-equal-weight-rating-announces-price-target-122",
      "filed": "2026-10-02",
      "chars_total": 101,
      "chars_shown": 101
     },
     {
      "doc_id": "BX-news-2026-10-01-62105131",
      "kind": "news",
      "title": "Benzinga: Blackstone Launches Defense Tech Platform Falcata Through TSC, Applied Systems Engineering Combination (2026-10-01)",
      "url": "https://www.benzinga.com/news/26/10/62105131/blackstone-launches-defense-tech-platform-falcata-through-tsc-applied-systems-engineering-combinatio",
      "filed": "2026-10-01",
      "chars_total": 102,
      "chars_shown": 102
     },
     {
      "doc_id": "BX-news-2026-09-30-62092249",
      "kind": "news",
      "title": "Benzinga: Goldman’s $18B Private Credit Fund Bucks Redemption Wave — Again (2026-09-30)",
      "url": "https://www.benzinga.com/markets/private-markets/26/09/62092249/goldman-private-credit-fund-bucks-redemption-wave-again",
      "filed": "2026-09-30",
      "chars_total": 183,
      "chars_shown": 183
     },
     {
      "doc_id": "BX-news-2026-09-29-62041393",
      "kind": "news",
      "title": "Benzinga: Blackstone To Debut Nordic Logistics Platform Of 200 Warehouses, Offering Investors More Direct Route Into High-Growth Sector (2026-09-29)",
      "url": "https://www.benzinga.com/news/26/09/62041393/blackstone-debut-nordic-logistics-platform-200-warehouses-offering-investors-more-direct-route-high-",
      "filed": "2026-09-29",
      "chars_total": 125,
      "chars_shown": 125
     }
    ],
    "model_status": "model said evidence: sufficient"
   },
   {
    "symbol": "SBUX",
    "verdict": "explained",
    "thesis": [
     {
      "claim": "Starbucks reported a 7.9% increase in global comparable store sales, according to its earnings release.",
      "quote": "Global comparable store sales increased 7.9%, primarily driven by a 4.2% increase in comparable transactions and a 3.5% increase in average ticket",
      "doc_id": "SBUX-8K-2026-07-29-ex99",
      "ok": true,
      "reason": "",
      "url": "https://www.sec.gov/Archives/edgar/data/829224/000082922426000129/sbux-06282026xearningsrele.htm",
      "source_kind": "earnings_release"
     },
     {
      "claim": "Starbucks raised its guidance, including expecting fourth quarter U.S. comparable store sales growth of 6.5% or greater.",
      "quote": "Fourth quarter U.S. comparable store sales growth of 6.5% or greater",
      "doc_id": "SBUX-8K-2026-07-29-ex99",
      "ok": true,
      "reason": "",
      "url": "https://www.sec.gov/Archives/edgar/data/829224/000082922426000129/sbux-06282026xearningsrele.htm",
      "source_kind": "earnings_release"
     },
     {
      "claim": "A news report says Starbucks has explored a takeover of Chipotle in a restaurant megadeal, which may explain the stock's underperformance despite strong fundamentals.",
      "quote": "Starbucks has explored takeover of Chipotle in restaurant megadeal",
      "doc_id": "SBUX-news-2026-10-08-62247653",
      "ok": true,
      "reason": "",
      "url": "https://www.benzinga.com/news/26/10/62247653/starbucks-has-explored-takeover-chipotle-restaurant-megadeal-financial-times",
      "source_kind": "news"
     }
    ],
    "bear_case": [
     {
      "claim": "A news report says Starbucks has looked into buying Chipotle, which could weigh on the stock due to deal risk.",
      "quote": "Starbucks has looked into buying the company",
      "doc_id": "SBUX-news-2026-10-08-62250019",
      "ok": true,
      "reason": "",
      "url": "https://www.benzinga.com/trading-ideas/movers/26/10/62250019/chipotle-stock-jumps-whats-going-on",
      "source_kind": "news"
     },
     {
      "claim": "Starbucks incurred a $282 million increase in restructuring and impairments, reflecting costs from store closures and organizational changes.",
      "quote": "Restructuring and impairments increased $282 million, largely due to costs associated with the impairment of Starbucks Reserve and Roastery store locations, and partner severance costs.",
      "doc_id": "SBUX-10Q-2026-07-29-mdna",
      "ok": true,
      "reason": "",
      "url": "https://www.sec.gov/Archives/edgar/data/829224/000082922426000130/sbux-20260628.htm",
      "source_kind": "mdna"
     },
     {
      "claim": "A news report says UBS maintained a Neutral rating and lowered its price target to $105, signaling caution on Starbucks shares.",
      "quote": "UBS Maintains Neutral on Starbucks, Lowers Price Target to $105",
      "doc_id": "SBUX-news-2026-10-08-62257066",
      "ok": true,
      "reason": "",
      "url": "https://www.benzinga.com/news/26/10/62257066/ubs-maintains-neutral-starbucks-lowers-price-target-105",
      "source_kind": "news"
     }
    ],
    "stripped": [],
    "documents": [
     {
      "doc_id": "SBUX-8K-2026-07-29-ex99",
      "kind": "earnings_release",
      "title": "SBUX 8-K earnings release (Exhibit 99.1), filed 2026-07-29",
      "url": "https://www.sec.gov/Archives/edgar/data/829224/000082922426000129/sbux-06282026xearningsrele.htm",
      "filed": "2026-07-29",
      "chars_total": 43442,
      "chars_shown": 24000
     },
     {
      "doc_id": "SBUX-10Q-2026-07-29-mdna",
      "kind": "mdna",
      "title": "SBUX 10-Q for period 2026-06-28, MD&A, filed 2026-07-29",
      "url": "https://www.sec.gov/Archives/edgar/data/829224/000082922426000130/sbux-20260628.htm",
      "filed": "2026-07-29",
      "chars_total": 61551,
      "chars_shown": 40000
     },
     {
      "doc_id": "SBUX-news-2026-10-08-62259027",
      "kind": "news",
      "title": "Benzinga: Why Is Jersey Mike's Subs Stock Gaining Thursday? (2026-10-08)",
      "url": "https://www.benzinga.com/trading-ideas/movers/26/10/62259027/why-is-jersey-mikes-subs-stock-gaining-thursday",
      "filed": "2026-10-08",
      "chars_total": 172,
      "chars_shown": 172
     },
     {
      "doc_id": "SBUX-news-2026-10-08-62257066",
      "kind": "news",
      "title": "Benzinga: UBS Maintains Neutral on Starbucks, Lowers Price Target to $105 (2026-10-08)",
      "url": "https://www.benzinga.com/news/26/10/62257066/ubs-maintains-neutral-starbucks-lowers-price-target-105",
      "filed": "2026-10-08",
      "chars_total": 63,
      "chars_shown": 63
     },
     {
      "doc_id": "SBUX-news-2026-10-08-62251550",
      "kind": "news",
      "title": "Benzinga: QUICK SPARK: Chipotle Stock Eyes Best Day Since July on Starbucks' Takeover Interest (2026-10-08)",
      "url": "https://www.benzinga.com/m-a/26/10/62251550/chipotle-stock-best-day-starbucks-takeover-interest",
      "filed": "2026-10-08",
      "chars_total": 239,
      "chars_shown": 239
     },
     {
      "doc_id": "SBUX-news-2026-10-08-62250019",
      "kind": "news",
      "title": "Benzinga: Chipotle Stock Jumps: What's Going On? (2026-10-08)",
      "url": "https://www.benzinga.com/trading-ideas/movers/26/10/62250019/chipotle-stock-jumps-whats-going-on",
      "filed": "2026-10-08",
      "chars_total": 161,
      "chars_shown": 161
     },
     {
      "doc_id": "SBUX-news-2026-10-08-62247653",
      "kind": "news",
      "title": "Benzinga: 'Starbucks has explored takeover of Chipotle in restaurant megadeal'- Financial Times (2026-10-08)",
      "url": "https://www.benzinga.com/news/26/10/62247653/starbucks-has-explored-takeover-chipotle-restaurant-megadeal-financial-times",
      "filed": "2026-10-08",
      "chars_total": 85,
      "chars_shown": 85
     },
     {
      "doc_id": "SBUX-news-2026-10-07-62232953",
      "kind": "news",
      "title": "Benzinga: Starbucks Raises Quarterly Dividend From $0.62 To $0.63/Share (2026-10-07)",
      "url": "https://www.benzinga.com/quote/SBUX",
      "filed": "2026-10-07",
      "chars_total": 61,
      "chars_shown": 61
     },
     {
      "doc_id": "SBUX-news-2026-10-06-62197465",
      "kind": "news",
      "title": "Benzinga: 'A Starbucks-Chipotle Tie-up Might Be Crazy Enough To Work; People Close To The Company Tell Semafor That Chipotle Hasn’t Received A Takeover Bid'- Semafor (2026-10-06)",
      "url": "https://www.benzinga.com/news/26/10/62197465/starbucks-chipotle-tie-might-be-crazy-enough-work-people-close-company-tell-semafor-chipotle-hasn-t-",
      "filed": "2026-10-06",
      "chars_total": 155,
      "chars_shown": 155
     },
     {
      "doc_id": "SBUX-news-2026-10-05-62172156",
      "kind": "news",
      "title": "Benzinga: 'Starbucks sued over 'sugar-free' claims for protein beverages'- Reuters (2026-10-05)",
      "url": "https://www.benzinga.com/news/26/10/62172156/starbucks-sued-over-sugar-free-claims-protein-beverages-reuters",
      "filed": "2026-10-05",
      "chars_total": 72,
      "chars_shown": 72
     },
     {
      "doc_id": "SBUX-news-2026-09-29-62053181",
      "kind": "news",
      "title": "Benzinga: JP Morgan Maintains Overweight on Starbucks, Lowers Price Target to $105 (2026-09-29)",
      "url": "https://www.benzinga.com/news/26/09/62053181/jp-morgan-maintains-overweight-starbucks-lowers-price-target-105",
      "filed": "2026-09-29",
      "chars_total": 72,
      "chars_shown": 72
     },
     {
      "doc_id": "SBUX-news-2026-09-25-61997944",
      "kind": "news",
      "title": "Benzinga: Starbucks to Close Select North America Coffeehouses, Cuts Store Outlook (2026-09-25)",
      "url": "https://www.benzinga.com/markets/large-cap/26/09/61997944/starbucks-to-close-select-north-america-coffeehouses-cuts-store-outlook",
      "filed": "2026-09-25",
      "chars_total": 210,
      "chars_shown": 210
     },
     {
      "doc_id": "SBUX-news-2026-09-24-61966820",
      "kind": "news",
      "title": "Benzinga: Starbucks Board Approves Further Actions Under 'Back To Starbucks' Strategy; Will Close ~250, Or ~1% Of, Its North America Coffeehouses; Expects $300M Of Restructuring Charges, Including $200M In Cash And $100M Non-Cash Charges For Coffeehouse Asset Disposal And Impairments; Expects FY26 Net New Global Coffeehouse Openings Of ~440; Majority Of Starbucks Coffeehouse Closures Expected By End Of FY26 (2026-09-24)",
      "url": "https://www.benzinga.com/quote/SBUX",
      "filed": "2026-09-24",
      "chars_total": 400,
      "chars_shown": 400
     },
     {
      "doc_id": "SBUX-news-2026-09-16-61809341",
      "kind": "news",
      "title": "Benzinga: Seaport Global Initiates Coverage On Starbucks with Neutral Rating (2026-09-16)",
      "url": "https://www.benzinga.com/news/26/09/61809341/seaport-global-initiates-coverage-starbucks-neutral-rating",
      "filed": "2026-09-16",
      "chars_total": 66,
      "chars_shown": 66
     }
    ],
    "model_status": "model said evidence: sufficient"
   }
  ],
  "limits": [
   "Prices: Alpaca SIP daily bars, split and dividend adjusted; no intraday data used.",
   "Fundamentals: SEC XBRL companyfacts, US-GAAP filers only. Foreign private issuers (IFRS, 20-F/40-F) and companies without standard tags drop out as 'missing', they are not guessed.",
   "Market cap uses the latest cover-page share count; for multi-class issuers it can understate.",
   "Industry groups are SEC SIC codes, a coarse proxy for a theme (no GICS/BICS in free data).",
   "Short interest: FINRA consolidated short interest (twice monthly, non-commercial use); % is of shares outstanding, not float.",
   "Earnings-call transcripts are licensed content and were not used; explanations rely on the 8-K earnings release, 10-Q/10-K MD&A, and news headlines and summaries (Alpaca / Benzinga), never full articles.",
   "No consensus estimates, revisions, ownership or borrow-cost data: those need a licensed source."
  ]
 }
];
