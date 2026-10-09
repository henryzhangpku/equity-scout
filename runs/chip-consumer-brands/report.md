# Screen: Quality consumer brands down 30% from their highs that still generate strong free cash flow

As of **2026-10-08** (last price date 2026-10-08). Universe: tradable US-listed (NYSE/Nasdaq/AMEX/Arca/BATS) operating companies with an SEC CIK and a 10-K/10-Q/20-F/40-F in the last 18 months; close >= $1; 50-day avg dollar volume >= $1,000,000; one listing per CIK. Model: deepseek / deepseek-v4-pro (translation and prose only; every filter, rank and number below is computed by code).

## 1. Screen spec (proposed by the model, validated by code)

```json
{
  "version": 1,
  "observation": "Quality consumer brands down 30% from their highs that still generate strong free cash flow",
  "universe": {
    "industry_groups": [
      "Food & Beverage",
      "Household & Personal Products",
      "Apparel & Luxury",
      "Restaurants",
      "Tobacco"
    ]
  },
  "conditions": [
    {
      "field": "drawdown_52w",
      "op": "<=",
      "value": -0.3,
      "why": "down 30% from their highs"
    },
    {
      "field": "fcf_margin",
      "op": ">",
      "value": 0.1,
      "why": "still generate strong free cash flow"
    }
  ],
  "rank": [
    {
      "field": "fcf_margin",
      "direction": "desc",
      "weight": 1
    }
  ],
  "top_n": 5,
  "unmapped": [
    {
      "text": "Quality consumer brands",
      "reason": "Brand strength/quality is not directly measurable; approximated by consumer industry groups and a strong free cash flow margin."
    }
  ],
  "notes": "Mapped 'consumer brands' to the listed consumer industry groups (Food & Beverage, Household & Personal Products, Apparel & Luxury, Restaurants, Tobacco). 'Down 30% from highs' is enforced as drawdown_52w <= -0.30; 'strong free cash flow' is interpreted as TTM FCF margin > 10% and ranked by that margin."
}
```

**Not screened: outside the schema**

- "Quality consumer brands": Brand strength/quality is not directly measurable; approximated by consumer industry groups and a strong free cash flow margin.

## 2. Funnel

| step | in | pass | fail | missing data |
|---|---:|---:|---:|---:|
| universe (liquid US common stocks with SEC filings) | 3827 | 3827 | 0 | 0 |
| industry group in ['Food & Beverage', 'Household & Personal Products', 'Apparel & Luxury', 'Restaurants', 'Tobacco'] | 3827 | 177 | 3609 | 41 |
| drawdown_52w <= -30.0% | 177 | 64 | 110 | 3 |
| fcf_margin > +10.0% | 64 | 9 | 33 | 22 |

## 3. Ranked survivors (9)

| rank | symbol | name | score | market_cap | drawdown_52w | fcf_margin |
|---|---|---|---|---|---|---|
| 1 | DECK | DECKERS OUTDOOR CORP | 1.000 | $11.3B | -31.7% | +20.2% |
| 2 | HSY | HERSHEY CO | 0.889 | $33.0B | -30.1% | +18.3% |
| 3 | WING | Wingstop Inc. | 0.778 | $3.2B | -58.1% | +17.8% |
| 4 | COCO | Vita Coco Company, Inc. | 0.667 | $3.2B | -33.4% | +17.6% |
| 5 | CELH | Celsius Holdings, Inc. | 0.556 | $6.9B | -57.8% | +15.2% |
| 6 | LULU | lululemon athletica inc. | 0.444 | $9.8B | -57.1% | +12.2% |
| 7 | SAM | BOSTON BEER CO INC | 0.333 | $1.8B | -34.2% | +10.7% |
| 8 | MZTI | MARZETTI CO | 0.222 | $2.8B | -39.8% | +10.7% |
| 9 | MGPI | MGP INGREDIENTS INC | 0.111 | $294M | -46.8% | +10.1% |

## 4. Why the dislocation might exist (top 5)

Every quote below was checked by code to appear verbatim in the linked SEC document. Claims whose quotes failed the check were removed and are listed.

### DECK: explained

- source: [DECK 8-K earnings release (Exhibit 99.1), filed 2026-07-23](https://www.sec.gov/Archives/edgar/data/910521/000091052126000015/deckex991pressrelease-6302.htm)
- source: [DECK 10-Q for period 2026-06-30, MD&A, filed 2026-07-30](https://www.sec.gov/Archives/edgar/data/910521/000091052126000022/deck-20260630.htm)
- source: [Benzinga: This Robinhood Analyst Begins Coverage On A Bullish Note; Here Are Top 5 Initiations For Wednesday (2026-09-09)](https://www.benzinga.com/analyst-stock-ratings/initiation/26/09/61682144/this-robinhood-analyst-begins-coverage-on-a-bullish-note-here-are-top-5-initiations-for-wednesday)
- source: [Benzinga: BMO Capital Initiates Coverage On Deckers Outdoor with Underperform Rating, Announces Price Target of $70 (2026-09-09)](https://www.benzinga.com/news/26/09/61679953/bmo-capital-initiates-coverage-deckers-outdoor-underperform-rating-announces-price-target-70)

**Thesis**
- The company's reported operating margin contracted by 190 basis points to 15.2% in the first quarter.  
  > "Income from operations as a percentage of net sales (operating margin) decreased 190 basis points to 15.2%." ([DECK-10Q-2026-07-30-mdna](https://www.sec.gov/Archives/edgar/data/910521/000091052126000022/deck-20260630.htm))
- The company said the decrease in net income was due to lower operating margins on higher net sales.  
  > "The decrease in net income, compared to the prior period, was due to lower operating margins on higher net sales." ([DECK-10Q-2026-07-30-mdna](https://www.sec.gov/Archives/edgar/data/910521/000091052126000022/deck-20260630.htm))
- A news report says BMO Capital initiated coverage on Deckers with an Underperform rating and a $70 price target.  
  > "BMO Capital Initiates Coverage On Deckers Outdoor with Underperform Rating, Announces Price Target of $70" ([DECK-news-2026-09-09-61679953](https://www.benzinga.com/news/26/09/61679953/bmo-capital-initiates-coverage-deckers-outdoor-underperform-rating-announces-price-target-70))

**Bear case**
- Advertising, marketing, and promotion expenses rose approximately $10,300, driven by higher promotional marketing spend.  
  > "Increased advertising, marketing, and promotion expenses of approximately $10,300, primarily due to higher promotional marketing expenses for the HOKA brand and UGG brand to drive global brand awareness and market share gains" ([DECK-10Q-2026-07-30-mdna](https://www.sec.gov/Archives/edgar/data/910521/000091052126000022/deck-20260630.htm))

*Stripped by the citation check (1):* "Management does not expect mitigation strategies to fully offset the incremental" (claim states numbers not in its quote: ['2027'])

*model said evidence: sufficient*

### HSY: explained

- source: [HSY 8-K earnings release (Exhibit 99.1), filed 2026-07-30](https://www.sec.gov/Archives/edgar/data/47111/000162828026050769/exhibit991_2026xq2.htm)
- source: [HSY 10-Q for period 2026-06-28, MD&A, filed 2026-07-30](https://www.sec.gov/Archives/edgar/data/47111/000162828026050900/hsy-20260628.htm)
- source: [Benzinga: Wells Fargo Maintains Equal-Weight on Hershey, Lowers Price Target to $170 (2026-10-05)](https://www.benzinga.com/news/26/10/62163018/wells-fargo-maintains-equal-weight-hershey-lowers-price-target-170)
- source: [Benzinga: Top 3 Risk Off Stocks You'll Regret Missing This Month (2026-10-01)](https://www.benzinga.com/trading-ideas/long-ideas/26/10/62101807/top-3-risk-off-stocks-youll-regret-missing-this-month-2)

**Thesis**
- The stock's decline despite strong free cash flow margin may reflect concern that reported sales growth is driven by price increases while unit volume is falling.  
  > "Organic, constant currency net sales increased 3.6%, driven by net price realization of approximately 12 points. Volume declined approximately 8 points primarily reflecting elasticity impacts in North America Confectionery and International, partially offset by growth in North America Salty Snacks." ([HSY-8K-2026-07-30-ex99](https://www.sec.gov/Archives/edgar/data/47111/000162828026050769/exhibit991_2026xq2.htm))
- The company's core U.S. candy, mint and gum share declined due to increased competitive innovation, which may undercut investor confidence.  
  > "Hershey’s U.S. candy, mint and gum (CMG) retail takeaway for the 12-week period ended July 19, 20263 in the multi-outlet plus convenience store channels (MULO+ w/ Convenience) increased 3.7%. For this period, Hershey’s CMG share declined compared to the prior year due to increased competitive innovation." ([HSY-8K-2026-07-30-ex99](https://www.sec.gov/Archives/edgar/data/47111/000162828026050769/exhibit991_2026xq2.htm))
- Persistently higher manufacturing, logistics, and supply chain costs challenge the business and drive incremental costs, potentially limiting margin expansion.  
  > "Higher manufacturing, logistics, and supply chain costs continue to challenge the business and drive incremental costs" ([HSY-10Q-2026-07-30-mdna](https://www.sec.gov/Archives/edgar/data/47111/000162828026050900/hsy-20260628.htm))

**Bear case**
- North America Salty Snacks segment income decreased 5.9% as higher logistic costs and lower price realization more than offset higher volume, indicating profitability pressure in a growth segment.  
  > "North America Salty Snacks segment income was $62.6 million in the second quarter of 2026, a decrease of 5.9% versus the second quarter of 2025, driven by higher logistic costs, lower net price realization, increased consumer marketing investments, and unfavorable mix, which more than offset benefits from supply chain productivity and higher volume." ([HSY-8K-2026-07-30-ex99](https://www.sec.gov/Archives/edgar/data/47111/000162828026050769/exhibit991_2026xq2.htm))
- International segment loss widened by $24.9 million due to increased raw material and manufacturing costs, showing weakness in overseas markets.  
  > "International segment loss was $5.1 million in the second quarter of 2026, a decrease of $24.9 million versus the prior year period driven by increased raw material and manufacturing costs and higher advertising investment, partially offset by net price realization and supply chain productivity and transformation program savings." ([HSY-8K-2026-07-30-ex99](https://www.sec.gov/Archives/edgar/data/47111/000162828026050769/exhibit991_2026xq2.htm))
- A news report says Wells Fargo lowered its price target on Hershey to $170 while maintaining an Equal-Weight rating.  
  > "Wells Fargo Maintains Equal-Weight on Hershey, Lowers Price Target to $170" ([HSY-news-2026-10-05-62163018](https://www.benzinga.com/news/26/10/62163018/wells-fargo-maintains-equal-weight-hershey-lowers-price-target-170))

*model said evidence: sufficient*

### WING: not enough evidence

- source: [WING 8-K earnings release (Exhibit 99.1), filed 2026-07-29](https://www.sec.gov/Archives/edgar/data/1636222/000162828026050401/a991wingearningsreleasefin.htm)
- source: [WING 10-Q for period 2026-06-27, MD&A, filed 2026-07-29](https://www.sec.gov/Archives/edgar/data/1636222/000162828026050580/wing-20260627.htm)
- source: [Benzinga: What's Going On With Wingstop Stock On Wednesday? (2026-09-16)](https://www.benzinga.com/trading-ideas/movers/26/09/61810347/whats-going-on-with-wingstop-stock-on-wednesday)
- source: [Benzinga: RBC Capital Maintains Outperform on Wingstop, Lowers Price Target to $150 (2026-09-17)](https://www.benzinga.com/news/26/09/61841893/rbc-capital-maintains-outperform-wingstop-lowers-price-target-150)
- source: [Benzinga: TD Cowen Maintains Hold on Wingstop, Lowers Price Target to $120 (2026-09-11)](https://www.benzinga.com/news/26/09/61734137/td-cowen-maintains-hold-wingstop-lowers-price-target-120)

**Thesis**
- A news report says TD Cowen maintained a Hold rating and lowered its price target to $120, reflecting reduced analyst expectations.  
  > "TD Cowen Maintains Hold on Wingstop, Lowers Price Target to $120" ([WING-news-2026-09-11-61734137](https://www.benzinga.com/news/26/09/61734137/td-cowen-maintains-hold-wingstop-lowers-price-target-120))

**Bear case**
- The company attributed the same-store sales decline to lower transaction volumes and continued pressure on consumer spending.  
  > "partially offset by a decrease of $5.0 million due to a 7.5% decline in domestic same store sales contributed by lower transaction volumes, reflecting continued pressure on consumer spending." ([WING-8K-2026-07-29-ex99](https://www.sec.gov/Archives/edgar/data/1636222/000162828026050401/a991wingearningsreleasefin.htm))
- A news report says August dining traffic fell 2.4% nationwide, indicating a broader restaurant demand slowdown.  
  > "August dining traffic fell 2.4% nationwide, according to Placer.ai." ([WING-news-2026-09-16-61810347](https://www.benzinga.com/trading-ideas/movers/26/09/61810347/whats-going-on-with-wingstop-stock-on-wednesday))
- A news report says RBC Capital lowered its price target to $150, suggesting limited upside from prior expectations.  
  > "RBC Capital Maintains Outperform on Wingstop, Lowers Price Target to $150" ([WING-news-2026-09-17-61841893](https://www.benzinga.com/news/26/09/61841893/rbc-capital-maintains-outperform-wingstop-lowers-price-target-150))

*Stripped by the citation check (2):* "The company reported that domestic same store sales decreased 7.5% in the second" (claim states numbers not in its quote: ['2026']); "Management's 2026 guidance now projects a further decline of 4% to 6% in domesti" (claim states numbers not in its quote: ['2026'])

*model said evidence: sufficient*

### COCO: explained

- source: [COCO 8-K earnings release (Exhibit 99.1), filed 2026-07-23](https://www.sec.gov/Archives/edgar/data/1482981/000162828026049279/coco-20260630xexx991pressr.htm)
- source: [COCO 10-Q for period 2026-06-30, MD&A, filed 2026-07-23](https://www.sec.gov/Archives/edgar/data/1482981/000148298126000173/coco-20260630.htm)
- source: [Benzinga: Wells Fargo Maintains Overweight on The Vita Coco Co, Lowers Price Target to $65 (2026-10-05)](https://www.benzinga.com/news/26/10/62162704/wells-fargo-maintains-overweight-vita-coco-co-lowers-price-target-65)
- source: [Benzinga: This Toll Brothers Analyst Begins Coverage On A Bullish Note; Here Are Top 5 Initiations For Thursday (2026-10-01)](https://www.benzinga.com/analyst-stock-ratings/initiation/26/10/62113639/this-toll-brothers-analyst-begins-coverage-on-a-bullish-note-here-are-top-5-initiations-for-thursday)
- source: [Benzinga: Oppenheimer Initiates Coverage On The Vita Coco Co with Outperform Rating, Announces Price Target of $70 (2026-10-01)](https://www.benzinga.com/news/26/10/62099476/oppenheimer-initiates-coverage-vita-coco-co-outperform-rating-announces-price-target-70)
- source: [Benzinga: Piper Sandler Maintains Overweight on The Vita Coco Co, Lowers Price Target to $83 (2026-09-10)](https://www.benzinga.com/news/26/09/61719059/piper-sandler-maintains-overweight-vita-coco-co-lowers-price-target-83)

**Thesis**
- The screen's strong free cash flow margin may be distorted by one-time tariff refunds that boosted second-quarter earnings, causing investors to treat the print as not repeatable.  
  > "The refunds represent the recovery of tariffs paid in prior periods and provided a one-time benefit to our results during the quarter." ([COCO-10Q-2026-07-23-mdna](https://www.sec.gov/Archives/edgar/data/1482981/000148298126000173/coco-20260630.htm))
- The company's acquisition of Copra shortly after quarter-end involves a large cash outlay and potential future payments, which may have driven price weakness despite positive results.  
  > "The initial consideration for this transaction was $175.0 million, including $140.0 million in cash and $35.0 million paid in our Common Stock at the date of closing." ([COCO-10Q-2026-07-23-mdna](https://www.sec.gov/Archives/edgar/data/1482981/000148298126000173/coco-20260630.htm))
- Management's own guidance warning about geopolitical instability and tariff changes may explain why the market is cautious despite raised full-year guidance.  
  > "Uncertainty and instability in the current operating environment, geopolitical landscape, and global economies, including the military conflict in Iran and related impacts, changes in tariff rates, natural disasters, associated potential competitive pricing actions and our own price elasticity, could affect this outlook and our future results." ([COCO-8K-2026-07-23-ex99](https://www.sec.gov/Archives/edgar/data/1482981/000162828026049279/coco-20260630xexx991pressr.htm))

**Bear case**
- The company expects current cost pressures to temporarily reduce gross margin for the rest of the year, which could compress future profitability relative to the just-reported quarter.  
  > "While we still expect to see current cost pressures temporarily reduce gross margin for the balance of year, our strong underlying performance allows us to increase our investments in sales and marketing in the second half in order to maintain our momentum into 2027." ([COCO-8K-2026-07-23-ex99](https://www.sec.gov/Archives/edgar/data/1482981/000162828026049279/coco-20260630xexx991pressr.htm))
- The administration has announced its intent to impose additional tariffs under other statutory authorities, which could raise costs and pressure margins if implemented.  
  > "The administration has announced its intent to impose additional tariffs under other statutory authorities." ([COCO-10Q-2026-07-23-mdna](https://www.sec.gov/Archives/edgar/data/1482981/000148298126000173/coco-20260630.htm))
- The company's global supply chain is subject to geopolitical instability and volatility in costs, posing an ongoing operational risk.  
  > "Our global supply chain is subject to risks arising from geopolitical instability, including the ongoing military conflict involving Iran, as well as volatility in interest rates, foreign exchange rates, and our cost of goods including raw materials, factory costs, and transportation costs." ([COCO-10Q-2026-07-23-mdna](https://www.sec.gov/Archives/edgar/data/1482981/000148298126000173/coco-20260630.htm))

*model said evidence: sufficient*

### CELH: explained

- source: [CELH 8-K earnings release (Exhibit 99.1), filed 2026-08-06](https://www.sec.gov/Archives/edgar/data/1341766/000134176626000047/ex9912q2026.htm)
- source: [CELH 10-Q for period 2026-06-30, MD&A, filed 2026-08-06](https://www.sec.gov/Archives/edgar/data/1341766/000134176626000050/celh-20260630.htm)
- source: [Benzinga: Celsius Holdings Reports Q2 2026 Results: Full Earnings Call Transcript (2026-10-05)](https://www.benzinga.com/news/26/10/62157891/celsius-holdings-reports-q2-2026-results-full-earnings-call-transcript)
- source: [Benzinga: Celsius Stock Edges Lower: What's Happening? (2026-09-10)](https://www.benzinga.com/trading-ideas/movers/26/09/61715822/celsius-stock-edges-lower-whats-happening)

**Thesis**
- The flagship Celsius brand's revenue fell by approximately 11.7% year over year in the second quarter of 2026, indicating core-brand weakness that can explain the price decline despite positive free cash flow.  
  > "CELSIUS brand revenue decreased by approximately 11.7% in the second quarter of 2026 compared to the same period last year" ([CELH-8K-2026-08-06-ex99](https://www.sec.gov/Archives/edgar/data/1341766/000134176626000047/ex9912q2026.htm))
- Diluted EPS dropped to $0.14 from $0.33 in the prior-year period, showing reported profitability deteriorated sharply.  
  > "Diluted earnings per share for the second quarter of 2026 was $0.14 compared to $0.33 for the prior-year period." ([CELH-8K-2026-08-06-ex99](https://www.sec.gov/Archives/edgar/data/1341766/000134176626000047/ex9912q2026.htm))
- The company attributed the decline in net income attributable to common stockholders primarily to distributor termination fees and dividends on Series B Preferred Stock that was not outstanding in the prior-year period.  
  > "The decrease in net income attributable to common stockholders for the three months ended June 30, 2026 was primarily driven by distributor termination fees related to the termination of certain former Alani Nu distributors and by dividends on our Series B Preferred Stock, which was not outstanding in the prior year period." ([CELH-10Q-2026-08-06-mdna](https://www.sec.gov/Archives/edgar/data/1341766/000134176626000050/celh-20260630.htm))

**Bear case**
- The company's gross profit margin decreased because of higher promotional and incentive activity as a percentage of revenue and channel mix.  
  > "The decrease in gross profit margin was primarily driven by higher promotional and incentive activity as a percentage of revenue and channel mix." ([CELH-10Q-2026-08-06-mdna](https://www.sec.gov/Archives/edgar/data/1341766/000134176626000050/celh-20260630.htm))
- The Celsius brand's U.S. retail sales decreased 2% year over year and its dollar share was approximately 9.5%, suggesting the core brand is losing share in the energy category.  
  > "CELSIUS brand retail sales decreased 2% year over year for the 13-week period ended June 28, 2026,3 and the brand held an approximate 9.5% dollar share in the U.S. RTD energy category for the period." ([CELH-8K-2026-08-06-ex99](https://www.sec.gov/Archives/edgar/data/1341766/000134176626000047/ex9912q2026.htm))
- A news report says investors are weighing cautious commentary on core-brand volume pressure and margin headwinds, suggesting the market is focused on deteriorating fundamentals rather than free cash flow.  
  > "Celsius Holdings is trading lower Thursday as investors weigh cautious commentary on core-brand volume pressure and margin headwinds." ([CELH-news-2026-09-10-61715822](https://www.benzinga.com/trading-ideas/movers/26/09/61715822/celsius-stock-edges-lower-whats-happening))

*model said evidence: sufficient*

## Data limits

- Prices: Alpaca SIP daily bars, split and dividend adjusted; no intraday data used.
- Fundamentals: SEC XBRL companyfacts, US-GAAP filers only. Foreign private issuers (IFRS, 20-F/40-F) and companies without standard tags drop out as 'missing', they are not guessed.
- Market cap uses the latest cover-page share count; for multi-class issuers it can understate.
- Industry groups are SEC SIC codes, a coarse proxy for a theme (no GICS/BICS in free data).
- Short interest: FINRA consolidated short interest (twice monthly, non-commercial use); % is of shares outstanding, not float.
- Earnings-call transcripts are licensed content and were not used; explanations rely on the 8-K earnings release, 10-Q/10-K MD&A, and news headlines and summaries (Alpaca / Benzinga), never full articles.
- No consensus estimates, revisions, ownership or borrow-cost data: those need a licensed source.
