# Screen: Oversold large caps on heavy volume

As of **2026-10-08** (last price date 2026-10-08). Universe: tradable US-listed (NYSE/Nasdaq/AMEX/Arca/BATS) operating companies with an SEC CIK and a 10-K/10-Q/20-F/40-F in the last 18 months; close >= $1; 50-day avg dollar volume >= $1,000,000; one listing per CIK. Model: deepseek / deepseek-v4-pro (translation and prose only; every filter, rank and number below is computed by code).

## 1. Screen spec (proposed by the model, validated by code)

```json
{
  "version": 1,
  "observation": "Oversold large caps on heavy volume",
  "universe": {
    "market_cap_min": 10000000000
  },
  "conditions": [
    {
      "field": "rsi14",
      "op": "<",
      "value": 30,
      "why": "oversold"
    },
    {
      "field": "volume_ratio_50d",
      "op": ">",
      "value": 2.0,
      "why": "heavy volume"
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
  "unmapped": [],
  "notes": "Interpreted oversold as RSI(14) below 30, heavy volume as volume at least twice the 50-day average, and large cap as market cap above $10B. Thresholds are defaults since exact levels were not specified."
}
```

## 2. Funnel

| step | in | pass | fail | missing data |
|---|---:|---:|---:|---:|
| universe (liquid US common stocks with SEC filings) | 3827 | 3827 | 0 | 0 |
| market_cap >= $10.00B | 3827 | 872 | 2742 | 213 |
| rsi14 < 30 | 872 | 35 | 837 | 0 |
| volume_ratio_50d > 2 | 35 | 7 | 28 | 0 |

## 3. Ranked survivors (7)

| rank | symbol | name | score | market_cap | rsi14 | volume_ratio_50d |
|---|---|---|---|---|---|---|
| 1 | EMA | EMERA INC | 1.000 | $13.7B | 22.80 | 4.42 |
| 2 | ARGX | ARGENX SE | 0.857 | $50.7B | 24.05 | 8.86 |
| 3 | NLY | ANNALY CAPITAL MANAGEMENT INC | 0.714 | $13.8B | 24.46 | 2.25 |
| 4 | DOC | HEALTHPEAK PROPERTIES, INC. | 0.571 | $12.8B | 24.46 | 2.11 |
| 5 | HRL | HORMEL FOODS CORP /DE/ | 0.429 | $10.7B | 27.07 | 2.04 |
| 6 | PUK | PRUDENTIAL PLC | 0.286 | $60.9B | 27.23 | 3.22 |
| 7 | HSBC | HSBC HOLDINGS PLC | 0.143 | $1,590.6B | 28.31 | 2.56 |

## 4. Why the dislocation might exist (top 5)

Every quote below was checked by code to appear verbatim in the linked SEC document. Claims whose quotes failed the check were removed and are listed.

### EMA: not enough evidence


*no earnings documents found on EDGAR for this as-of date*

### ARGX: explained

- source: [Benzinga: Argenx Halts Phase 3 Study in Rare Disease Following Futility Analysis (2026-10-08)](https://www.benzinga.com/trading-ideas/movers/26/10/62243091/argenx-halts-phase-3-study-in-rare-disease-following-futility-analysis)
- source: [Benzinga: Argenx Will Discontinue Phase 3 UNITY Study Of Efgartigimod SC In Sjögren's Disease After IDMC Recommends Stopping For Futility At Interim Analysis; No New Safety Signals Identified (2026-10-08)](https://www.benzinga.com/quote/ARGX)
- source: [Benzinga: Argenx's FB102 Meets Primary Endpoint In Phase 2 Celiac Disease Study Versus Placebo With No New Safety Signals; Company Will Advance First-In-Class CD122 Inhibitor Into Phase 3 Development (2026-10-08)](https://www.benzinga.com/news/26/10/62236814/argenx-s-fb102-meets-primary-endpoint-phase-2-celiac-disease-study-versus-placebo-no-new-safety-sign)
- source: [Benzinga: Halozyme Therapeutic Expands Collaboration, License Deal With Argenx Over Development, Commercialization Of ENHANCE With Two Additional Targets (2026-10-06)](https://www.benzinga.com/news/26/10/62204613/halozyme-therapeutic-expands-collaboration-license-deal-argenx-over-development-commercialization-en)
- source: [Benzinga: Argenx Says VYVGART Showed Continued Improvement In Ocular Myasthenia Gravis, Sustained One-Year Efficacy In Antibody-Negative Generalized MG (2026-09-29)](https://www.benzinga.com/quote/ARGX)
- source: [Benzinga: Here's How Much $100 Invested In argenx 5 Years Ago Would Be Worth Today (2026-09-24)](https://www.benzinga.com/news/26/09/61976850/here-s-how-much-100-invested-argenx-5-years-ago-would-be-worth-today)
- source: [Benzinga: Wedbush Reiterates Outperform on argenx, Maintains $1150 Price Target (2026-09-08)](https://www.benzinga.com/news/26/09/61657831/wedbush-reiterates-outperform-argenx-maintains-1150-price-target)

**Thesis**
- A news report says argenx will discontinue its Phase 3 UNITY study of efgartigimod SC in Sjögren's disease after an independent data monitoring committee recommended stopping for futility.  
  > "Argenx Will Discontinue Phase 3 UNITY Study Of Efgartigimod SC In Sjögren's Disease After IDMC Recommends Stopping For Futility At Interim Analysis; No New Safety Signals Identified" ([ARGX-news-2026-10-08-62236825](https://www.benzinga.com/quote/ARGX))
- A news report says argenx's FB102 met its primary endpoint in a Phase 2 celiac disease study and the company will advance the first-in-class CD122 inhibitor into Phase 3 development.  
  > "Argenx's FB102 Meets Primary Endpoint In Phase 2 Celiac Disease Study Versus Placebo With No New Safety Signals; Company Will Advance First-In-Class CD122 Inhibitor Into Phase 3 Development" ([ARGX-news-2026-10-08-62236814](https://www.benzinga.com/news/26/10/62236814/argenx-s-fb102-meets-primary-endpoint-phase-2-celiac-disease-study-versus-placebo-no-new-safety-sign))
- A news report says Wedbush reiterated an Outperform rating and a $1150 price target on argenx.  
  > "Wedbush Reiterates Outperform on argenx, Maintains $1150 Price Target" ([ARGX-news-2026-09-08-61657831](https://www.benzinga.com/news/26/09/61657831/wedbush-reiterates-outperform-argenx-maintains-1150-price-target))
- A news report says Halozyme Therapeutic expanded its collaboration and license deal with argenx over development and commercialization of ENHANCE with two additional targets.  
  > "Halozyme Therapeutic Expands Collaboration, License Deal With Argenx Over Development, Commercialization Of ENHANCE With Two Additional Targets" ([ARGX-news-2026-10-06-62204613](https://www.benzinga.com/news/26/10/62204613/halozyme-therapeutic-expands-collaboration-license-deal-argenx-over-development-commercialization-en))

**Bear case**
- A news report says the Phase 3 UNITY study was stopped for futility at an interim analysis, signaling that efgartigimod SC failed to show sufficient efficacy in Sjögren's disease.  
  > "Argenx Will Discontinue Phase 3 UNITY Study Of Efgartigimod SC In Sjögren's Disease After IDMC Recommends Stopping For Futility At Interim Analysis; No New Safety Signals Identified" ([ARGX-news-2026-10-08-62236825](https://www.benzinga.com/quote/ARGX))
- A news report says the FB102 celiac disease program is still only advancing into Phase 3 development, so its clinical and commercial success is not yet established.  
  > "Argenx's FB102 Meets Primary Endpoint In Phase 2 Celiac Disease Study Versus Placebo With No New Safety Signals; Company Will Advance First-In-Class CD122 Inhibitor Into Phase 3 Development" ([ARGX-news-2026-10-08-62236814](https://www.benzinga.com/news/26/10/62236814/argenx-s-fb102-meets-primary-endpoint-phase-2-celiac-disease-study-versus-placebo-no-new-safety-sign))

*model said evidence: sufficient*

### NLY: explained

- source: [NLY 8-K earnings release (Exhibit 99.1), filed 2026-07-21](https://www.sec.gov/Archives/edgar/data/1043219/000104321926000052/a2026q2nlyex991.htm)
- source: [NLY 10-Q for period 2026-06-30, MD&A, filed 2026-07-29](https://www.sec.gov/Archives/edgar/data/1043219/000104321926000058/nly-20260630.htm)
- source: [Benzinga: BTIG Maintains Buy on Annaly Capital Management, Lowers Price Target to $21 (2026-10-07)](https://www.benzinga.com/news/26/10/62210625/btig-maintains-buy-annaly-capital-management-lowers-price-target-21)

**Thesis**
- The company reported GAAP net income of $1.06 per average common share for the quarter, reflecting strong profitability despite the stock's weakness.  
  > "GAAP net income of $1.06 per average common share for the quarter" ([NLY-8K-2026-07-21-ex99](https://www.sec.gov/Archives/edgar/data/1043219/000104321926000052/a2026q2nlyex991.htm))
- Book value per common share of $20.15 suggests the stock is trading at a discount to reported book value.  
  > "Book value per common share of $20.15" ([NLY-8K-2026-07-21-ex99](https://www.sec.gov/Archives/edgar/data/1043219/000104321926000052/a2026q2nlyex991.htm))
- Management increased the quarterly common stock dividend to $0.75 per share, citing durable earnings power.  
  > "supported our decision to increase the quarterly common stock dividend to $0.75 per share, reflecting the durable earnings power of our portfolio" ([NLY-8K-2026-07-21-ex99](https://www.sec.gov/Archives/edgar/data/1043219/000104321926000052/a2026q2nlyex991.htm))

**Bear case**
- The Federal Reserve discussed potential interest rate hikes as rates rose over the quarter, creating headwinds for mortgage REITs.  
  > "Federal Reserve (the “Fed”) officials discussed the potential for interest rate hikes, and interest rates rose over the quarter, led by the front end of the yield curve, as market pricing shifted from an expectation of roughly two 25 basis point (“bps”) cuts this year to the possibility of at least one hike." ([NLY-10Q-2026-07-29-mdna](https://www.sec.gov/Archives/edgar/data/1043219/000104321926000058/nly-20260630.htm))
- GAAP leverage increased to 7.4x, amplifying exposure to interest rate movements.  
  > "GAAP leverage of 7.4x, up from 7.3x in the prior quarter; economic leverage of 5.6x, down from 5.7x in the prior quarter" ([NLY-8K-2026-07-21-ex99](https://www.sec.gov/Archives/edgar/data/1043219/000104321926000052/a2026q2nlyex991.htm))

*Stripped by the citation check (1):* "Inflation remained elevated from energy shocks, tariffs, and AI-related demand, " (quote not found verbatim in the cited document)

*model said evidence: sufficient*

### DOC: explained

- source: [DOC 8-K earnings release (Exhibit 99.1), filed 2026-08-04](https://www.sec.gov/Archives/edgar/data/765880/000162828026052608/ex99106302026.htm)
- source: [DOC 10-Q for period 2026-06-30, MD&A, filed 2026-08-05](https://www.sec.gov/Archives/edgar/data/765880/000162828026053373/peak-20260630.htm)
- source: [Benzinga: Evercore ISI Group Maintains In-Line on Healthpeak Properties, Lowers Price Target to $22 (2026-09-21)](https://www.benzinga.com/news/26/09/61898566/evercore-isi-group-maintains-line-healthpeak-properties-lowers-price-target-22)
- source: [Benzinga: Jefferies Assumes Healthpeak Properties at Hold, Lowers Price Target of $21 (2026-09-15)](https://www.benzinga.com/news/26/09/61793714/jefferies-assumes-healthpeak-properties-hold-lowers-price-target-21)

**Thesis**
- The company highlights that elevated interest rates could continue to adversely affect borrowing costs and real estate values, which may pressure the stock.  
  > "Elevated interest rates have and could continue to adversely impact our borrowing costs, the fair value of our fixed rate instruments, transaction volume, and real estate values generally, including our real estate." ([DOC-10Q-2026-08-05-mdna](https://www.sec.gov/Archives/edgar/data/765880/000162828026053373/peak-20260630.htm))
- The company identifies uncertainty faced by its lab tenants from regulation and funding requirements as a risk, which could weigh on lab performance.  
  > "changes within the life science industry, and significant regulation, funding requirements, and uncertainty faced by our lab tenants;" ([DOC-10Q-2026-08-05-mdna](https://www.sec.gov/Archives/edgar/data/765880/000162828026053373/peak-20260630.htm))
- A news report says Evercore ISI Group maintained an In-Line rating on Healthpeak Properties but lowered its price target to $22, reflecting analyst caution.  
  > "Evercore ISI Group Maintains In-Line on Healthpeak Properties, Lowers Price Target to $22" ([DOC-news-2026-09-21-61898566](https://www.benzinga.com/news/26/09/61898566/evercore-isi-group-maintains-line-healthpeak-properties-lowers-price-target-22))

**Bear case**
- The lab segment's occupancy was 78.5%, well below the outpatient medical segment's 90.7%, indicating weaker lab demand.  
  > "Total occupancy increased sequentially by +20 basis points ("bps") in Outpatient Medical to 90.7% and by +80 bps in Lab to 78.5%" ([DOC-8K-2026-08-04-ex99](https://www.sec.gov/Archives/edgar/data/765880/000162828026052608/ex99106302026.htm))
- Increased costs for tenant improvements and construction plus higher capital costs could reduce expected yields on development projects.  
  > "We have also been affected by increased costs relating to tenant improvements and construction, which, together with higher costs of capital and tariff actions (or potential tariff actions), have adversely affected, and in the future may adversely affect, construction starts and the expected yields on our capital projects, including our developments and redevelopments." ([DOC-10Q-2026-08-05-mdna](https://www.sec.gov/Archives/edgar/data/765880/000162828026053373/peak-20260630.htm))
- If tenants face liquidity constraints, they may be unable to pay rent, which could reduce occupancy.  
  > "To the extent our tenants and/or operators have experienced, or will experience, increased costs, liquidity constraints, and financing difficulties due to the foregoing macroeconomic and market conditions, they may be unable or unwilling to make payments or perform their obligations when due, and occupancy of our properties could be adversely affected." ([DOC-10Q-2026-08-05-mdna](https://www.sec.gov/Archives/edgar/data/765880/000162828026053373/peak-20260630.htm))

*Stripped by the citation check (1):* "The company's lab segment reported a same-store Adjusted NOI decline of 3.2 %, i" (quote is 5 words (must be 6-80))

*model said evidence: sufficient*

### HRL: explained

- source: [HRL 8-K earnings release (Exhibit 99.1), filed 2026-08-27](https://www.sec.gov/Archives/edgar/data/48465/000004846526000053/hormelearningsreleaseq32026.htm)
- source: [HRL 10-Q for period 2026-07-26, MD&A, filed 2026-08-27](https://www.sec.gov/Archives/edgar/data/48465/000004846526000055/hrl-20260726.htm)
- source: [Benzinga: BNP Paribas Maintains Neutral on Hormel Foods, Lowers Price Target to $23 (2026-10-07)](https://www.benzinga.com/news/26/10/62228810/bnp-paribas-maintains-neutral-hormel-foods-lowers-price-target-23)
- source: [Benzinga: Hormel Strikes $1.06 Billion Deal to Expand Its Chicken Business (2026-09-30)](https://www.benzinga.com/m-a/26/09/62088644/hormel-strikes-1-06-billion-deal-to-expand-its-chicken-business)
- source: [Benzinga: Hormel Foods To Acquire Brakebush Brothers For ~$1.055B (2026-09-30)](https://www.benzinga.com/m/26/09/62073125/hormel-foods-acquire-brakebush-brothers-1-055b)
- source: [Benzinga: Top 3 Defensive Stocks That Could Blast Off In Q3 (2026-09-16)](https://www.benzinga.com/trading-ideas/long-ideas/26/09/61809782/top-3-defensive-stocks-that-could-blast-off-in-q3)

**Thesis**
- The decline in GAAP earnings was driven by discrete one-time charges rather than the underlying operating trend.  
  > "Earnings before income taxes decreased 56 percent for the third quarter of fiscal 2026, primarily due to a $56 million loss related to the Brazil divestiture, a $48 million non-cash impairment charge, and a litigation settlement of $38 million." ([HRL-10Q-2026-08-27-mdna](https://www.sec.gov/Archives/edgar/data/48465/000004846526000055/hrl-20260726.htm))
- Adjusted diluted earnings per share rose 6% year over year despite the GAAP decline, indicating core profitability improved.  
  > "Adjusted diluted earnings per share for the third quarter of fiscal 2026 was $0.37, up 6 percent compared to the same period last year." ([HRL-10Q-2026-08-27-mdna](https://www.sec.gov/Archives/edgar/data/48465/000004846526000055/hrl-20260726.htm))
- The Foodservice segment delivered its 12th consecutive quarter of organic net sales growth, showing demand strength in a key segment.  
  > "The third quarter of fiscal 2026 marked the 12th consecutive quarter of organic net sales1 growth for the Foodservice segment." ([HRL-8K-2026-08-27-ex99](https://www.sec.gov/Archives/edgar/data/48465/000004846526000053/hormelearningsreleaseq32026.htm))
- A news report says Hormel Foods is oversold with RSI near 30 and offers potential value, consistent with the mechanical screen.  
  > "Consumer staples stocks Tootsie Roll, Lamb Weston and Hormel Foods are oversold, with RSI readings near or below 30, offering potential value." ([HRL-news-2026-09-16-61809782](https://www.benzinga.com/trading-ideas/long-ideas/26/09/61809782/top-3-defensive-stocks-that-could-blast-off-in-q3))

**Bear case**
- Volume decreased for all three segments in the third quarter, primarily due to the commodity turkey portfolio.  
  > "For the third quarter of fiscal 2026, volume decreased for all three segments, primarily driven by the commodity turkey portfolio." ([HRL-10Q-2026-08-27-mdna](https://www.sec.gov/Archives/edgar/data/48465/000004846526000055/hrl-20260726.htm))
- The company warns that continued pressure from the external environment could have an adverse impact on results of operations.  
  > "However, continued pressure from the external environment, at a level greater than expected, could have an adverse impact on results of operations." ([HRL-10Q-2026-08-27-mdna](https://www.sec.gov/Archives/edgar/data/48465/000004846526000055/hrl-20260726.htm))
- GAAP operating margin was 3.7% compared to 7.9% a year earlier.  
  > "Operating margin and adjusted operating margin1 were 3.7% and 9.0%, respectively, compared to 7.9% and 8.4%, respectively, in the prior year." ([HRL-8K-2026-08-27-ex99](https://www.sec.gov/Archives/edgar/data/48465/000004846526000053/hormelearningsreleaseq32026.htm))

*model said evidence: sufficient*

## Data limits

- Prices: Alpaca SIP daily bars, split and dividend adjusted; no intraday data used.
- Fundamentals: SEC XBRL companyfacts, US-GAAP filers only. Foreign private issuers (IFRS, 20-F/40-F) and companies without standard tags drop out as 'missing', they are not guessed.
- Market cap uses the latest cover-page share count; for multi-class issuers it can understate.
- Industry groups are SEC SIC codes, a coarse proxy for a theme (no GICS/BICS in free data).
- Short interest: FINRA consolidated short interest (twice monthly, non-commercial use); % is of shares outstanding, not float.
- Earnings-call transcripts are licensed content and were not used; explanations rely on the 8-K earnings release, 10-Q/10-K MD&A, and news headlines and summaries (Alpaca / Benzinga), never full articles.
- No consensus estimates, revisions, ownership or borrow-cost data: those need a licensed source.
